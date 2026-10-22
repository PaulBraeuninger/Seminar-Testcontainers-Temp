"""Tests for DELETE requests to the REST API."""

from http import HTTPStatus
from typing import Final

from common_test import login
from constants import CTX, REST_URL
from httpx import delete
from pytest import mark

pytestmark = mark.member


@mark.rest
@mark.delete_request
@mark.parametrize("member_id", [3])
def test_delete_by_id(member_id: int) -> None:
    """Test DELETE /rest/{id}."""
    # arrange
    token: Final = login()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = delete(
        f"{REST_URL}/{member_id}",
        headers=headers,
        verify=CTX,
    )

    # assert
    assert response.status_code == HTTPStatus.NO_CONTENT
    assert not response.content
