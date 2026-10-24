from pathlib import Path

import pytest
from connector_sdk import AuthorizationRejected, HttpError, load_project
from pydantic import ValidationError

from form_demo.app import App, Auth, ListTickets, Login, Token


class Context:
    """Test double for public HTTP methods; no SDK persistence or transport is replaced."""

    def __init__(self, login=None, profile=None, tickets=None):
        self.login = login if login is not None else {"authenticated": True, "token": "test-token"}
        self.profile = profile if profile is not None else {
            "account_id": "account-1", "tenant_id": "tenant-1", "permissions": ["tickets.read"],
        }
        self.tickets = tickets if tickets is not None else {"items": [{"id": "1", "title": "Test"}]}
        self.calls = []

    def http(self, name, *, credential=None):
        owner = self

        class Client:
            async def request_json(self, method, path, **kwargs):
                assert name == "login" and credential is None
                owner.calls.append((name, method, path, kwargs))
                if isinstance(owner.login, Exception):
                    raise owner.login
                return owner.login

            async def get_json(self, path, **kwargs):
                assert name == "api"
                owner.calls.append((name, path, kwargs))
                if path == "me":
                    assert isinstance(credential, Token)
                    assert credential.token.get_secret_value() == "test-token"
                    return owner.profile
                assert path == "tickets" and credential is None
                return owner.tickets

        return Client()


def submission():
    return Login(tenant="tenant-1", username="user", password="test-password")


def test_declaration_uses_ordered_form_and_single_read_operation():
    declared = load_project(Path(__file__).resolve().parents[1] / "pyproject.toml")
    auth = declared.manifest.auth
    assert declared.manifest.id == "form-demo"
    assert auth.type == "form"
    assert [(f.name, f.type) for f in auth.fields] == [
        ("tenant", "text"), ("username", "text"), ("password", "secret"),
    ]
    assert all(field.required for field in auth.fields)
    assert tuple(declared.operations) == ("list_tickets",)
    assert declared.manifest.operations[0].effects == "read"
    assert "test-password" not in declared.manifest.to_json()


@pytest.mark.parametrize("permissions", [None, [], ["tickets.read"]])
async def test_login_exchange_verifies_server_identity_and_saves_only_token(permissions):
    ctx = Context(profile={"account_id": "account-1", "tenant_id": "tenant-1",
                           "permissions": permissions})
    result = await Auth().verify(ctx, submission())
    assert result.identity.account_id == "account-1" and result.identity.tenant_id == "tenant-1"
    assert type(result.credential).model_fields.keys() == {"token"}
    assert result.credential.token.get_secret_value() == "test-token"
    assert result.capabilities == (None if permissions is None else
                                   {"tickets.read": "tickets.read" in permissions})
    assert "test-token" not in repr(result) and "test-password" not in repr(result)
    assert ctx.calls[0] == ("login", "POST", "login", {"json": {
        "tenant": "tenant-1", "username": "user", "password": "test-password",
    }})
    assert ctx.calls[1] == ("api", "me", {})


@pytest.mark.parametrize("login,profile,error", [
    ({"authenticated": False}, None, AuthorizationRejected),
    ({"authenticated": True}, None, ValueError),
    ({"authenticated": True, "token": ""}, None, ValidationError),
    ({"authenticated": "true", "token": "test-token"}, None, ValidationError),
    (None, {}, ValidationError),
    (None, {"account_id": "a", "tenant_id": "other"}, AuthorizationRejected),
    (HttpError("http_transport_error"), None, HttpError),
])
async def test_invalid_credentials_identity_and_transport_fail_without_success(
    login, profile, error,
):
    with pytest.raises(error):
        await Auth().verify(Context(login=login, profile=profile), submission())


@pytest.mark.parametrize("change", [
    {"tenant": ""}, {"tenant": "other tenant"}, {"username": ""}, {"password": ""},
    {"password": None}, {"token": "unexpected"},
])
def test_login_fields_reject_invalid_or_extra_values(change):
    values = {"tenant": "tenant-1", "username": "user", "password": "test-password"}
    with pytest.raises(ValidationError):
        Login.model_validate(values | change, strict=True)


async def test_business_read_uses_sdk_http_and_validates_response():
    ctx = Context()
    output = await App().list_tickets(ctx, ListTickets(query="Test", limit=5))
    assert output.model_dump() == {"items": [{"id": "1", "title": "Test"}]}
    assert ctx.calls == [("api", "tickets", {"params": {"q": "Test", "limit": "5"}})]
    with pytest.raises(ValidationError):
        await App().list_tickets(Context(tickets={}), ListTickets())


@pytest.mark.parametrize("values", [{"limit": 0}, {"limit": 101}, {"limit": True},
                                    {"limit": "2"}, {"query": "x" * 201}, {"extra": 1}])
def test_business_parameters_are_bounded_and_strict(values):
    with pytest.raises(ValidationError):
        ListTickets.model_validate(values, strict=True)
