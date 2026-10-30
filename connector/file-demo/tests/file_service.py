"""Controlled API for local demonstrations and isolated file tests."""

import argparse
import asyncio
import hashlib
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from starlette.responses import JSONResponse, StreamingResponse


@dataclass
class Resource:
    data: bytes = b""
    file_name: str = "样例.bin"
    mime_type: str | None = None
    known: bool = True
    account_id: str = "account-1"
    fault: str | None = None
    path: Path | None = None

    @property
    def size(self):
        return self.path.stat().st_size if self.path is not None else len(self.data)

    def digest(self):
        if self.path is not None:
            with self.path.open("rb") as file:
                return hashlib.file_digest(file, "sha256").hexdigest()
        return hashlib.sha256(self.data).hexdigest()

    def chunks(self):
        if self.path is not None:
            with self.path.open("rb") as file:
                while chunk := file.read(65536):
                    yield chunk
        else:
            for start in range(0, len(self.data), 65536):
                yield self.data[start : start + 65536]


class FileService:
    def __init__(self, tokens, *, data_dir=None, permissions=None):
        self.tokens = dict(tokens)
        self.permissions = permissions or {}
        self.data_dir = data_dir
        self.resources = {
            "sample": Resource("通用文件示例\n".encode(), "样例.txt", "text/plain"),
            "empty": Resource(b"", "empty.bin"),
            "binary": Resource(bytes(range(256)) * 8192),
            "unknown": Resource(b"unknown-size\x00file", known=False),
        }
        self.calls = []
        self.started, self.released = asyncio.Event(), asyncio.Event()
        self.closed = 0
        self.produced = 0
        self.closed_files = {}
        self.upload_fault = None
        self.uploads = []
        self.upload_opened = self.upload_closed = self.upload_received = 0
        self.pending_uploads = set()

    def app(self, *, probe=False):
        app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

        def account(request, permission=None):
            auth = request.headers.get("authorization", "")
            owner = self.tokens.get(auth[7:]) if auth.startswith("Bearer ") else None
            if owner is None:
                raise HTTPException(401, "invalid_token")
            permissions = self.permissions.get(auth[7:], ["files.read", "files.write"])
            if permission is not None and permissions is not None and permission not in permissions:
                raise HTTPException(403, "permission_denied")
            return owner

        def resource(request, file_id):
            owner = account(request, "files.read")
            item = self.resources.get(file_id)
            if item is None or item.account_id != owner:
                raise HTTPException(404, "file_not_found")
            self.calls.append((owner, request.url.path, file_id))
            return item

        @app.get("/api/me")
        async def me(request: Request):
            return {
                "account_id": account(request),
                "tenant_id": None,
                "display_name": None,
                "permissions": self.permissions.get(
                    request.headers["authorization"][7:], ["files.read", "files.write"]
                ),
            }

        @app.post("/api/files")
        async def upload(request: Request, file_name: str, mime_type: str | None = None):
            owner = account(request, "files.write")

            def valid(value):
                return (
                    value
                    and value.strip()
                    and len(value) <= 255
                    and not any(
                        ord(c) < 32 or ord(c) == 127 or 0xD800 <= ord(c) <= 0xDFFF for c in value
                    )
                )

            if (
                not valid(file_name)
                or file_name in {".", ".."}
                or "/" in file_name
                or "\\" in file_name
                or (mime_type is not None and not valid(mime_type))
            ):
                raise HTTPException(400, "invalid_metadata")
            if self.data_dir is None:
                raise HTTPException(503, "upload_storage_unavailable")
            fault, self.upload_fault = self.upload_fault, None
            if fault == "reject":
                raise HTTPException(403, "permission_denied")
            file_id = uuid4().hex
            destination = self.data_dir / file_id
            fd, name = tempfile.mkstemp(prefix=".upload-", dir=self.data_dir)
            temporary = Path(name)
            self.pending_uploads.add(name)
            self.upload_opened += 1
            committed, size = False, 0
            try:
                with os.fdopen(fd, "wb") as target:
                    async for chunk in request.stream():
                        size += len(chunk)
                        self.upload_received += len(chunk)
                        if size > 100 * 1024 * 1024:
                            raise HTTPException(413, "file_too_large")
                        target.write(chunk)
                temporary.replace(destination)
                item = Resource(
                    file_name=file_name, mime_type=mime_type, account_id=owner, path=destination
                )
                self.resources[file_id] = item
                self.uploads.append(file_id)
                committed = True
                value = dict(
                    file_id=file_id, file_name=file_name, mime_type=mime_type, size_bytes=size
                )
                if fault == "lost":

                    async def lost():
                        yield b"{"
                        raise RuntimeError("controlled upload receipt interruption")

                    return StreamingResponse(lost(), status_code=201, media_type="application/json")
                if fault == "malformed":
                    value["size_bytes"] = True
                return JSONResponse(value, status_code=201)
            finally:
                self.upload_closed += 1
                self.pending_uploads.discard(name)
                temporary.unlink(missing_ok=True)
                if not committed:
                    destination.unlink(missing_ok=True)

        @app.get("/api/files/metadata")
        async def metadata(request: Request, file_id: str):
            item = resource(request, file_id)
            return {
                "file_id": "other" if item.fault == "metadata" else file_id,
                "file_name": item.file_name,
                "mime_type": item.mime_type,
                "size_bytes": 100 * 1024 * 1024 + 1
                if item.fault == "limit"
                else item.size
                if item.known
                else None,
            }

        @app.get("/api/files/content")
        async def content(request: Request, file_id: str):
            item = resource(request, file_id)

            async def chunks():
                self.started.set()
                try:
                    for chunk in item.chunks():
                        self.produced += len(chunk)
                        yield chunk
                        if item.fault == "truncated":
                            raise RuntimeError("controlled file interruption")
                        if item.fault == "slow":
                            await self.released.wait()
                finally:
                    self.closed += 1
                    self.closed_files[file_id] = self.closed_files.get(file_id, 0) + 1

            headers = {"Cache-Control": "no-store"}
            if item.known:
                headers["Content-Length"] = str(item.size)
            return StreamingResponse(
                chunks(), media_type="application/octet-stream", headers=headers
            )

        if probe:
            self.resources.update(
                {
                    "slow": Resource(b"s" * 200000, known=False, fault="slow"),
                    "truncated": Resource(b"t" * 200000, known=False, fault="truncated"),
                    "limit": Resource(b"x", fault="limit"),
                    "metadata": Resource(b"x", fault="metadata"),
                    "foreign": Resource(b"private", account_id="another-account"),
                }
            )

            @app.get("/probe/state")
            async def state(request: Request):
                owner = account(request)
                return {
                    "closed": self.closed,
                    "closed_files": self.closed_files,
                    "produced": self.produced,
                    "calls": self.calls,
                    "uploads": {
                        "opened": self.upload_opened,
                        "closed": self.upload_closed,
                        "received": self.upload_received,
                        "pending": len(self.pending_uploads),
                        "created": [
                            ident
                            for ident in self.uploads
                            if self.resources[ident].account_id == owner
                        ],
                    },
                    "files": {
                        name: {
                            "size": item.size,
                            "sha256": item.digest(),
                            "file_name": item.file_name,
                            "mime_type": item.mime_type,
                        }
                        for name, item in self.resources.items()
                        if item.account_id == owner
                    },
                }

            @app.post("/probe/release")
            async def release(request: Request):
                account(request)
                self.released.set()
                return {"released": True}

            @app.post("/probe/upload-fault")
            async def upload_fault(request: Request):
                account(request)
                value = await request.json()
                if value not in ("reject", "lost", "malformed", None):
                    raise HTTPException(400, "invalid_probe_fault")
                self.upload_fault = value
                return {"configured": True}

        return app


def main():
    import uvicorn

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--token-file", type=Path, required=True)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=24019)
    parser.add_argument(
        "--probe", action="store_true", help="Enable isolated test faults and counters"
    )
    args = parser.parse_args()
    token = args.token_file.read_text().strip()
    if not token or any(c.isspace() for c in token):
        parser.error("token file must contain a single nonempty token")
    args.data_dir.mkdir(mode=0o700, parents=True, exist_ok=False)
    uvicorn.run(
        FileService({token: "account-1"}, data_dir=args.data_dir).app(probe=args.probe),
        host=args.host,
        port=args.port,
        access_log=False,
    )


if __name__ == "__main__":
    main()
