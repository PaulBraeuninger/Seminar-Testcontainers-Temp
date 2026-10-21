"""Shared fixtures for the Testcontainers tests."""

from collections.abc import Iterator
from pathlib import Path
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


@fixture(scope="session")
def keycloak_container() -> Iterator[DockerContainer]:
    """Provide Keycloak with an isolated test realm and clean up after the session.

    Yields:
        DockerContainer: The running Keycloak container with imported users and client roles.

    """
    realm_file = Path(__file__).parent / "resources" / "library-test-realm.json"
    container = (
        DockerContainer("quay.io/keycloak/keycloak:26.5.5")
        .with_exposed_ports(8080)
        .with_copy_into_container(realm_file, "/opt/keycloak/data/import/library-test-realm.json")
        .with_command("start-dev --import-realm")
        .waiting_for(
            HttpWaitStrategy(8080, "/realms/library-test/.well-known/openid-configuration")
            .for_status_code(200)
            .with_startup_timeout(120)
        )
    )
    with container as keycloak:
        yield keycloak
