"""The module contains tests for the endpoint GET."""

from http import HTTPStatus
from typing import Final

from common_test import login
from constants import CTX, REST_URL
from httpx import get
from pytest import mark

pytestmark = mark.member


@mark.rest
@mark.get_request
@mark.parametrize("member_id", [1, 2])
def test_get_by_id_admin(member_id: int) -> None:
    """Test for getting a member by ID using REST API as admin."""
    # arrange
    token: Final = login()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        f"{REST_URL}/{member_id}",
        headers=headers,
        verify=CTX,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    id_actual: Final = response_body.get("id")
    assert id_actual is not None
    assert id_actual == member_id


@mark.rest
@mark.get_request
@mark.parametrize("member_id", [0, -1, 9999])
def test_get_by_id_non_existent(member_id: int) -> None:
    """Test for getting a non-existent member by ID using REST API."""
    # arrange
    token: Final = login()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        f"{REST_URL}/{member_id}",
        headers=headers,
        verify=CTX,
    )

    # assert
    assert response.status_code == HTTPStatus.NOT_FOUND


@mark.rest
@mark.get_request
def test_get_by_id_patient() -> None:
    """Test for getting a member by ID using REST API as member."""
    # arrange
    member_id: Final = 2
    token: Final = login(username="ole")
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        f"{REST_URL}/{member_id}",
        headers=headers,
        verify=CTX,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    id_actual: Final = response_body.get("id")
    assert id_actual is not None
    assert id_actual == member_id


@mark.rest
@mark.get_request
@mark.parametrize("member_id", [1, 3])
def test_get_by_id_patient_forbidden(member_id: int) -> None:
    """Test for getting a member by ID using REST API as member with forbidden access."""
    # arrange
    token: Final = login(username="ole")
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        f"{REST_URL}/{member_id}",
        headers=headers,
        verify=CTX,
    )

    # assert
    assert response.status_code == HTTPStatus.FORBIDDEN
