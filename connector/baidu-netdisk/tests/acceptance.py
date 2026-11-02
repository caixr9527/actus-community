"""Independent installed-wheel TLS acceptance. Invoke with the consumer venv's python -I."""

import argparse
import asyncio
import datetime
import hashlib
import importlib.metadata
import ipaddress
import json
import os
import socket
import ssl
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from uuid import uuid4

import httpx
import jwt
from connector_sdk import FileInput, HttpOptions
from connector_sdk.client import ConnectorClient
from connector_sdk.packaging import validate_package
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

OPTIONS = HttpOptions(8, 4, 3, 5, 5, 3, 1024 * 1024, 1024 * 1024)
LIMIT = 100 * 1024 * 1024


def certificate(root):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "baidu-acceptance")])
    now = datetime.datetime.now(datetime.UTC)
    cert = (x509.CertificateBuilder().subject_name(name).issuer_name(name)
            .public_key(key.public_key()).serial_number(x509.random_serial_number())
            .not_valid_before(now - datetime.timedelta(days=1))
            .not_valid_after(now + datetime.timedelta(days=1))
            .add_extension(x509.SubjectAlternativeName([
                x509.IPAddress(ipaddress.ip_address("127.0.0.1"))]), False)
            .sign(key, hashes.SHA256()))
    private, public = root / "tls.key", root / "tls.crt"
    private.write_bytes(key.private_bytes(serialization.Encoding.PEM,
                        serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
    private.chmod(0o600)
    public.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    return private, public


class Installation:
    def __init__(self, package, root):
        root.mkdir(exist_ok=False)
        self.root = root
        _, self.manifest = validate_package(package)
        self.key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        (root / "gateway.pub").write_bytes(self.key.public_key().public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))
        key_file = root / "credentials.key"
        key_file.write_bytes(os.urandom(32))
        key_file.chmod(0o600)
        secret = root / "secrets.json"
        secret.write_text(json.dumps({"client-key": "test-secret"}))
        secret.chmod(0o600)
        private, public = certificate(root)
        self.ca = ssl.create_default_context(cafile=str(public))
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        self.url = f"https://127.0.0.1:{port}"
        self.installation_id = uuid4()
        settings = {
            "package_file": str(package), "values": {"client_id": "test-client"},
            "secrets_file": str(secret),
            "runtime": {"installation_id": str(self.installation_id),
                        "data_dir": str(root / "data"),
                        "credential_key_file": str(key_file),
                        "secret_bindings": {"client_secret": "client-key"},
                        "oauth_redirect_uri": "https://backend.test/api/connector-oauth/callback"},
            "platform": {"issuer": "baidu-acceptance", "audience": "sdk",
                         "public_key_file": str(root / "gateway.pub")},
            "runtime_options": {"max_concurrency": 8, "max_waiting": 8, "timeout_seconds": 30},
            "server_options": {"max_request_bytes": 1024 * 1024},
            "http_options": vars(OPTIONS),
            "listen": {"host": "127.0.0.1", "port": port, "scheme": "https",
                       "private_key_file": str(private), "certificate_file": str(public)}}
        self.settings = root / "settings.json"
        self.settings.write_text(json.dumps(settings))
        self.stats = root / "vendor-stats.json"
        self.processes = []

    def args(self, action, *, user="user-A", **scope):
        now = int(time.time())
        claims = {"iss": "baidu-acceptance", "aud": "sdk", "sub": user, "subject_kind": "user",
                  "iat": now, "exp": now + 60, "action": action,
                  "installation_id": str(self.installation_id), **scope}
        return {"token": jwt.encode(claims, self.key, algorithm="RS256"),
                "request_id": "independent-acceptance",
                "deadline": asyncio.get_running_loop().time() + 15}

    def invocation(self, cid, name, **kwargs):
        m = self.manifest
        return dict(connection_id=cid, app_version=m.version, catalog_revision=m.catalog_revision,
                    **self.args("operation.invoke", app_id=m.id, app_version=m.version,
                                catalog_revision=m.catalog_revision, operation_name=name,
                                connection_id=str(cid), **kwargs))

    def client(self):
        return ConnectorClient(base_url=self.url, installation_id=self.installation_id,
                               http_options=OPTIONS,
                               transport=httpx.AsyncHTTPTransport(verify=self.ca, trust_env=False))

    @contextmanager
    def running(self, label, *, mocked):
        if mocked:
            command = [sys.executable, "-I", "-B",
                       str(Path(__file__).with_name("serve_fixture.py")),
                       str(self.settings), str(self.stats)]
        else:
            command = [str(Path(sys.executable).with_name("connector")), "serve", "--entrypoint",
                       self.manifest.entrypoint, "--settings", str(self.settings)]
        with (self.root / f"{label}.stdout").open("w") as out, \
                (self.root / f"{label}.stderr").open("w") as err:
            process = subprocess.Popen(command, cwd=self.root, stdout=out, stderr=err)
            self.processes.append(process)
            try:
                with httpx.Client(verify=self.ca, trust_env=False, timeout=0.3) as browser:
                    end = time.monotonic() + 10
                    while time.monotonic() < end:
                        assert process.poll() is None, (self.root / f"{label}.stderr").read_text()
                        try:
                            if browser.get(self.url + "/v1/health").status_code == 200:
                                break
                        except httpx.HTTPError:
                            pass
                        time.sleep(0.02)
                    else:
                        raise AssertionError("isolated_service_not_ready")
                yield
            finally:
                if process.poll() is None:
                    process.terminate()
                try:
                    process.wait(timeout=45)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
                    raise
                assert process.returncode == 0, (self.root / f"{label}.stderr").read_text()


async def authorize(item):
    async with item.client() as sdk:
        begun = await sdk.begin_authorization(**item.args("authorization.create"))
        assert begun.status == "succeeded", begun
        view = begun.data
        values = {"state": parse_qs(urlsplit(view.authorization_url).query)["state"][0],
                  "code": "test-code"}
        blocked = await sdk.complete_authorization(view.transaction_id, values,
            **item.args("authorization.complete", user="user-B",
                        transaction_id=str(view.transaction_id)))
        assert blocked.status == "failed"
        result = await sdk.complete_authorization(view.transaction_id, values,
            **item.args("authorization.complete", transaction_id=str(view.transaction_id)))
        assert result.status == "succeeded" and result.data.status == "connected", result
        repeated = await sdk.complete_authorization(view.transaction_id, values,
            **item.args("authorization.complete", transaction_id=str(view.transaction_id)))
        assert repeated.data == result.data
        return result.data.connection.connection_id


async def execute(item, cid):
    async with item.client() as sdk:
        results = await asyncio.gather(*(sdk.invoke("get_quota", {},
            **item.invocation(cid, "get_quota")) for _ in range(4)))
        assert all(r.status == "succeeded" and r.data["free_bytes"] == 51 for r in results)
        cases = [
            ("list_files", {}), ("search_files", {"query": "测试"}),
            ("semantic_search", {"query": "发票"}), ("get_file_metadata", {"fs_id": "123"}),
            ("create_folder", {"path": "/new"}),
            ("copy_file", {"source_path": "/old", "destination_directory": "/new",
                           "new_name": "copy"}),
            ("move_file", {"source_path": "/old", "destination_directory": "/new",
                           "new_name": "moved"}),
            ("rename_file", {"path": "/old", "new_name": "renamed"}),
            ("delete_file", {"path": "/old"})]
        for name, params in cases:
            reply = await sdk.invoke(name, params, **item.invocation(cid, name))
            assert reply.status == "succeeded", (name, reply)
        denied = await sdk.invoke("get_quota", {},
                                  **item.invocation(cid, "get_quota", user="user-B"))
        assert denied.status == "failed"
        content = b"a" * (4 * 1024 * 1024) + b"b" * (4 * 1024 * 1024) + b"c"

        async def chunks():
            for offset in range(0, len(content), 65536):
                yield content[offset:offset + 65536]

        upload = await sdk.invoke_file_input("upload_file", {"destination_path": "/目标"},
            FileInput(file_name="上传.txt", content=chunks(), size_bytes=len(content)),
            max_file_bytes=LIMIT, **item.invocation(cid, "upload_file"))
        assert upload.status == "succeeded" and upload.data["external_resource_id"] == "125", upload

        async def consume(response):
            assert response.external_resource_id == "123" and response.file.file_name == "测试.txt"
            return b"".join([part async for part in response.file.content])

        download = await sdk.invoke_file_output("download_file", {"fs_id": "123"},
            consume=consume, max_file_bytes=LIMIT, **item.invocation(cid, "download_file"))
        assert download.status == "succeeded" and download.data == b"abc", download


async def disconnect(item, cid):
    async with item.client() as sdk:
        live = await sdk.get_connection(cid, **item.args("connection.read", connection_id=str(cid)))
        assert live.status == "succeeded" and live.data.revision > 1
        closed = await sdk.disconnect(cid, expected_revision=live.data.revision,
            **item.args("connection.disconnect", connection_id=str(cid)))
        assert closed.data.status == "disconnected"
        assert closed.data.revocation.status == "not_attempted"
        assert (await sdk.invoke("get_quota", {},
            **item.invocation(cid, "get_quota"))).status == "failed"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    import connector_sdk

    import baidu_netdisk

    origins = [baidu_netdisk.__file__, connector_sdk.__file__]
    assert all(str(Path(sys.prefix)) in p and "site-packages" in p for p in origins)
    assert importlib.metadata.version("actus-connector-sdk") == "0.0.1b9"
    item = Installation(args.package.resolve(), args.output.resolve())
    with item.running("normal-cli", mocked=False):
        pass  # Real unmodified CLI, package verification, startup and TLS health.
    with item.running("authorization", mocked=True):
        cid = asyncio.run(authorize(item))
    time.sleep(1.05)
    with item.running("operations", mocked=True):
        asyncio.run(execute(item, cid))
    with item.running("persisted-refresh", mocked=True):
        asyncio.run(disconnect(item, cid))
    stats = json.loads(item.stats.read_text())
    assert stats["grants"] == ["authorization_code", "refresh_token"]
    assert stats["parts"] == [1] and len(stats["merge_hashes"]) == 3
    assert all(process.poll() == 0 for process in item.processes)
    for path in item.root.glob("*.std*"):
        log = path.read_text()
        assert all(secret not in log for secret in ("test-secret", "test-code", "access-1",
                                                    "access-2", "refresh-1", "refresh-2"))
    for path in (item.root / "data").rglob("*"):
        if path.is_file():
            assert all(secret not in path.read_bytes() for secret in
                       (b"access-1", b"refresh-1", b"access-2", b"refresh-2"))
    report = {"application": "baidu-netdisk", "version": item.manifest.version,
              "sdk": "0.0.1b9",
              "package_sha256": hashlib.sha256(args.package.read_bytes()).hexdigest(),
              "module_origins": origins, "operations": 12, "tls": True,
              "vendor": "deterministic HTTPX boundary substitute; no real Baidu account",
              "source_required": False, "refreshes": 1, "partial_upload_part_indexes": [1],
              "full_merge_hash_count": 3, "process_exit_codes": [p.poll() for p in item.processes]}
    (item.root / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
