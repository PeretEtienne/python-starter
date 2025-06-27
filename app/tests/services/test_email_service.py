from email.message import EmailMessage
from pathlib import Path
from typing import Tuple

import pytest
from pytest_mock import MockFixture

from app.services.email.dto import EmailMessageData
from app.services.email.service import EmailService
from app.settings import settings


@pytest.fixture
def email_service() -> EmailService:
    return EmailService()


@pytest.fixture
def message_with_html() -> Tuple[EmailMessageData, dict[str, str | list[str]]]:
    receivers = ["to@example.com"]
    subject = "Test Subject"
    html = "<p>Hello</p>"

    return EmailMessageData(
        receivers=receivers,
        subject=subject,
        html=html,
    ), {
        "sender": settings.smtp_user,
        "receivers": receivers,
        "cc": [],
        "bcc": [],
        "subject": subject,
        "html": html,
    }


@pytest.fixture
def message_with_template(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> Tuple[EmailMessageData, dict[str, str | list[str]]]:
    tpl_dir = tmp_path / "email_tpl"
    tpl_dir.mkdir()
    (tpl_dir / "welcome.html").write_text("Hello {name}, see you at {static_host}")

    monkeypatch.setattr(settings, "static_dir", str(tmp_path))
    monkeypatch.setattr(settings, "static_host", "https://static.example.com")

    receivers = ["to@example.com"]
    subject = "Welcome!"
    tpl = "welcome"
    data_name = "Alice"
    static_host = settings.static_host

    return EmailMessageData(
        receivers=receivers,
        subject=subject,
        tpl=tpl,
        data={"name": data_name},
    ), {
        "sender": settings.smtp_user,
        "receivers": receivers,
        "cc": [],
        "bcc": [],
        "subject": subject,
        "data_name": data_name,
        "static_host": static_host,
    }


@pytest.mark.asyncio
async def test_send_with_html(
    email_service: EmailService,
    message_with_html: Tuple[EmailMessageData, dict[str, str | list[str]]],
    mocker: MockFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "dev_email", None)

    message, expected = message_with_html

    mock_sender = mocker.patch("app.services.email.service.EmailSender")
    mock_send = mock_sender.return_value.send
    mock_email = EmailMessage()
    mock_email["Subject"] = expected["subject"]
    mock_send.return_value = mock_email

    result = email_service.send(message)

    assert result is mock_email

    args = mock_send.call_args.kwargs
    assert args["sender"] == expected["sender"]
    assert args["receivers"] == expected["receivers"]
    assert args["cc"] == expected["cc"]
    assert args["bcc"] == expected["bcc"]
    assert args["subject"] == expected["subject"]
    assert args["html"] == expected["html"]


@pytest.mark.asyncio
async def test_send_with_template(
    email_service: EmailService,
    message_with_template: Tuple[EmailMessageData, dict[str, str | list[str]]],
    mocker: MockFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "dev_email", None)

    message, expected = message_with_template

    mock_sender = mocker.patch("app.services.email.service.EmailSender")
    mock_send = mock_sender.return_value.send
    mock_email = EmailMessage()
    mock_email["Subject"] = expected["subject"]
    mock_send.return_value = mock_email

    result = email_service.send(message)

    assert result is mock_email

    args = mock_send.call_args.kwargs
    assert args["sender"] == expected["sender"]
    assert args["receivers"] == expected["receivers"]
    assert args["cc"] == expected["cc"]
    assert args["bcc"] == expected["bcc"]
    assert args["subject"] == expected["subject"]
    assert expected["data_name"] in args["html"]
    assert expected["static_host"] in args["html"]


@pytest.mark.asyncio
async def test_send_raises_if_template_missing_data(
    email_service: EmailService,
    tmp_path: Path,
    mocker: MockFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "static_dir", str(tmp_path))
    monkeypatch.setattr(settings, "static_host", "https://static.example.com")
    monkeypatch.setattr(settings, "dev_email", None)

    tpl_dir = tmp_path / "email_tpl"
    tpl_dir.mkdir()
    (tpl_dir / "oops.html").write_text("Hello {name}, {static_host}")

    message = EmailMessageData(
        receivers=["to@example.com"],
        subject="Oops",
        tpl="oops",
        data=None,  # pas de data => erreur attendue
    )

    mocker.patch("app.services.email.service.EmailSender")

    with pytest.raises(ValueError, match="Either 'html' must be provided"):
        email_service.send(message)


@pytest.mark.asyncio
async def test_send_with_dev_email(
    email_service: EmailService,
    tmp_path: Path,
    mocker: MockFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "dev_email", "dev@example.com")
    monkeypatch.setattr(settings, "static_host", "https://static.example.com")
    monkeypatch.setattr(settings, "static_dir", str(tmp_path))

    tpl_dir = tmp_path / "email_tpl"
    tpl_dir.mkdir()
    (tpl_dir / "tpl.html").write_text("Hi {name}, go to {static_host}")

    expected = {
        "receivers": ["dev@example.com"],
        "cc": ["dev@example.com"],
        "bcc": ["dev@example.com"],
        "subject": "Dev Mode",
        "data_name": "Bob",
        "static_host": settings.static_host,
        "sender": settings.smtp_user,
    }

    message = EmailMessageData(
        receivers=["real@example.com"],
        subject=str(expected["subject"]),
        tpl="tpl",
        data={"name": str(expected["data_name"])},
    )

    mock_sender = mocker.patch("app.services.email.service.EmailSender")
    mock_email = EmailMessage()
    mock_email["Subject"] = expected["subject"]
    mock_sender.return_value.send.return_value = mock_email

    result = email_service.send(message)
    assert result is mock_email

    args = mock_sender.return_value.send.call_args.kwargs
    assert args["sender"] == expected["sender"]
    assert args["receivers"] == expected["receivers"]
    assert args["cc"] == expected["cc"]
    assert args["bcc"] == expected["bcc"]
    assert args["subject"] == expected["subject"]
    assert expected["data_name"] in args["html"]
    assert expected["static_host"] in args["html"]


@pytest.mark.asyncio
async def test_send_uses_real_recipients_when_dev_email_not_set(
    email_service: EmailService,
    message_with_html: Tuple[EmailMessageData, dict[str, str | list[str]]],
    mocker: MockFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "dev_email", None)

    message, expected = message_with_html

    mock_sender = mocker.patch("app.services.email.service.EmailSender")
    mock_email = EmailMessage()
    mock_email["Subject"] = expected["subject"]
    mock_sender.return_value.send.return_value = mock_email

    result = email_service.send(message)
    assert result is mock_email

    args = mock_sender.return_value.send.call_args.kwargs
    assert args["receivers"] == expected["receivers"]
    assert args["cc"] == expected["cc"]
    assert args["bcc"] == expected["bcc"]
