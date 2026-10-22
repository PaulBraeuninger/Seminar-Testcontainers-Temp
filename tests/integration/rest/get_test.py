"""Tests for GET requests to the REST API."""

from http import HTTPStatus
from typing import Final

from common_test import login
from constants import CTX, REST_URL
from httpx import get
from pytest import mark

pytestmark = mark.member


@mark.rest
@mark.get_request
@mark.parametrize("username", ["admin", "ole"])
def test_get_by_username(username: str) -> None:
    """Test for getting a member by username using REST API."""
    # arrange
    params = {"username": username}
    token: Final = login()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        REST_URL,
        params=params,
        headers=headers,
        verify=CTX,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    content: Final = response_body["content"]
    assert isinstance(content, list)
    assert len(content) == 1
    member = content[0]
    assert member is not None
    assert member.get("username") == username
    assert member.get("id") is not None


@mark.rest
@mark.get_request
@mark.parametrize("username", ["fail.query", "fail"])
def test_get_by_username_not_exists(username: str) -> None:
    """Test for getting a member by username that does not exist."""
    # arrange
    params = {"username": username}
    token: Final = login()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        REST_URL,
        params=params,
        headers=headers,
        verify=CTX,
    )

    # assert
    assert response.status_code == HTTPStatus.NOT_FOUND


@mark.rest
@mark.get_request
@mark.parametrize("email", ["admin@example.com", "ole.menke@example.com"])
def test_get_by_email(email: str) -> None:
    """Test for getting a member by email using REST API."""
    # arrange
    params = {"email_address": email}
    token: Final = login()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        REST_URL,
        params=params,
        headers=headers,
        verify=CTX,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    content: Final = response_body["content"]
    assert isinstance(content, list)
    assert len(content) == 1
    member = content[0]
    assert member is not None
    assert member.get("email_address") == email
    assert member.get("id") is not None


@mark.rest
@mark.get_request
@mark.parametrize("email", ["fail.query@example.com", "fail@fail.com"])
def test_get_by_email_not_exists(email: str) -> None:
    """Test for getting a member by email that does not exist."""
    # arrange
    params = {"email_address": email}
    token: Final = login()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        REST_URL,
        params=params,
        headers=headers,
        verify=CTX,
    )

    # assert
    assert response.status_code == HTTPStatus.NOT_FOUND
