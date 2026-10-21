"""Constants for integration tests."""

from pathlib import Path
from ssl import create_default_context
from typing import Final

__all__ = [
    "BASE_URL",
    "CERTIFICATE",
    "CTX",
    "DB_POPULATE_PATH",
    "GRAPHQL_PATH",
    "GRAPHQL_URL",
    "HEALTH_URL",
    "HOST",
    "KEYCLOAK_POPULATE_PATH",
    "PASSWORD_ADMIN",
    "PORT",
    "REST_PATH",
    "REST_URL",
    "SCHEMA",
    "TIMEOUT",
    "TOKEN_PATH",
    "USERNAME_ADMIN",
]


SCHEMA: Final = "https"
PORT: Final = 8000

HOST: Final = "127.0.0.1"

BASE_URL: Final = f"{SCHEMA}://{HOST}:{PORT}"

REST_PATH: Final = "/rest"
REST_URL: Final = f"{BASE_URL}{REST_PATH}"
HEALTH_URL: Final = f"{BASE_URL}/health"

GRAPHQL_PATH: Final = "/graphql"
GRAPHQL_URL: Final = f"{BASE_URL}/graphql"

TOKEN_PATH: Final = "/auth/token"  # noqa: S105
DB_POPULATE_PATH: Final = "/dev/db_populate"
KEYCLOAK_POPULATE_PATH: Final = "/dev/keycloak_populate"

USERNAME_ADMIN: Final = "admin"
PASSWORD_ADMIN: Final = "p"  # noqa: S105  # NOSONAR

TIMEOUT: Final = 30

CERTIFICATE: Final = str(Path(__file__).with_name("certificate.crt"))

CTX = create_default_context(cafile=CERTIFICATE)
