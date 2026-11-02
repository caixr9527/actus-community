import asyncio
import json

import httpx
import pytest
from connector_sdk.client import ClientError
from vendor import CREATE, PROFILE, TASK, response

CASES = [
    ("get_current_user", {}, "GET", PROFILE),
    ("create_personal_todo", {"subject": "复核"}, "POST", CREATE),
    ("update_personal_todo", {"task_id": "task-1", "description": "修改"}, "PUT", TASK + "/update"),
    (
        "set_my_executor_status",
        {"task_id": "task-1", "done": True},
        "PUT",
        TASK + "/updateExecutorStatus",
    ),
    ("delete_personal_todo", {"task_id": "task-1"}, "DELETE", TASK + "/remove"),
]


@pytest.mark.parametrize("name,params,method,path", CASES)
async def test_static_wire_operations(case, name, params, method, path):
    connection = await case.connect()
    reply = await case.invoke(connection, name, params)
    assert reply.status == "succeeded", reply
    assert case.vendor.calls[-1].method == method and case.vendor.calls[-1].url.path == path
    if name == "get_current_user":
        assert reply.data == {"union_id": "union-42", "display_name": "测试用户"}
        assert "private-mobile" not in repr(reply) and "private-email" not in repr(reply)
    elif name == "create_personal_todo":
        assert reply.data == {"task_id": "task-1", "created_time_ms": 1793606400000}
    elif name == "set_my_executor_status":
        assert reply.data == {"task_id": "task-1", "success": True, "executor_done": True}
    else:
        assert reply.data == {"task_id": "task-1", "success": True}


@pytest.mark.parametrize(
    "name,params",
    [
        ("get_current_user", {"union_id": "other"}),
        ("create_personal_todo", {"subject": ""}),
        ("create_personal_todo", {"subject": "  "}),
        ("create_personal_todo", {"subject": "x" * 51}),
        ("create_personal_todo", {"subject": "x", "executor_ids": ["other"]}),
        ("create_personal_todo", {"subject": "x", "creator_id": "other"}),
        ("create_personal_todo", {"subject": "x", "description": None}),
        ("create_personal_todo", {"subject": "x", "due_at": None}),
        ("create_personal_todo", {"subject": "x", "due_at": "2026-11-03T18:00:00"}),
        ("create_personal_todo", {"subject": "x", "due_at": "2026-02-30T00:00:00Z"}),
        ("create_personal_todo", {"subject": "x", "due_at": "2026-11-03T18:00:00-00:00"}),
        ("create_personal_todo", {"subject": "x", "due_at": "2026-11-03"}),
        ("create_personal_todo", {"subject": "x", "due_at": "2026-11-03T18:00:00.0001Z"}),
        ("update_personal_todo", {"task_id": "task-1"}),
        ("update_personal_todo", {"task_id": "task-1", "description": None}),
        ("update_personal_todo", {"task_id": "task-1", "description": "x" * 1001}),
        ("update_personal_todo", {"task_id": "task-1", "done": True}),
        ("update_personal_todo", {"task_id": "task-1", "executorIds": ["other"]}),
        ("delete_personal_todo", {"task_id": "../x"}),
        ("delete_personal_todo", {"task_id": "https://evil.test/x"}),
        ("delete_personal_todo", {"task_id": "x%2fy"}),
        ("delete_personal_todo", {"task_id": "x?other=1"}),
        ("delete_personal_todo", {"task_id": "x\ny"}),
        ("delete_personal_todo", {"task_id": True}),
        ("set_my_executor_status", {"task_id": "task-1", "done": 1}),
        ("set_my_executor_status", {"task_id": "task-1", "done": "false"}),
    ],
)
async def test_invalid_input_never_reaches_vendor(case, name, params):
    connection = await case.connect()
    before = len(case.vendor.calls)
    assert (await case.invoke(connection, name, params)).status == "failed"
    assert len(case.vendor.calls) == before


async def test_create_self_assignment_and_timezone_conversion(case):
    connection = await case.connect()
    result = await case.invoke(
        connection,
        "create_personal_todo",
        {
            "subject": "复核",
            "description": "说明",
            "due_at": "2026-11-03T18:00:00.123+08:00",
        },
    )
    assert result.status == "succeeded", result
    assert case.vendor.writes == [
        {
            "subject": "复核",
            "description": "说明",
            "dueTime": 1793700000123,
            "executorIds": ["union-42"],
        }
    ]


async def test_update_omission_empty_description_and_restore_state(case):
    connection = await case.connect()
    result = await case.invoke(
        connection,
        "update_personal_todo",
        {
            "task_id": "task-1",
            "description": "",
        },
    )
    assert result.status == "succeeded"
    assert case.vendor.writes == [{"description": ""}]
    result = await case.invoke(
        connection,
        "set_my_executor_status",
        {
            "task_id": "task-1",
            "done": False,
        },
    )
    assert result.status == "succeeded" and result.data["executor_done"] is False
    assert case.vendor.writes[-1] == {"done": "false"}
    assert not case.vendor.calls[-1].content


@pytest.mark.parametrize("mode", ["changed", "denied", "malformed"])
async def test_identity_preflight_failure_does_not_dispatch_create(case, mode):
    connection = await case.connect()
    if mode == "changed":
        case.vendor.profile_change = {"unionId": "another-user"}
    else:

        async def inject(request):
            if request.url.path == PROFILE:
                return response({"error": "private"}, 403) if mode == "denied" else response({})

        case.vendor.inject = inject
    reply = await case.invoke(connection, "create_personal_todo", {"subject": "复核"})
    assert reply.status == "failed" and not case.vendor.writes
    assert all(r.url.path != CREATE for r in case.vendor.calls)


@pytest.mark.parametrize("name,params,method,path", CASES[1:])
@pytest.mark.parametrize("mode", ["lost", "bad", "rejected", "http", "redirect"])
async def test_sent_write_is_uncertain_without_retry(case, name, params, method, path, mode):
    connection = await case.connect()
    sent = []

    async def inject(request):
        if request.url.path == path:
            sent.append(request)
            if mode == "lost":
                raise httpx.ReadError("private-write-body")
            if mode == "bad":
                return response({})
            if mode == "rejected":
                return response({"success": False, "message": "private-write-body"})
            if mode == "http":
                return response({"message": "private-write-body"}, 503)
            return httpx.Response(307, headers={"location": "https://evil.test/target"})

    case.vendor.inject = inject
    reply = await case.invoke(connection, name, params)
    assert reply.status == "uncertain", reply
    assert len(sent) == 1 and "private-write-body" not in repr(reply)


@pytest.mark.parametrize(
    "body",
    [
        b"null",
        b"[]",
        b'{"unionId":"union-42","unionId":"other"}',
        b'{"unionId":"union-42","nick":NaN}',
        b"{",
        b"x" * (1024 * 1024 + 1),
        b'{"unionId":"union-42","code":"private"}',
    ],
)
async def test_bad_json_is_not_success(case, body):
    connection = await case.connect()

    async def inject(request):
        if request.url.path == PROFILE:
            return httpx.Response(200, content=body)

    case.vendor.inject = inject
    assert (await case.invoke(connection, "get_current_user", {})).status == "failed"


@pytest.mark.parametrize("status", [400, 401, 403, 404, 429, 500])
async def test_vendor_errors_are_not_returned_or_retried(case, status):
    connection = await case.connect()

    async def inject(request):
        if request.url.path == PROFILE:
            return response({"message": "private-error"}, status, {"retry-after": "60"})

    case.vendor.inject = inject
    before = len(case.vendor.calls)
    result = await case.invoke(connection, "get_current_user", {})
    assert result.status == "failed" and "private-error" not in repr(result)
    assert len(case.vendor.calls) == before + 1


@pytest.mark.parametrize(
    "data",
    [
        {"taskId": "task-1", "createdTime": True},
        {"taskId": "task-1", "createdTime": 0},
        {"taskId": "../other", "createdTime": 1793606400000},
        {"taskId": "task-1"},
    ],
)
async def test_invalid_create_receipt_remains_uncertain(case, data):
    connection = await case.connect()

    async def inject(request):
        if request.url.path == CREATE:
            return response(data)

    case.vendor.inject = inject
    result = await case.invoke(connection, "create_personal_todo", {"subject": "x"})
    assert result.status == "uncertain"


async def test_delete_uses_string_receipt_contract(case):
    connection = await case.connect()

    async def inject(request):
        if request.url.path == TASK + "/remove":
            return response({"success": True})

    case.vendor.inject = inject
    assert (
        await case.invoke(
            connection,
            "delete_personal_todo",
            {
                "task_id": "task-1",
            },
        )
    ).status == "uncertain"


async def test_read_redirect_does_not_follow_or_replay(case):
    connection = await case.connect()

    async def inject(request):
        if request.url.path == PROFILE:
            return httpx.Response(302, headers={"location": "https://evil.test/profile"})

    case.vendor.inject = inject
    before = len(case.vendor.calls)
    assert (await case.invoke(connection, "get_current_user", {})).status == "failed"
    assert len(case.vendor.calls) == before + 1


async def test_cancelled_create_does_not_resend(case):
    connection = await case.connect()
    started, sent = asyncio.Event(), []

    async def inject(request):
        if request.url.path == CREATE:
            sent.append(json.loads(request.content))
            started.set()
            await asyncio.Event().wait()

    case.vendor.inject = inject
    task = asyncio.create_task(case.invoke(connection, "create_personal_todo", {"subject": "x"}))
    await asyncio.wait_for(started.wait(), 2)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert len(sent) == 1


@pytest.mark.parametrize(
    "changes",
    [
        {"subject": "bad\nsubject"},
        {"description": "bad\x00description"},
        {"due_at": "2026-11-03T18:00:00+08:99"},
        {"due_at": "2026-11-03T18:00:00+24:00"},
        {"due_at": "1970-01-01T00:00:00Z"},
        {"due_at": "0001-01-01T00:00:00+08:00"},
    ],
)
async def test_invalid_text_and_timezone_are_rejected_before_write(case, changes):
    connection = await case.connect()
    before = len(case.vendor.calls)
    reply = await case.invoke(connection, "create_personal_todo", {"subject": "x"} | changes)
    assert reply.status == "failed" and len(case.vendor.calls) == before


async def test_far_future_time_preserves_millisecond_boundary(case):
    connection = await case.connect()
    reply = await case.invoke(
        connection,
        "update_personal_todo",
        {
            "task_id": "task-1",
            "due_at": "9999-12-31T23:59:59.999Z",
        },
    )
    assert reply.status == "succeeded"
    assert case.vendor.writes == [{"dueTime": 253402300799999}]


async def test_original_deadline_cancels_sent_write(case):
    connection = await case.connect()
    sent = []

    async def inject(request):
        if request.url.path == CREATE:
            sent.append(request)
            await asyncio.Event().wait()

    case.vendor.inject = inject
    invocation = case.invocation(connection, "create_personal_todo")
    invocation["deadline"] = asyncio.get_running_loop().time() + 0.1
    with pytest.raises(ClientError) as captured:
        await asyncio.wait_for(
            case.sdk.invoke(
                "create_personal_todo",
                {"subject": "x"},
                **invocation,
            ),
            2,
        )
    assert captured.value.code == "client_deadline_exceeded"
    assert captured.value.outcome == "result_unknown" and len(sent) == 1


async def test_missing_nickname_does_not_break_stable_identity(case):
    case.vendor.profile_change = {"nick": None}
    connection = await case.connect()
    reply = await case.invoke(connection, "get_current_user", {})
    assert reply.status == "succeeded"
    assert reply.data == {"union_id": "union-42", "display_name": None}
