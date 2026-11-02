"""Run with the independent consumer interpreter: python -I acceptance.py PACKAGE NEW_OUTPUT."""

import datetime
import importlib.metadata
import ipaddress
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from uuid import uuid4

import connector_sdk
import httpx
from connector_sdk import HttpOptions
from connector_sdk.packaging import validate_package
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

import dingtalk_connector


def main():
    package, root = (Path(p).resolve() for p in sys.argv[1:])
    root.mkdir(exist_ok=False)
    _, manifest = validate_package(package)
    assert manifest.id == "dingtalk" and len(manifest.operations) == 5
    assert importlib.metadata.version("actus-connector-sdk") == "0.0.1b9"
    for module in (connector_sdk, dingtalk_connector):
        assert "site-packages" in Path(module.__file__).parts, module.__file__

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private = key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
    )
    private_file, cert_file, public_file = root / "tls.key", root / "tls.crt", root / "platform.pub"
    private_file.write_bytes(private)
    private_file.chmod(0o600)
    public_file.write_bytes(
        key.public_key().public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
        )
    )
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "dingtalk-acceptance")])
    now = datetime.datetime.now(datetime.UTC)
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=1))
        .not_valid_after(now + datetime.timedelta(days=1))
        .add_extension(
            x509.SubjectAlternativeName([x509.IPAddress(ipaddress.ip_address("127.0.0.1"))]), False
        )
        .sign(key, hashes.SHA256())
    )
    cert_file.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    credential_key = root / "credentials.key"
    credential_key.write_bytes(os.urandom(32))
    credential_key.chmod(0o600)
    secrets_file = root / "secrets.json"
    secrets_file.write_text(json.dumps({"client-secret": "isolated-smoke-secret"}))
    secrets_file.chmod(0o600)
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    settings = {
        "package_file": str(package),
        "values": {"client_id": "ding.smoke"},
        "secrets_file": str(secrets_file),
        "runtime": {
            "installation_id": str(uuid4()),
            "data_dir": str(root / "data"),
            "credential_key_file": str(credential_key),
            "secret_bindings": {"client_secret": "client-secret"},
            "oauth_redirect_uri": "https://backend.test/api/connector-oauth/callback",
        },
        "platform": {
            "issuer": "dingtalk-acceptance",
            "audience": "sdk",
            "public_key_file": str(public_file),
        },
        "runtime_options": {"max_concurrency": 4, "max_waiting": 4, "timeout_seconds": 30},
        "server_options": {"max_request_bytes": 1024 * 1024},
        "http_options": vars(HttpOptions(8, 4, 3, 5, 5, 3, 1024 * 1024, 1024 * 1024)),
        "listen": {
            "host": "127.0.0.1",
            "port": port,
            "scheme": "https",
            "private_key_file": str(private_file),
            "certificate_file": str(cert_file),
        },
    }
    settings_file = root / "settings.json"
    settings_file.write_text(json.dumps(settings))
    args = [
        str(Path(sys.executable).with_name("connector")),
        "serve",
        "--entrypoint",
        "dingtalk_connector.app:App",
        "--settings",
        str(settings_file),
    ]
    with (root / "stdout.log").open("w") as out, (root / "stderr.log").open("w") as err:
        process = subprocess.Popen(args, cwd=root, stdout=out, stderr=err)
        try:
            import ssl

            tls = ssl.create_default_context(cafile=str(cert_file))
            with httpx.Client(verify=tls, trust_env=False, timeout=0.5) as client:
                end = time.monotonic() + 15
                while time.monotonic() < end:
                    assert process.poll() is None, "connector_serve_exited"
                    try:
                        response = client.get(f"https://127.0.0.1:{port}/v1/health")
                        if response.status_code == 200:
                            break
                    except httpx.HTTPError:
                        pass
                    time.sleep(0.05)
                else:
                    raise AssertionError("connector_serve_not_ready")
        finally:
            process.terminate()
            try:
                process.wait(timeout=20)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
                raise
        assert process.returncode == 0, "connector_serve_shutdown_failed"
    logs = (root / "stdout.log").read_text() + (root / "stderr.log").read_text()
    assert "isolated-smoke-secret" not in logs
    print(
        json.dumps(
            {
                "application": manifest.id,
                "version": manifest.version,
                "operations": len(manifest.operations),
                "tls_health": "passed",
                "shutdown": "passed",
                "app_module": dingtalk_connector.__file__,
                "sdk_module": connector_sdk.__file__,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
