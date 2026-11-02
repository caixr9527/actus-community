"""Deterministic vendor boundary. Only public HTTPX transports are substituted in tests."""

import hashlib
import json
from email import policy
from email.parser import BytesParser
from urllib.parse import parse_qs

import httpx

PART = 4 * 1024 * 1024


class Stream(httpx.AsyncByteStream):
    def __init__(self, chunks):
        self.chunks, self.closed = chunks, 0

    async def __aiter__(self):
        for chunk in self.chunks:
            yield chunk

    async def aclose(self):
        self.closed += 1


class Vendor:
    def __init__(self):
        self.calls, self.tokens, self.parts, self.creates, self.streams = [], [], [], [], []
        self.generation, self.expires, self.refresh_fail = 0, 3600, False
        self.missing, self.rapid, self.inject, self.token_change = None, False, None, {}
        self.content = b"abc"
        self.pending = {}

    def file(self):
        return {"fs_id": 123, "server_filename": "测试.txt", "path": "/测试.txt",
                "size": len(self.content), "isdir": 0, "category": 4,
                "dlink": "https://pan.baidu.com/file/download?sign=vendor-signature",
                "access_token": "must-not-be-returned"}

    async def __call__(self, request):
        self.calls.append(request)
        query = dict(request.url.params)
        if self.inject:
            injected = await self.inject(request)
            if injected is not None:
                return injected
        if request.url.host == "openapi.baidu.com":
            assert request.url.path == "/oauth/2.0/token" and request.method == "GET"
            assert not request.content and "authorization" not in request.headers
            assert query["client_id"] == "test-client" and query["client_secret"] == "test-secret"
            self.tokens.append(query)
            if query["grant_type"] == "refresh_token":
                assert query["refresh_token"] == f"refresh-{self.generation}"
                if self.refresh_fail:
                    return httpx.Response(400, json={"error": "invalid_grant"})
            else:
                assert query["code"] == "test-code" and "code_verifier" not in query
                assert query["redirect_uri"] == "https://backend.test/api/connector-oauth/callback"
            self.generation += 1
            return httpx.Response(200, json={"access_token": f"access-{self.generation}",
                                           "refresh_token": f"refresh-{self.generation}",
                                           "scope": "basic,netdisk", "expires_in": self.expires,
                                           **self.token_change})
        assert request.url.scheme == "https"
        if request.url.path == "/file/download":
            assert request.url.host == "pan.baidu.com"
            assert query["access_token"] == f"access-{self.generation}"
            return httpx.Response(302, headers={
                "location": "https://cdn.baidupcs.com/content?sign=vendor-signature"})
        if request.url.host == "cdn.baidupcs.com":
            assert "access_token" not in query and "authorization" not in request.headers
            stream = Stream([self.content[:1], self.content[1:]])
            self.streams.append(stream)
            return httpx.Response(200, stream=stream,
                                  headers={"content-length": str(len(self.content))})
        assert query["access_token"] == f"access-{self.generation}"
        assert "authorization" not in request.headers
        if request.url.path == "/rest/2.0/pcs/superfile2":
            assert request.url.host == "d.pcs.baidu.com" and request.method == "POST"
            message = BytesParser(policy=policy.default).parsebytes(
                b"Content-Type: " + request.headers["content-type"].encode() + b"\r\n\r\n"
                + request.content)
            part = list(message.iter_parts())[0].get_payload(decode=True)
            self.parts.append((int(query["partseq"]), part))
            return httpx.Response(200, json={"md5": hashlib.md5(part).hexdigest()})
        assert request.url.host == "pan.baidu.com"
        method = query.get("method")
        if method == "uinfo":
            return httpx.Response(200, json={"errno": 0, "uk": 456, "netdisk_name": "测试账号"})
        if method in ("list", "search", "filemetas"):
            return httpx.Response(200, json={"errno": 0, "list": [self.file()], "has_more": 0})
        if request.url.path == "/api/quota":
            return httpx.Response(200, json={"errno": 0, "total": 100, "used": 40,
                                           "free": 51, "expire": 0})
        if request.url.path == "/xpan/unisearch":
            assert request.method == "POST" and json.loads(request.content) == {}
            assert json.loads(query["dirs"]) == [{"uk": 456, "path": "/"}]
            return httpx.Response(200, json={"errno": 0, "data": [{"list": [self.file()]}],
                                           "is_end": True})
        form = {k: v[0] for k, v in parse_qs(request.content.decode()).items()}
        if method == "precreate":
            self.pending = form
            hashes = json.loads(form["block_list"])
            if self.rapid:
                return httpx.Response(200, json={"errno": 0, "return_type": 2})
            missing = list(range(len(hashes))) if self.missing is None else self.missing
            return httpx.Response(200, json={"errno": 0, "return_type": 1,
                                           "uploadid": "upload-1", "block_list": missing})
        if method == "create":
            self.creates.append(form)
            if form["isdir"] == "1":
                return httpx.Response(200, json={"errno": 0, "fs_id": 124, "isdir": 1,
                                               "path": form["path"]})
            assert form["block_list"] == self.pending["block_list"]
            return httpx.Response(200, json={"errno": 0, "fs_id": 125, "path": form["path"],
                                           "size": int(form["size"])})
        if method == "filemanager":
            assert form["async"] == "0"
            items = json.loads(form["filelist"])
            return httpx.Response(200, json={"errno": 0, "info": [{"errno": 0,
                                           "path": items[0] if type(items[0]) is str
                                           else items[0]["path"]}]})
        raise AssertionError("unexpected_vendor_request")
