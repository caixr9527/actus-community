"""Controlled API for local demonstrations and isolated file tests."""

import argparse
import asyncio
import hashlib
from dataclasses import dataclass
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from starlette.responses import StreamingResponse


@dataclass
class Resource:
    data: bytes
    file_name: str = "样例.bin"
    mime_type: str | None = None
    known: bool = True
    account_id: str = "account-1"
    fault: str | None = None


class FileService:
    def __init__(self, tokens):
        self.tokens = dict(tokens)
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

    def app(self, *, probe=False):
        app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

        def account(request):
            auth = request.headers.get("authorization", "")
            owner = self.tokens.get(auth[7:]) if auth.startswith("Bearer ") else None
            if owner is None:
                raise HTTPException(401, "invalid_token")
            return owner

        def resource(request, file_id):
            owner = account(request)
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
                "permissions": ["files.read"],
            }

        @app.get("/api/files/metadata")
        async def metadata(request: Request, file_id: str):
            item = resource(request, file_id)
            return {
                "file_id": "other" if item.fault == "metadata" else file_id,
                "file_name": item.file_name,
                "mime_type": item.mime_type,
                "size_bytes": 100 * 1024 * 1024 + 1
                if item.fault == "limit"
                else len(item.data)
                if item.known
                else None,
            }

        @app.get("/api/files/content")
        async def content(request: Request, file_id: str):
            item = resource(request, file_id)

            async def chunks():
                self.started.set()
                try:
                    for start in range(0, len(item.data), 65536):
                        chunk = item.data[start : start + 65536]
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
                headers["Content-Length"] = str(len(item.data))
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
                    "files": {
                        name: {
                            "size": len(item.data),
                            "sha256": hashlib.sha256(item.data).hexdigest(),
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

        return app


def main():
    import uvicorn

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--token-file", type=Path, required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=24019)
    parser.add_argument(
        "--probe", action="store_true", help="Enable isolated test faults and counters"
    )
    args = parser.parse_args()
    token = args.token_file.read_text().strip()
    if not token or any(c.isspace() for c in token):
        parser.error("token file must contain a single nonempty token")
    uvicorn.run(
        FileService({token: "account-1"}).app(probe=args.probe),
        host=args.host,
        port=args.port,
        access_log=False,
    )


if __name__ == "__main__":
    main()
