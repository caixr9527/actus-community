import asyncio
import json

import httpx
import pytest
from vendor import ROOT, response

REPO = {"owner": "octo", "repo": "demo"}
ISSUE = REPO | {"issue_number": 7}
PULL = REPO | {"pull_number": 8}
CASES = [
    ("list_installations", {}, "GET", "/user/installations"),
    ("list_repositories", {"installation_id": 1}, "GET", "/user/installations/1/repositories"),
    ("get_repository", REPO, "GET", ROOT),
    ("list_issues", REPO, "GET", ROOT + "/issues"),
    ("get_issue", ISSUE, "GET", ROOT + "/issues/7"),
    ("create_issue", REPO | {"title": "New", "labels": ["bug"]}, "POST", ROOT + "/issues"),
    ("update_issue", ISSUE | {"body": "new", "labels": []}, "PATCH", ROOT + "/issues/7"),
    ("list_issue_comments", ISSUE, "GET", ROOT + "/issues/7/comments"),
    ("create_issue_comment", ISSUE | {"body": "hello"}, "POST", ROOT + "/issues/7/comments"),
    ("list_labels", REPO, "GET", ROOT + "/labels"),
    ("list_pull_requests", REPO, "GET", ROOT + "/pulls"),
    ("get_pull_request", PULL, "GET", ROOT + "/pulls/8"),
    ("list_pull_request_files", PULL, "GET", ROOT + "/pulls/8/files"),
]


@pytest.mark.parametrize("name,params,method,path", CASES)
async def test_thirteen_static_wire_operations(case, name, params, method, path):
    connection = await case.connect()
    reply = await case.invoke(connection, name, params)
    assert reply.status == "succeeded", reply
    assert any(r.method == method and r.url.path == path for r in case.vendor.calls)
    if name == "update_issue":
        assert case.vendor.writes == [{"body": "new", "labels": []}]


@pytest.mark.parametrize(
    "name,params",
    [
        ("get_repository", REPO | {"owner": "../x"}),
        ("get_repository", REPO | {"repo": ".."}),
        ("get_repository", REPO | {"repo": "https://evil"}),
        ("get_issue", ISSUE | {"issue_number": True}),
        ("list_issues", REPO | {"page": 0}),
        ("list_issues", REPO | {"since": "2026-99-99T00:00:00Z"}),
        ("list_issues", REPO | {"labels": ["a,b"]}),
        ("update_issue", ISSUE),
        ("update_issue", ISSUE | {"body": None}),
        ("update_issue", ISSUE | {"state_reason": "completed"}),
        ("update_issue", ISSUE | {"labels": ["bug", "bug"]}),
        ("create_issue", REPO | {"title": "  "}),
        ("create_issue", REPO | {"title": "x", "labels": None}),
        ("create_issue_comment", ISSUE | {"body": "  "}),
        ("get_pull_request", PULL | {"url": "https://evil"}),
    ],
)
async def test_invalid_inputs_do_not_reach_vendor(case, name, params):
    connection = await case.connect()
    before = len(case.vendor.calls)
    assert (await case.invoke(connection, name, params)).status == "failed"
    assert len(case.vendor.calls) == before


@pytest.mark.parametrize(
    "name,params",
    [
        ("get_issue", {}),
        ("update_issue", {"body": "x"}),
        ("list_issue_comments", {}),
        ("create_issue_comment", {"body": "x"}),
    ],
)
async def test_pr_cannot_be_mutated_through_issue_routes(case, name, params):
    connection = await case.connect()
    reply = await case.invoke(connection, name, REPO | {"issue_number": 8} | params)
    assert reply.status == "failed" and not case.vendor.writes
    assert all(r.method == "GET" for r in case.vendor.calls if r.url.host == "api.github.com")


async def test_filtered_pr_page_preserves_link_progress(case):
    connection = await case.connect()

    async def inject(request):
        if request.url.path == ROOT + "/issues":
            return response(
                [case.vendor.issue | {"pull_request": {}}],
                headers={
                    "Link": "<https://api.github.com/repositories/10/issues?"
                    'page=2&per_page=30>; rel="next"'
                },
            )

    case.vendor.inject = inject
    reply = await case.invoke(connection, "list_issues", REPO)
    assert reply.status == "succeeded", reply
    assert reply.data["data"]["items"] == [] and reply.data["data"]["next_page"] == 2


@pytest.mark.parametrize(
    "link",
    [
        '<https://evil.test/issues?page=2>; rel="next"',
        '<https://api.github.com/user?page=2>; rel="next"',
        '<https://api.github.com/repos/octo/demo/labels?page=1>; rel="next"',
        '<https://api.github.com/repos/octo/demo/labels?page=2&page=3>; rel="next"',
        '<https://api.github.com/repos/octo/demo/labels?page=2&per_page=1>; rel="next"',
        "broken",
    ],
)
async def test_bad_links_fail_without_following_them(case, link):
    connection = await case.connect()

    async def inject(request):
        if request.url.path == ROOT + "/labels":
            return response([], headers={"link": link})

    case.vendor.inject = inject
    before = len(case.vendor.calls)
    assert (await case.invoke(connection, "list_labels", REPO)).status == "failed"
    assert len(case.vendor.calls) == before + 1


async def test_same_origin_canonical_read_redirect(case):
    connection = await case.connect()

    async def inject(request):
        if request.url.path == ROOT:
            return httpx.Response(
                301, headers={"location": "https://api.github.com/repositories/10"}
            )

    case.vendor.inject = inject
    assert (await case.invoke(connection, "get_repository", REPO)).status == "succeeded"


@pytest.mark.parametrize(
    "target",
    [
        "https://evil.test/repositories/10",
        "http://api.github.com/repositories/10",
        "https://api.github.com/user",
        "https://api.github.com/repos/a/b/../x",
        "https://api.github.com/repos/a/b%2fx",
    ],
)
async def test_unsafe_read_redirect_rejected(case, target):
    connection = await case.connect()

    async def inject(request):
        if request.url.path == ROOT:
            return httpx.Response(301, headers={"location": target})

    case.vendor.inject = inject
    before = len(case.vendor.calls)
    assert (await case.invoke(connection, "get_repository", REPO)).status == "failed"
    # SDK rejects 3xx without exposing Location. The adapter replays only the original GET.
    assert len(case.vendor.calls) == before + 2
    assert all(
        r.url.host == "api.github.com" and r.url.path == ROOT for r in case.vendor.calls[before:]
    )


@pytest.mark.parametrize("mode", ["lost", "bad", "http", "redirect", "ignored_labels"])
async def test_sent_write_remains_uncertain_and_never_retries(case, mode):
    connection = await case.connect()
    sent = []

    async def inject(request):
        if request.url.path == ROOT + "/issues" and request.method == "POST":
            sent.append(request)
            if mode == "lost":
                raise httpx.ReadError("private")
            if mode == "bad":
                return response({})
            if mode == "http":
                return response({"message": "private"}, 503)
            if mode == "redirect":
                return httpx.Response(
                    307, headers={"location": "https://api.github.com/repositories/10/issues"}
                )
            return response(case.vendor.issue | {"labels": []}, 201)

    case.vendor.inject = inject
    reply = await case.invoke(connection, "create_issue", REPO | {"title": "x", "labels": ["bug"]})
    assert reply.status == "uncertain", reply
    assert len(sent) == 1 and "private" not in repr(reply)


async def test_new_label_rejected_before_write(case):
    connection = await case.connect()
    reply = await case.invoke(connection, "create_issue", REPO | {"title": "x", "labels": ["new"]})
    assert reply.status == "failed" and not case.vendor.writes


async def test_patch_missing_is_not_a_complete_diff(case):
    connection = await case.connect()
    reply = await case.invoke(connection, "list_pull_request_files", PULL)
    coverage = reply.data["data"]["coverage"]
    assert coverage["missing_patch_count"] == 1 and coverage["patches_are_partial"]
    assert coverage["file_list_complete"]
    case.vendor.pull["changed_files"] = 3001
    reply = await case.invoke(connection, "list_pull_request_files", PULL)
    assert reply.data["data"]["coverage"]["exceeds_api_limit"]
    assert not reply.data["data"]["coverage"]["file_list_complete"]


async def test_pull_change_during_file_read_is_detected(case):
    connection = await case.connect()

    async def inject(request):
        if request.url.path.endswith("/files"):
            case.vendor.pull["head"] = {"sha": "c" * 40}

    case.vendor.inject = inject
    assert (await case.invoke(connection, "list_pull_request_files", PULL)).status == "failed"


@pytest.mark.parametrize(
    "content",
    [
        b'{"id":10,"id":11,"full_name":"octo/demo"}',
        b"null",
        b"[]",
        b'{"id":true,"full_name":"octo/demo"}',
        b"X" * (1024 * 1024 + 1),
    ],
)
async def test_invalid_responses_fail(case, content):
    connection = await case.connect()

    async def inject(request):
        if request.url.path == ROOT:
            return httpx.Response(200, content=content)

    case.vendor.inject = inject
    assert (await case.invoke(connection, "get_repository", REPO)).status == "failed"


async def test_cancel_write_does_not_resend(case):
    connection = await case.connect()
    started = asyncio.Event()
    sent = []

    async def inject(request):
        if request.url.path == ROOT + "/issues" and request.method == "POST":
            sent.append(request)
            started.set()
            await asyncio.Event().wait()

    case.vendor.inject = inject
    task = asyncio.create_task(case.invoke(connection, "create_issue", REPO | {"title": "x"}))
    await asyncio.wait_for(started.wait(), 2)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert len(sent) == 1


async def test_label_replacement_and_empty_body_are_explicit(case):
    connection = await case.connect()
    reply = await case.invoke(connection, "update_issue", ISSUE | {"body": "", "labels": []})
    assert reply.status == "succeeded"
    assert case.vendor.writes[-1] == {"body": "", "labels": []}
    assert json.loads(case.vendor.calls[-1].content) == {"body": "", "labels": []}


@pytest.mark.parametrize(
    "status,headers,message",
    [
        (429, {"retry-after": "30"}, "private"),
        (403, {"x-ratelimit-remaining": "0", "x-ratelimit-reset": "9999999999"}, "private"),
        (403, {}, "You have exceeded a secondary rate limit"),
        (200, {"x-ratelimit-remaining": "0"}, None),
    ],
)
async def test_rate_cooldown_blocks_further_business_requests(case, status, headers, message):
    connection = await case.connect()

    async def inject(request):
        if request.url.path == "/user/installations":
            data = {"installations": []} if status == 200 else {"message": message}
            return response(data, status, headers)

    case.vendor.inject = inject
    first = await case.invoke(connection, "list_installations", {})
    assert first.status == ("succeeded" if status == 200 else "failed")
    before = len(case.vendor.calls)
    assert (await case.invoke(connection, "get_repository", REPO)).status == "failed"
    assert (await case.invoke(connection, "create_issue", REPO | {"title": "x"})).status == "failed"
    assert len(case.vendor.calls) == before


async def test_cooldown_and_mutation_spacing_are_enforced(case):
    import time

    connection = await case.connect()
    sent = []

    async def inject(request):
        if request.url.path == ROOT + "/issues" and request.method == "POST":
            sent.append(time.monotonic())

    case.vendor.inject = inject
    for _ in range(2):
        assert (
            await case.invoke(connection, "create_issue", REPO | {"title": "x"})
        ).status == "succeeded"
    assert sent[1] - sent[0] >= 0.99


async def test_read_redirect_honors_size_and_eof(case):
    connection = await case.connect()

    async def inject(request):
        if request.url.path == ROOT:
            return httpx.Response(
                301, headers={"location": "https://api.github.com/repositories/10"}
            )
        if request.url.path == "/repositories/10":
            return httpx.Response(200, content=b"{}", headers={"content-length": "10"})

    case.vendor.inject = inject
    assert (await case.invoke(connection, "get_repository", REPO)).status == "failed"


@pytest.mark.parametrize(
    "name,params",
    [
        ("list_installations", {}),
        ("list_labels", REPO),
        ("list_issues", REPO),
    ],
)
async def test_malformed_list_items_are_not_success(case, name, params):
    connection = await case.connect()

    async def inject(request):
        if request.url.path == "/user/installations":
            return response({"installations": [{}]})
        if request.url.path in (ROOT + "/labels", ROOT + "/issues"):
            return response([{}])

    case.vendor.inject = inject
    assert (await case.invoke(connection, name, params)).status == "failed"


async def test_duplicate_files_do_not_claim_complete_coverage(case):
    connection = await case.connect()

    async def inject(request):
        if request.url.path.endswith("/files"):
            return response([{"filename": "a.py"}, {"filename": "a.py"}])

    case.vendor.inject = inject
    assert (await case.invoke(connection, "list_pull_request_files", PULL)).status == "failed"


@pytest.mark.parametrize(
    "location",
    [
        "https://api.github.com/repos/octo/demo",
        "https://api.github.com/repositories/10",
    ],
)
async def test_redirect_loop_is_bounded(case, location):
    connection = await case.connect()

    async def inject(request):
        if request.url.path in (ROOT, "/repositories/10"):
            return httpx.Response(301, headers={"location": location})

    case.vendor.inject = inject
    before = len(case.vendor.calls)
    assert (await case.invoke(connection, "get_repository", REPO)).status == "failed"
    assert len(case.vendor.calls) == before + 5  # SDK GET plus bounded adapter GETs.


async def test_skipped_next_page_is_rejected(case):
    connection = await case.connect()

    async def inject(request):
        if request.url.path.endswith("/labels"):
            return response(
                [],
                headers={
                    "link": '<https://api.github.com/repos/octo/demo/labels?page=3>; rel="next"'
                },
            )

    case.vendor.inject = inject
    assert (await case.invoke(connection, "list_labels", REPO)).status == "failed"


async def test_cooldown_does_not_block_another_connection(case):
    first = await case.connect()
    case.vendor.profile_change = {"id": 43, "login": "second"}
    second = await case.connect()

    async def inject(request):
        if request.url.path == "/user/installations":
            return response({"message": "limited"}, 429, {"retry-after": "60"})

    case.vendor.inject = inject
    assert (await case.invoke(first, "list_installations", {})).status == "failed"
    before = len(case.vendor.calls)
    case.vendor.inject = None
    assert (await case.invoke(second, "list_installations", {})).status == "succeeded"
    assert len(case.vendor.calls) == before + 1
