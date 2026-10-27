import json
import os
import stat
from concurrent.futures import ThreadPoolExecutor

import pytest

from notion_connector.protocol import METADATA, ORIGIN, PROTECTED, RESOURCE
from notion_connector.registration import PreparationError, Transport, prepare


class Registration:
    def __init__(self):
        self.posts = 0
        self.fail = False
        self.metadata = {
            "issuer": ORIGIN, "authorization_endpoint": ORIGIN + "/authorize",
            "token_endpoint": ORIGIN + "/token", "registration_endpoint": ORIGIN + "/register",
            "revocation_endpoint": ORIGIN + "/token", "scopes_supported": ["default"],
            "code_challenge_methods_supported": ["S256"],
            "token_endpoint_auth_methods_supported": ["none"],
            "response_types_supported": ["code"],
            "grant_types_supported": ["authorization_code", "refresh_token"],
            "authorization_response_iss_parameter_supported": True,
        }

    def __call__(self, url, body=None):
        if url == PROTECTED:
            return {"resource": RESOURCE, "authorization_servers": [ORIGIN]}
        if url == METADATA:
            return self.metadata
        assert url == ORIGIN + "/register"
        self.posts += 1
        assert body["token_endpoint_auth_method"] == "none"
        if self.fail:
            raise PreparationError("response_lost")
        return {**body, "client_id": "registered-client", "client_id_issued_at": 1,
                "registration_access_token": "private-registration-token"}


@pytest.mark.parametrize("scheme", ["http", "https"])
def test_registration_exclusive_private_reused_without_network(tmp_path, scheme):
    vendor, path = Registration(), tmp_path / "registration.json"
    callback = f"{scheme}://backend.internal:23140/api/connector-oauth/callback"
    assert prepare(callback, path, transport=vendor) == {"client_id": "registered-client"}
    assert json.loads(path.read_text())["redirect_uri"] == callback
    assert path.stat().st_mode & 0o777 == 0o600
    assert "private-registration-token" not in path.read_text()
    assert prepare(callback, path, transport=lambda *_: pytest.fail("unexpected network")) == {
        "client_id": "registered-client"}
    assert vendor.posts == 1
    with pytest.raises(PreparationError):
        prepare("https://different.test/callback", path, transport=vendor)
    assert vendor.posts == 1


def test_lost_registration_response_is_persisted_unknown_and_never_retried(tmp_path):
    vendor, path = Registration(), tmp_path / "registration.json"
    vendor.fail = True
    for _ in range(2):
        with pytest.raises(PreparationError):
            prepare("https://backend.test/callback", path, transport=vendor)
    assert vendor.posts == 1
    assert json.loads(path.read_text())["status"] == "registration_unknown"


@pytest.mark.parametrize("key,value", [
    ("issuer", "https://other.test"), ("registration_endpoint", "https://other.test/register"),
    ("revocation_endpoint", ORIGIN + "/revoke"), ("code_challenge_methods_supported", ["plain"]),
    ("token_endpoint_auth_methods_supported", ["client_secret_basic"]),
    ("authorization_response_iss_parameter_supported", False),
])
def test_untrusted_or_changed_metadata_never_registers(tmp_path, key, value):
    vendor, path = Registration(), tmp_path / "registration.json"
    vendor.metadata[key] = value
    with pytest.raises(PreparationError):
        prepare("https://backend.test/callback", path, transport=vendor)
    assert not path.exists() and vendor.posts == 0


@pytest.mark.parametrize("callback", ["ftp://backend.test/cb", "https://x.test/cb?x=1",
                                      "https://u:p@x.test/cb", "https://x.test/cb#fragment",
                                      "http://x.test:0/cb", "http://x.test:65536/cb",
                                      "http://x.test:bad/cb", "http://x.test/cb?",
                                      "http://x.test/cb#"])
def test_invalid_callback_rejected_without_network(tmp_path, callback):
    with pytest.raises(PreparationError):
        prepare(callback, tmp_path / "registration.json",
                transport=lambda *_: pytest.fail("network"))


@pytest.mark.parametrize("variant", ["valid", "connection_close", "truncated", "redirect",
                                    "oversize", "late", "not_json"])
def test_transport_bounds_and_total_deadline(monkeypatch, variant):
    clock, requests, timeouts = [100.0], [], []
    closed = [False]
    monkeypatch.setattr("notion_connector.registration.time.monotonic", lambda: clock[0])

    class Response:
        status = 302 if variant == "redirect" else 200
        length = None

        def __enter__(self):
            self.chunks = iter([b"x" * 8192] * 9 if variant == "oversize" else [b'{"ok":true}'])
            return self

        def __exit__(self, *_):
            pass

        def getheader(self, *_):
            return "text/html" if variant == "not_json" else "application/json"

        def read1(self, size):
            clock[0] += 31 if variant == "late" else 0.1
            if variant in {"connection_close", "truncated"}:
                closed[0] = True
                self.length = 7 if variant == "truncated" else 0
            return next(self.chunks, b"")[:size]

        def isclosed(self):
            return closed[0]

    class Socket:
        def settimeout(self, value):
            if closed[0]:
                raise OSError("socket_closed_after_complete_body")
            timeouts.append(value)

    class Connection:
        closed = False

        def __init__(self, host, timeout):
            assert host == "mcp.notion.com" and timeout <= 30
            self.sock = Socket()

        def connect(self):
            clock[0] += 0.1

        def request(self, *args, **kwargs):
            requests.append(args)

        def getresponse(self):
            return Response()

        def close(self):
            Connection.closed = True

    monkeypatch.setattr("notion_connector.registration.http.client.HTTPSConnection", Connection)
    if variant in {"valid", "connection_close"}:
        assert Transport()(METADATA) == {"ok": True}
    else:
        with pytest.raises(PreparationError):
            Transport()(METADATA)
    assert Connection.closed and len(requests) == 1
    assert timeouts == sorted(timeouts, reverse=True)


def test_concurrent_preparation_sends_at_most_one_registration(tmp_path):
    vendor, path = Registration(), tmp_path / "registration.json"

    def attempt():
        try:
            return prepare("https://backend.test/callback", path, transport=vendor)
        except (PreparationError, OSError):
            return None

    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(lambda _: attempt(), range(4)))
    assert any(results) and vendor.posts == 1
    assert json.loads(path.read_text())["status"] == "registered"


def test_registration_reservation_directory_is_durable_before_post(tmp_path, monkeypatch):
    vendor, path = Registration(), tmp_path / "registration.json"
    synchronized = []
    fsync = os.fsync

    def sync(fd):
        if stat.S_ISDIR(os.fstat(fd).st_mode):
            synchronized.append(True)
        fsync(fd)

    def request(url, body=None):
        if body is not None:
            assert synchronized == [True]
        return vendor(url, body)

    monkeypatch.setattr("notion_connector.registration.os.fsync", sync)
    assert prepare("https://backend.test/callback", path, transport=request) == {
        "client_id": "registered-client"}
    assert vendor.posts == 1


def test_failed_directory_sync_never_registers_or_retries(tmp_path, monkeypatch):
    vendor, path = Registration(), tmp_path / "registration.json"
    fsync = os.fsync

    def sync(fd):
        if stat.S_ISDIR(os.fstat(fd).st_mode):
            raise OSError("directory_sync_failed")
        fsync(fd)

    monkeypatch.setattr("notion_connector.registration.os.fsync", sync)
    with pytest.raises(OSError, match="directory_sync_failed"):
        prepare("https://backend.test/callback", path, transport=vendor)
    with pytest.raises(PreparationError):
        prepare("https://backend.test/callback", path, transport=vendor)
    assert vendor.posts == 0
    assert json.loads(path.read_text())["status"] == "registration_unknown"
