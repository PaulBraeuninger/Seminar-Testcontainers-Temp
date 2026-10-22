"""Integration tests for the PostgreSQL test container."""

from pytest import mark
from sqlalchemy import create_engine, text
from testcontainers.community.postgres import PostgresContainer

pytestmark = mark.postgres


def test_postgres_connection(postgres_container: PostgresContainer) -> None:
    """Verify that the PostgreSQL container accepts connections and executes SQL.

    Args:
        postgres_container: The running PostgreSQL container provided by the fixture.

    """
    # arrange
    engine = create_engine(postgres_container.get_connection_url())
    try:
        # act
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1")).scalar_one()

        # assert
        assert result == 1
    finally:
        engine.dispose()
