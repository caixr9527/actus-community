"""Personal APIs only; no enterprise token, delegated operator or write retry."""

from connector_sdk import HttpError, OperationRejected
from pydantic import ValidationError

from .api import profile, request
from .models import Created, ExecutorReceipt, Receipt, milliseconds


def changes(params):
    result = {}
    for key in ("subject", "description", "due_at"):
        if key not in params.model_fields_set:
            continue
        value = getattr(params, key)
        if key == "due_at":
            value = milliseconds(value)
            key = "dueTime"
        result[key] = value
    return result


async def current_user(ctx, params):
    user = await profile(ctx)
    if user.union_id != ctx.connection.identity.account_id:
        raise HttpError("dingtalk_identity_changed")
    return user


async def create(ctx, params):
    try:
        user = await current_user(ctx, None)
    except HttpError:
        # A failed identity preflight has not dispatched the todo write.
        raise OperationRejected() from None
    body = changes(params) | {"executorIds": [user.union_id]}
    data = await request(ctx, "POST", "v1.0/todo/users/me/personalTasks", body=body)
    try:
        return Created(task_id=data.get("taskId"), created_time_ms=data.get("createdTime"))
    except ValidationError:
        raise HttpError("dingtalk_invalid_receipt") from None


def receipt(data, *, deletion=False):
    # The official SDK declares DELETE success as string; PUT success is boolean.
    accepted = data.get("success") == "true" if deletion else data.get("success") is True
    if not accepted:
        raise HttpError("dingtalk_invalid_receipt")


async def update(ctx, params):
    data = await request(
        ctx, "PUT", f"v1.0/todo/users/me/tasks/{params.task_id}/update", body=changes(params)
    )
    receipt(data)
    return Receipt(task_id=params.task_id, success=True)


async def executor_status(ctx, params):
    data = await request(
        ctx,
        "PUT",
        f"v1.0/todo/users/me/tasks/{params.task_id}/updateExecutorStatus",
        params={"done": "true" if params.done else "false"},
    )
    receipt(data)
    return ExecutorReceipt(task_id=params.task_id, success=True, executor_done=params.done)


async def delete(ctx, params):
    data = await request(ctx, "DELETE", f"v1.0/todo/users/me/tasks/{params.task_id}/remove")
    receipt(data, deletion=True)
    return Receipt(task_id=params.task_id, success=True)
