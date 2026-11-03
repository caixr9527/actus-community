"""Optional typed stderr events. No provider prose, credential or identity values."""

import asyncio
import json
import os
import select
from contextlib import contextmanager
from contextvars import ContextVar
from uuid import UUID, uuid4

from connector_sdk import AuthorizationRejected, HttpError, OAuthClientError

PREFIX = b"ACTUS_DIAGNOSTIC_V1 "
_current = ContextVar("feishu_diagnostic_attempt", default=None)
_checks = {"access_valid", "refresh_valid", "access_expiry_valid", "refresh_expiry_valid",
           "token_type_valid", "scope_valid", "required_scope_granted", "account_valid",
           "tenant_valid", "name_valid"}
_reasons = {"transport", "timeout", "provider_rejected", "client_rejected", "invalid_response",
            "invalid_material", "required_scope_missing", "invalid_identity", "refresh_not_rotated",
            "processing_failed", "cancelled"}


def _identifier(value):
    try:
        text = str(value)
        return text if str(UUID(text)) == text and UUID(text).int else None
    except (TypeError, ValueError):
        return None


@contextmanager
def scope(phase, *, transaction_id=None, request_id=None):
    value = {"phase": phase, "attempt_id": str(uuid4()), "dropped_emissions": 0}
    for key, source in (("transaction_id", transaction_id), ("request_id", request_id)):
        if (ident := _identifier(source)) is not None:
            value[key] = ident
    token = _current.set(value)
    try:
        yield
    finally:
        _current.reset(token)


def _write(data):
    # A bounded atomic pipe write is best effort; don't wait for a saturated stderr sink.
    if not select.select([], [2], [], 0)[1]:
        return False
    return os.write(2, data) == len(data)


def emit(outcome, *, phase=None, http_status=None, provider_code=None, reason=None, checks=None):
    context = _current.get()
    if context is None:
        return
    try:
        record = {k: v for k, v in context.items() if k != "dropped_emissions" or v}
        record.update(phase=phase or context["phase"], outcome=outcome)
        if record["phase"] not in {"oauth_exchange", "oauth_refresh", "token_response", "identity"}:
            return
        if outcome not in {"started", "observed", "succeeded", "failed", "cancelled"}:
            return
        for key, value, low, high in (("http_status", http_status, 100, 599),
                                      ("provider_code", provider_code, 0, 2147483647)):
            if type(value) is int and low <= value <= high:
                record[key] = value
        if reason in _reasons:
            record["reason"] = reason
        if checks is not None:
            if type(checks) is not dict or checks.keys() - _checks or any(
                    type(value) is not bool for value in checks.values()):
                return
            record["checks"] = checks
        data = PREFIX + json.dumps(record, separators=(",", ":")).encode() + b"\n"
        if len(data) > 2048 or not _write(data):
            context["dropped_emissions"] = min(2147483647, context["dropped_emissions"] + 1)
        else:
            context["dropped_emissions"] = 0
    except Exception:
        # Never replace an authorization result or its primary exception with a logging error.
        context["dropped_emissions"] = min(2147483647, context["dropped_emissions"] + 1)


def reason_for(error):
    if isinstance(error, asyncio.CancelledError):
        return "cancelled"
    if isinstance(error, TimeoutError):
        return "timeout"
    if isinstance(error, OAuthClientError):
        return "client_rejected"
    if isinstance(error, AuthorizationRejected):
        return "provider_rejected"
    if isinstance(error, HttpError):
        if error.code == "feishu_invalid_response":
            return "invalid_response"
        if error.code in {"feishu_access_denied", "feishu_business_failed", "feishu_rate_limited"}:
            return "provider_rejected"
        return "timeout" if error.code == "http_deadline_exceeded" else "transport"
    return "processing_failed"
