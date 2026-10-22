"""Integration tests for the Keycloak test container using synthetic test credentials."""

# ruff: noqa: PLC0415
# Defer project imports so test collection does not load local application configuration.

from base64 import urlsafe_b64decode, urlsafe_b64encode
from datetime import date
from http import HTTPStatus
from json import dumps, loads
from types import SimpleNamespace
from typing import TYPE_CHECKING

from fastapi import HTTPException, Request
from jwcrypto.jwt import JWTExpired
from keycloak import KeycloakAuthenticationError, KeycloakOpenID
from pytest import fixture, mark, raises
from testcontainers.core.container import DockerContainer

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

    from library.security.token_service import TokenService
    from library.service.member_service import MemberService

pytestmark = mark.security

PASSWORD = "test-password"  # noqa: S105 -- Only used in the disposable test realm.


@fixture
def keycloak_client(keycloak_container: DockerContainer) -> KeycloakOpenID:
    """Connect to the imported test realm through Keycloak's OpenID Connect client."""
    host = keycloak_container.get_container_host_ip()
    port = keycloak_container.get_exposed_port(8080)
    return KeycloakOpenID(
        server_url=f"http://{host}:{port}/",
        realm_name="library-test",
        client_id="python-client",
        client_secret_key="test-client-secret",  # noqa: S106 -- Disposable test realm.
        timeout=10,
    )


@fixture
def token_service() -> TokenService:
    """Provide the project's token service without contacting an external server."""
    from library.security.token_service import TokenService

    return TokenService()


@fixture
def container_token_service(token_service: TokenService, keycloak_client: KeycloakOpenID) -> TokenService:
    """Use the real Keycloak container for token issuance and signature verification."""
    token_service.keycloak = keycloak_client
    return token_service


@fixture
def member_service(mocker: MockerFixture) -> MemberService:
    """Provide the real member service with isolated repository and session dependencies."""
    from library.entity.member import Member
    from library.repository.member_repository import MemberRepository
    from library.service.member_service import MemberService

    member = mocker.Mock(
        spec=Member,
        id=1,
        username="member",
        version=0,
        first_name="Test",
        last_name="Member",
        gender=None,
        date_of_birth=date(2000, 1, 1),
        member_since=None,
        is_student=False,
        email_address="member@example.com",
        interests_json=[],
        address=mocker.Mock(postal_code="76133", place="Karlsruhe"),
    )
    repository = mocker.create_autospec(MemberRepository, instance=True)
    repository.find_by_id.return_value = member
    mocker.patch("library.service.member_service.Session")
    return MemberService(repository)


def _request(authorization: str | None) -> Request:
    headers = [] if authorization is None else [(b"authorization", authorization.encode())]
    return Request({"type": "http", "headers": headers})


@mark.keycloak
def test_keycloak_discovery(keycloak_client: KeycloakOpenID) -> None:
    """Verify that the imported realm publishes its OpenID Connect endpoints."""
    # Arrange
    issuer = f"{keycloak_client.connection.base_url}realms/library-test"

    # Act
    configuration = keycloak_client.well_known()

    # Assert
    assert configuration["issuer"] == issuer
    assert configuration["token_endpoint"] == f"{issuer}/protocol/openid-connect/token"
    assert configuration["jwks_uri"] == f"{issuer}/protocol/openid-connect/certs"


@mark.keycloak
@mark.parametrize(("username", "role"), [("admin", "admin"), ("member", "patient")])
def test_keycloak_login_and_roles(keycloak_client: KeycloakOpenID, username: str, role: str) -> None:
    """Verify login, JWT signatures, user claims, and the assigned client roles."""
    # Act
    token = keycloak_client.token(username, PASSWORD, scope="openid profile email")
    claims = keycloak_client.decode_token(token["access_token"])

    # Assert
    assert token["token_type"].lower() == "bearer"
    assert token["expires_in"] > 0
    assert token["refresh_token"]
    assert claims["iss"] == f"{keycloak_client.connection.base_url}realms/library-test"
    assert claims["preferred_username"] == username
    assert claims["email"] == f"{username}@example.com"
    assert claims["resource_access"]["python-client"]["roles"] == [role]


@mark.keycloak
@mark.parametrize(("username", "password"), [("member", "wrong-password"), ("unknown", PASSWORD)])
def test_keycloak_rejects_invalid_credentials(keycloak_client: KeycloakOpenID, username: str, password: str) -> None:
    """Verify that wrong passwords and unknown users cannot obtain a token."""
    # Act
    with raises(KeycloakAuthenticationError) as error:
        keycloak_client.token(username, password)

    # Assert
    assert error.value.response_code == HTTPStatus.UNAUTHORIZED
    assert error.value.response_body is not None
    assert b"invalid_grant" in error.value.response_body


@mark.keycloak
def test_keycloak_logout(keycloak_client: KeycloakOpenID) -> None:
    """Verify that logout invalidates the session's refresh token using introspection."""
    # Arrange
    token = keycloak_client.token("member", PASSWORD)
    hint = "refresh_token"
    assert keycloak_client.introspect(token["refresh_token"], token_type_hint=hint)["active"] is True

    # Act
    keycloak_client.logout(token["refresh_token"])

    # Assert
    assert keycloak_client.introspect(token["refresh_token"], token_type_hint=hint)["active"] is False


@mark.keycloak
@mark.parametrize("scheme", ["Bearer", "bearer", "BEARER"])
def test_token_service_reads_bearer_token(container_token_service: TokenService, scheme: str) -> None:
    """Verify request parsing and user mapping with a real signed Keycloak token."""
    from library.security.role import Role

    token = container_token_service.token("member", PASSWORD)["access_token"]

    user = container_token_service.get_user_from_request(_request(f"{scheme} {token}"))

    assert user.username == "member"
    assert user.email == "member@example.com"
    assert user.vorname == "Test"
    assert user.nachname == "Member"
    assert user.roles == [Role.PATIENT]


@mark.parametrize("authorization", [None, "", "Bearer", "Bearer one two", "Basic credentials"])
def test_token_service_rejects_invalid_authorization_header(token_service: TokenService, authorization: str | None) -> None:
    """Reject missing tokens, malformed headers, and unsupported authentication schemes."""
    from library.security.exceptions import AuthorizationError

    with raises(AuthorizationError):
        token_service.get_user_from_request(_request(authorization))


@mark.keycloak
def test_token_service_rejects_tampered_token(container_token_service: TokenService) -> None:
    """Reject changed user and role claims when the original signature is retained."""
    from library.security.exceptions import AuthorizationError

    token = container_token_service.token("member", PASSWORD)["access_token"]
    header, payload, signature = token.split(".")
    claims = loads(urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
    claims["preferred_username"] = "admin"
    claims["resource_access"]["python-client"]["roles"] = ["admin"]
    changed_payload = urlsafe_b64encode(dumps(claims).encode()).rstrip(b"=").decode()
    tampered_token = f"{header}.{changed_payload}.{signature}"

    with raises(AuthorizationError):
        container_token_service.get_user_from_request(_request(f"Bearer {tampered_token}"))


@mark.keycloak
def test_token_service_rejects_expired_token(container_token_service: TokenService, mocker: MockerFixture) -> None:
    """Reject a genuine signed token after its expiry, including the verifier's clock tolerance."""
    from library.security.exceptions import AuthorizationError

    token = container_token_service.token("member", PASSWORD)["access_token"]
    claims = container_token_service.keycloak.decode_token(token)
    # Replace only jwcrypto's clock; networking and the test runner keep real time.
    mocker.patch("jwcrypto.jwt.time", SimpleNamespace(time=lambda: claims["exp"] + 120))

    with raises(AuthorizationError) as error:
        container_token_service.get_user_from_request(_request(f"Bearer {token}"))

    assert isinstance(error.value.__cause__, JWTExpired)


@mark.keycloak
@mark.parametrize(
    ("username", "required_roles", "allowed"),
    [
        ("admin", ["ADMIN"], True),
        ("member", ["ADMIN"], False),
        ("member", ["PATIENT"], True),
        ("admin", ["PATIENT"], False),
        ("admin", ["ADMIN", "PATIENT"], True),
        ("member", ["ADMIN", "PATIENT"], True),
    ],
)
def test_role_based_access(
    container_token_service: TokenService, username: str, required_roles: list[str], *, allowed: bool
) -> None:
    """Enforce single-role and alternative-role requirements using real Keycloak tokens."""
    from library.security.role import Role
    from library.security.roles_required import RolesRequired

    token = container_token_service.token(username, PASSWORD)["access_token"]
    request = _request(f"Bearer {token}")
    roles = [Role[name] for name in required_roles]
    guard = RolesRequired(roles[0] if len(roles) == 1 else roles)

    if allowed:
        guard(request, container_token_service)
        assert request.state.current_user.username == username
        assert any(role in request.state.current_user.roles for role in roles)
    else:
        with raises(HTTPException) as error:
            guard(request, container_token_service)
        assert error.value.status_code == HTTPStatus.FORBIDDEN
        assert not hasattr(request.state, "current_user")


@mark.keycloak
@mark.member
@mark.parametrize("username", ["admin", "member"])
def test_member_access_to_existing_member(
    container_token_service: TokenService, member_service: MemberService, username: str
) -> None:
    """Allow admins to read other members and members to read their own data."""
    token = container_token_service.token(username, PASSWORD)["access_token"]
    user = container_token_service.get_user_from_request(_request(f"Bearer {token}"))

    member = member_service.find_by_id(member_id=1, user=user)

    assert member.id == 1
    assert member.username == "member"


@mark.keycloak
@mark.member
def test_member_cannot_read_other_member(
    container_token_service: TokenService, member_service: MemberService, mocker: MockerFixture
) -> None:
    """Deny reading another member's data even with a valid token and patient role."""
    from library.service.exceptions import ForbiddenError

    token = container_token_service.token("member", PASSWORD)["access_token"]
    user = container_token_service.get_user_from_request(_request(f"Bearer {token}"))
    mocker.patch.object(member_service.repo, "find_by_id").return_value = mocker.Mock(username="other-member")

    with raises(ForbiddenError):
        member_service.find_by_id(member_id=2, user=user)
