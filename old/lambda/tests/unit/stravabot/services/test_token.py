from datetime import timedelta
from unittest.mock import patch

import jwt
import pytest

from stravabot.models import Token
from stravabot.services.token import TokenService


@pytest.fixture
def token_service():
    return TokenService("secret")


def test_generate_returns_expected_token_without_ttl(token_service):
    token = token_service.generate(user_id="a-user-id", data={"foo": "bar"})

    decoded_token = jwt.decode(token.token, "secret", ["HS256"])

    assert token.expires is None
    assert token.slack_user_id == "a-user-id"
    assert token.data == {"sub": "a-user-id", "foo": "bar"}
    assert decoded_token == {
        "sub": "a-user-id",
        "foo": "bar",
    }


def test_generate_returns_expected_token_with_ttl(freezer, token_service):
    freezer.move_to("2050-01-01T10:10:10")
    token = token_service.generate(user_id="a-user-id", data={"foo": "bar"}, ttl=timedelta(days=10))

    decoded_token = jwt.decode(token.token, "secret", ["HS256"])

    assert token.expires == 2525508610
    assert token.slack_user_id == "a-user-id"
    assert token.data == {"sub": "a-user-id", "exp": 2525508610, "foo": "bar"}
    assert decoded_token == {
        "sub": "a-user-id",
        "exp": 2525508610,
        "foo": "bar",
    }


@patch("stravabot.services.token.jwt")
def test_generate_passes_secret_to_jwt(jwt):
    tokens = TokenService("shh-its-a-secret")
    tokens.generate("a-user", {})
    jwt.encode.assert_called_once_with({"sub": "a-user"}, "shh-its-a-secret", "HS256")


def test_decode_returns_expected_token_without_expires(token_service):
    token = jwt.encode(
        {
            "sub": "a-user-id",
            "some": "data",
        },
        "secret",
        "HS256",
    )
    assert token_service.decode(token) == Token(
        slack_user_id="a-user-id",
        data={
            "sub": "a-user-id",
            "some": "data",
        },
        token=token,
    )


def test_decode_returns_expected_token_with_expires(token_service):
    token = jwt.encode(
        {
            "sub": "a-user-id",
            "some": "data",
            "exp": 2525508610,
        },
        "secret",
        "HS256",
    )
    assert token_service.decode(token) == Token(
        slack_user_id="a-user-id",
        expires=2525508610,
        data={
            "sub": "a-user-id",
            "some": "data",
            "exp": 2525508610,
        },
        token=token,
    )


@patch("stravabot.services.token.jwt")
def test_decode_passes_secret_to_jwt(jwt):
    tokens = TokenService("shh-its-a-secret")
    tokens.decode("a-token")
    jwt.decode.assert_called_once_with("a-token", "shh-its-a-secret", ["HS256"])
