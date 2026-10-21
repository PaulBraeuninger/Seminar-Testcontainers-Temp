"""Shared fixtures for integration tests."""

from collections.abc import Iterator
from secrets import token_hex

from pytest import fixture
from testcontainers.community.postgres import PostgresContainer
from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import CompositeWaitStrategy, HttpWaitStrategy, PortWaitStrategy


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


@fixture
def mailpit_container() -> Iterator[DockerContainer]:
    """Provide an isolated Mailpit instance and clean up the container afterward.

    Yields:
        DockerContainer: The running Mailpit container with SMTP and HTTP ports available.

    """
    container = (
        DockerContainer("axllent/mailpit:v1.29.3")
        .with_exposed_ports(1025, 8025)
        .waiting_for(
            CompositeWaitStrategy(
                PortWaitStrategy(1025).with_startup_timeout(30),
                HttpWaitStrategy(8025, "/readyz").for_status_code(200).with_startup_timeout(30),
            )
        )
    )
    with container as mailpit:
        yield mailpit
