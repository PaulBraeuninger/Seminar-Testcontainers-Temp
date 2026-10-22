"""Tests for PUT requests to the REST API."""

from http import HTTPStatus
from typing import Final

from common_test import login
from constants import CTX, REST_URL
from httpx import put
from pytest import mark

pytestmark = mark.member


@mark.rest
@mark.put_request
def test_update_member() -> None:
    """Test for updating an existing member using REST API."""
    # arrange
    token: Final = login()
    assert token is not None
    member_id: Final = 2
    if_match: Final = '"0"'
    updated_member_data: Final = {
        "first_name": "Put",
        "last_name": "Test",
        "gender": "M",
        "date_of_birth": "1990-01-01",
        "member_since": "2020-01-01",
        "is_student": False,
        "email_address": "updated_member@example.com",
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "If-Match": if_match,
    }

    # act
    response: Final = put(
        f"{REST_URL}/{member_id}",
        json=updated_member_data,
        headers=headers,
        verify=CTX,
    )

    # assert
    assert response.status_code == HTTPStatus.NO_CONTENT
    assert not response.text


@mark.rest
@mark.put_request
def tes_put_with_invalid_data() -> None:
    """Test for updating a member using invalid data."""
    #arrange
    member_id: Final = 3
    invalid_member_data: Final = {
        "first_name": "wrong_first_name",
        "last_name": "wrong_last_name...",
        "date_of_birth": "1990-01-01",
        "member_since": "2020-01-01",
        "is_student": False,
        "email_address": "invalid@"
    }
    token: Final = login()
    assert token is not None
    headers = {
        "If-Match": '"0"',
        "Authorization": f"Bearer {token}",
    }

    #act
    response: Final = put(
        f"{REST_URL}/{member_id}",
        json=invalid_member_data,
        headers=headers,
        verify=CTX
    )

    #assert
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert "first_name" in response.text
    assert "last_name" in response.text
    assert "email_address" in response.text
