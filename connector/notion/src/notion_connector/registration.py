"""Explicit administrator preparation, never imported by the application entrypoint."""

import argparse
import http.client
import json
import os
import time
from pathlib import Path
from urllib.parse import urlsplit

from .protocol import CLIENT_NAME, METADATA, ORIGIN, PROTECTED, RESOURCE

LIMIT = 64 * 1024


class PreparationError(Exception):
    pass


class Transport:
    """Fixed-origin HTTPS, bounded response, one deadline and no retries or redirects."""

    def __init__(self):
        self.deadline = time.monotonic() + 30

    def remaining(self):
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise PreparationError("preparation_timeout")
        return remaining

    def __call__(self, url, body=None):
        if urlsplit(url).netloc != "mcp.notion.com" or not url.startswith(ORIGIN + "/"):
            raise PreparationError("untrusted_endpoint")
        payload = None if body is None else json.dumps(body).encode()
        connection = http.client.HTTPSConnection("mcp.notion.com", timeout=self.remaining())
        try:
            connection.connect()
            sock = connection.sock
            sock.settimeout(self.remaining())
            connection.request("GET" if body is None else "POST", urlsplit(url).path,
                               body=payload, headers={"Accept": "application/json",
                                                      "Content-Type": "application/json"})
            sock.settimeout(self.remaining())
            with connection.getresponse() as response:
                if response.status not in {200, 201}:
                    raise PreparationError("preparation_request_failed")
                content_type = response.getheader("Content-Type", "").split(";")[0].strip()
                if content_type != "application/json":
                    raise PreparationError("metadata_not_json")
                chunks, size = [], 0
                while True:
                    if response.isclosed():
                        if response.length not in (None, 0):
                            raise PreparationError("metadata_incomplete")
                        break
                    sock.settimeout(self.remaining())
                    chunk = response.read1(min(8192, LIMIT + 1 - size))
                    if not chunk:
                        if response.length not in (None, 0):
                            raise PreparationError("metadata_incomplete")
                        break
                    size += len(chunk)
                    if size > LIMIT:
                        raise PreparationError("metadata_too_large")
                    chunks.append(chunk)
                raw = b"".join(chunks)
            self.remaining()
            value = json.loads(raw)
            if not isinstance(value, dict):
                raise ValueError
            return value
        except (OSError, ValueError, http.client.HTTPException):
            raise PreparationError("preparation_request_failed") from None
        finally:
            connection.close()


def redirect_uri(value):
    try:
        url = urlsplit(value)
        valid = (url.scheme == "https" and url.hostname and url.username is None
                 and url.password is None and not url.query and not url.fragment
                 and url.path and "\\" not in value
                 and all(ord(c) > 32 and ord(c) != 127 for c in value))
        _ = url.port
    except ValueError:
        valid = False
    if not valid:
        raise PreparationError("invalid_redirect_uri")
    return value


def client(value):
    if (not isinstance(value, str) or not value or len(value) > 4096
            or any(c.isspace() or ord(c) < 33 or ord(c) == 127 for c in value)):
        raise PreparationError("invalid_registration")
    return value


def prepare(callback, output, *, transport=None):
    callback, output = redirect_uri(callback), Path(output)
    if output.exists() or output.is_symlink():
        try:
            if output.is_symlink() or not output.is_file() or output.stat().st_mode & 0o077:
                raise PreparationError("registration_file_permissions")
            if output.stat().st_size > LIMIT:
                raise PreparationError("invalid_registration_file")
            record = json.loads(output.read_text())
            if (record["status"] != "registered" or record["redirect_uri"] != callback
                    or record["issuer"] != ORIGIN):
                raise PreparationError("registration_requires_manual_review")
            return {"client_id": client(record["client_id"])}
        except (OSError, ValueError, KeyError, TypeError):
            raise PreparationError("invalid_registration_file") from None
    request = transport or Transport()
    resource, metadata = request(PROTECTED), request(METADATA)
    if (resource.get("resource") != RESOURCE
            or resource.get("authorization_servers") != [ORIGIN]):
        raise PreparationError("untrusted_resource_metadata")
    expected = {"issuer": ORIGIN, "authorization_endpoint": ORIGIN + "/authorize",
                "token_endpoint": ORIGIN + "/token", "registration_endpoint": ORIGIN + "/register",
                "revocation_endpoint": ORIGIN + "/token"}
    if any(metadata.get(k) != v for k, v in expected.items()):
        raise PreparationError("oauth_metadata_changed")
    for key, required in {"code_challenge_methods_supported": "S256",
                          "token_endpoint_auth_methods_supported": "none",
                          "scopes_supported": "default",
                          "response_types_supported": "code",
                          "grant_types_supported": "refresh_token"}.items():
        if not isinstance(metadata.get(key), list) or required not in metadata[key]:
            raise PreparationError("oauth_metadata_incompatible")
    if metadata.get("authorization_response_iss_parameter_supported") is not True:
        raise PreparationError("oauth_issuer_not_supported")
    if "authorization_code" not in metadata["grant_types_supported"]:
        raise PreparationError("oauth_metadata_incompatible")
    registration = {"client_name": CLIENT_NAME, "redirect_uris": [callback],
                    "token_endpoint_auth_method": "none", "scope": "default",
                    "grant_types": ["authorization_code", "refresh_token"],
                    "response_types": ["code"]}
    record = {"status": "registration_unknown", "issuer": ORIGIN, "redirect_uri": callback,
              "registration_endpoint": expected["registration_endpoint"],
              "requested_at": int(time.time())}
    # Reserve before the non-idempotent POST. A lost response must not cause re-registration.
    fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as target:
        target.write(json.dumps(record) + "\n")
        target.flush()
        os.fsync(target.fileno())
        directory = os.open(output.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
        result = request(expected["registration_endpoint"], registration)
        identifier = client(result.get("client_id"))
        if (result.get("token_endpoint_auth_method") != "none"
                or result.get("redirect_uris") != [callback]
                or result.get("client_secret")):
            raise PreparationError("invalid_registration")
        issued = result.get("client_id_issued_at")
        if issued is not None and (type(issued) is not int or issued < 0):
            raise PreparationError("invalid_registration")
        record.update(status="registered", client_id=identifier,
                      client_id_issued_at=issued)
        target.seek(0)
        target.truncate()
        target.write(json.dumps(record) + "\n")
        target.flush()
        os.fsync(target.fileno())
    return {"client_id": identifier}


def main():
    parser = argparse.ArgumentParser(description="Prepare one reusable public Notion OAuth client")
    parser.add_argument("--redirect-uri", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        values = prepare(args.redirect_uri, args.output)
    except (PreparationError, OSError):
        parser.exit(1, "Preparation failed; inspect local registration status before retry.\n")
    print(json.dumps({"values": values}))


if __name__ == "__main__":
    main()
