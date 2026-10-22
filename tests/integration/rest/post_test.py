"""Tests for POST requests to the REST API."""
from http import HTTPStatus
from re import search
from typing import Final

from constants import CTX, REST_URL
from httpx import post
from pytest import mark

token: str | None


pytestmark = mark.member


@mark.rest
@mark.post_request
def test_create_member() -> None:
    """Test for creating a new member using REST API."""
    # arrange
    member_data: Final = {
        "username": "test_member_rest",
        "first_name": "Post",
        "last_name": "Test",
        "gender": "M",
        "date_of_birth": "1990-01-01",
        "member_since": "2020-01-01",
        "email_address": "testmemberrest@example.com",
        "is_student": False,
        "interests": ["F"],
        "address": {
            "postal_code": "12345",
            "place": "City",
        },
        "books": [
            {
                "name": "REST Testing",
                "isbn": "978-3-16-148410-0",
                "author": "John Doe",
                "still_borrowed": True,
                "genre": "F",
            }
        ],
    }
    headers = {"Content-Type": "application/json"}

    # act
    response: Final = post(
        REST_URL,
        json=member_data,
        headers=headers,
        verify=CTX,
    )

    # assert
    assert response.status_code == HTTPStatus.CREATED
    location_header: Final = response.headers.get("Location")
    assert location_header is not None
    int_pattern: Final = "[1-9][0-9]*$"
    assert search(int_pattern, location_header) is not None
    assert not response.text


@mark.rest
@mark.post_request
def test_create_member_with_invalid_data() -> None:
    """Test for creating a new member with invalid data using REST API."""
    #arrange
    invalid_member_data: Final = {
        "username": "invalid_member_rest",
        "first_name": "Invalid",
        "last_name": "last name",
        "gender": "X",
        "date_of_birth": "1990-01-01",
        "member_since": "2020-01-01",
        "is_student": False,
        "email_address": "invalid_member.example",
        "interests": ["F"],
        "address": {
            "postal_code": "5",
            "place": "Test City",
        },
        "books": [
            {
                "name": "Invalid REST Testing",
                "isbn": "978-3-16-148410-0",
                "author": "John Doe",
                "still_borrowed": True,
                "genre": "F",
            }
        ],
    }
    headers = {"Content-Type": "application/json"}

    #act
    response: Final = post(
        REST_URL,
        json=invalid_member_data,
        headers=headers,
        verify=CTX,
    )

    #assert
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    response_body = response.text
    assert response_body is not None
    assert "last_name" in response_body
    assert "gender" in response_body
    assert "email_address" in response_body
    assert "postal_code" in response_body
