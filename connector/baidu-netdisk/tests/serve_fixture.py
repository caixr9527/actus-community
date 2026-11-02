"""Run the installed public CLI with an HTTPX vendor substitute; never ship this fixture."""

import importlib.util
import json
import sys
from pathlib import Path

import httpx


def main():
    settings, stats_file = map(Path, sys.argv[1:])
    spec = importlib.util.spec_from_file_location("vendor_fixture",
                                                 Path(__file__).with_name("vendor.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    vendor = module.Vendor()
    stats = json.loads(stats_file.read_text()) if stats_file.exists() else {
        "generation": 0, "requests": [], "grants": [], "parts": [], "merge_hashes": []}
    vendor.generation = stats["generation"]
    vendor.expires = 1
    vendor.missing = [1]

    async def respond(request):
        if request.url.params.get("grant_type") == "refresh_token":
            vendor.expires = 3600
        response = await vendor(request)
        stats["generation"] = vendor.generation
        stats["requests"].append({"host": request.url.host, "path": request.url.path,
                                  "method": request.method})
        grant = request.url.params.get("grant_type")
        if grant:
            stats["grants"].append(grant)
        if vendor.parts:
            stats["parts"] = [i for i, _ in vendor.parts]
        if vendor.creates and "block_list" in vendor.creates[-1]:
            stats["merge_hashes"] = json.loads(vendor.creates[-1]["block_list"])
        stats_file.write_text(json.dumps(stats))
        return response

    # Public third-party network seam only. No SDK symbols, app code or settings are patched.
    httpx.AsyncHTTPTransport = lambda **_: httpx.MockTransport(respond)
    from connector_sdk.cli import main as cli

    raise SystemExit(cli(["serve", "--entrypoint", "baidu_netdisk.app:App",
                          "--settings", str(settings)]))


if __name__ == "__main__":
    main()
