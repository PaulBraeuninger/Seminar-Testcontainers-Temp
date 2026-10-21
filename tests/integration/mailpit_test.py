"""Integration tests for the Mailpit test container."""

from email.message import EmailMessage
from smtplib import SMTP

from httpx import Client
from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import HttpWaitStrategy


def test_mailpit_delivery(mailpit_container: DockerContainer) -> None:
    """Verify that Mailpit receives SMTP messages and exposes their content via HTTP.

    Args:
        mailpit_container: The isolated Mailpit container provided by the fixture.

    """
    
    # Arrange
    host = mailpit_container.get_container_host_ip()
    smtp_port = int(mailpit_container.get_exposed_port(1025))
    http_port = int(mailpit_container.get_exposed_port(8025))
    sender = "sender@example.com"
    recipient = "recipient@example.com"
    subject = "Mailpit integration test"
    body = "This message was sent through the Mailpit test container."

    message = EmailMessage()
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    # Act
    with SMTP(host, smtp_port, timeout=10) as smtp:
        refused_recipients = smtp.send_message(message)

    # Assert
    assert refused_recipients == {}

    HttpWaitStrategy(8025, "/api/v1/message/latest").for_status_code(200).with_startup_timeout(10).wait_until_ready(
        mailpit_container
    )
    with Client(base_url=f"http://{host}:{http_port}", timeout=10) as client:
        response = client.get("/api/v1/message/latest")
        response.raise_for_status()
        received_message = response.json()

    assert received_message["From"]["Address"] == sender
    assert [address["Address"] for address in received_message["To"]] == [recipient]
    assert received_message["Subject"] == subject
    assert received_message["Text"].strip() == body
