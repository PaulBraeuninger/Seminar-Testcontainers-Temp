"""Test for Mutation with GraphQL."""

from http import HTTPStatus
from typing import Final

from constants import CTX, GRAPHQL_URL
from httpx import post
from pytest import mark

pytestmark = mark.member


@mark.graphql
@mark.mutation
def test_create_member() -> None:
    """Test for creating a new member using GraphQL API."""
    # arrange
    query: Final = {
        "query": """
            mutation {
                createMember(
                    memberInput: {
                        username: "test_member_graphql"
                        firstName: "Graphql"
                        lastName: "Testmember"
                        gender: MALE
                        dateOfBirth: "1990-01-01"
                        memberSince: "2020-01-01"
                        isStudent: false
                        emailAddress: "test.graphql.member@example.com"
                        interests: [FANTASY]
                        address: {
                            postalCode: "12345"
                            place: "Test City"
                            }
                        books: [
                            {
                                name: "GraphQL Testing"
                                isbn: "978-3-16-148410-0"
                                author: "John Doe"
                                stillBorrowed: true
                                genre: FANTASY
                            }
                        ]
                    }
                ) {
                    id
                }
            }
            """,
    }
    # act
    response: Final = post(GRAPHQL_URL, json=query, verify=CTX)

    # assert
    assert response is not None
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    assert isinstance(response_body["data"]["createMember"]["id"], int)
    assert response_body.get("errors") is None
