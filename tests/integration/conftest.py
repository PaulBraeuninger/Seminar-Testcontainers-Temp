"""Shared fixtures for integration tests."""

from collections.abc import Iterator
from secrets import token_hex

from pytest import fixture
from testcontainers.community.postgres import PostgresContainer


@fixture(scope="session")
def postgres_container() -> Iterator[PostgresContainer]:
    """Provide PostgreSQL for the test session and clean up the container afterward.

    Yields:
        PostgresContainer: The running PostgreSQL container with its connection details.

    """
    with PostgresContainer(
        image="postgres:18.3",
        username="library",
        password=token_hex(16),
        dbname="library",
        driver="psycopg",
    ) as postgres:
        yield postgres
