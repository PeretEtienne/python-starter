from email.message import EmailMessage
from pathlib import Path
from typing import List, Tuple

import pytest
from pytest_mock import MockFixture

from app.services.email.dto import EmailMessageData
from app.services.email.service import EmailService
from app.settings import settings


@pytest.fixture
def email_service() -> EmailService:
    return EmailService()


@pytest.fixture
def message_with_html() -> EmailMessageData:
    return EmailMessageData(
        receivers=["to@example.com"],
        subject="Test Subject",
        html="<p>Hello</p>",
    )


@pytest.fixture
def message_with_template(tmp_path: Path, monkeypatch: "pytest.MonkeyPatch") -> EmailMessageData:
    tpl_dir = tmp_path / "email_tpl"
    tpl_dir.mkdir()
    (tpl_dir / "welcome.html").write_text("Hello {name}, see you at {static_host}")

    monkeypatch.setattr(settings, "static_dir", str(tmp_path))
    monkeypatch.setattr(settings, "static_host", "https://static.example.com")

    return EmailMessageData(
        receivers=["to@example.com"],
        subject="Welcome!",
        tpl="welcome",
        data={"name": "Alice"},
    )


@pytest.mark.asyncio
async def test_send_with_html(
    email_service: EmailService,
    message_with_html: EmailMessageData,
    mocker: MockFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "dev_email", None)

    mock_sender = mocker.patch("app.services.email.service.EmailSender")
    mock_send = mock_sender.return_value.send

    mock_email = EmailMessage()
    mock_email["Subject"] = "Test Subject"
    mock_send.return_value = mock_email

    result = email_service.send(message_with_html)

    assert result is mock_email
    mock_send.assert_called_once_with(
        sender=settings.smtp_user,
        receivers=["to@example.com"],
        cc=[],
        bcc=[],
        subject="Test Subject",
        html="<p>Hello</p>",
    )



@pytest.mark.asyncio
async def test_send_with_template(
    email_service: EmailService,
    message_with_template: EmailMessageData,
    mocker: MockFixture,
) -> None:
    mock_sender = mocker.patch("app.services.email.service.EmailSender")
    mock_send = mock_sender.return_value.send

    mock_email = EmailMessage()
    mock_email["Subject"] = "Welcome!"
    mock_email.set_content("Hello Alice, see you at https://static.example.com")

    mock_send.return_value = mock_email

    result = email_service.send(message_with_template)

    assert result is mock_email

    mock_send.assert_called_once()
    assert "Alice" in mock_send.call_args.kwargs["html"]
    assert "https://static.example.com" in mock_send.call_args.kwargs["html"]



def test_render_template_success(
    email_service: EmailService,
    message_with_template: EmailMessageData,
) -> None:
    html = email_service._render_template(message_with_template)
    assert html == "Hello Alice, see you at https://static.example.com"


def test_render_template_missing_data(
    email_service: EmailService,
) -> None:
    msg = EmailMessageData(receivers=["a"], subject="subject", tpl="test_tpl")

    with pytest.raises(ValueError, match="Either 'html' must be provided"):
        email_service._render_template(msg)


def test_resolve_recipients_normal(email_service: EmailService, monkeypatch: "pytest.MonkeyPatch") -> None:
    monkeypatch.setattr(settings, "dev_email", None)

    to: List[str] = ["to@example.com"]
    cc: List[str] = ["cc@example.com"]
    bcc: List[str] = ["bcc@example.com"]

    result: Tuple[List[str], List[str], List[str]] = email_service._resolve_recipients(to, cc, bcc)
    assert result == (to, cc, bcc)


def test_resolve_recipients_with_dev(monkeypatch: "pytest.MonkeyPatch") -> None:
    monkeypatch.setattr(settings, "dev_email", "dev@ex.com")
    service = EmailService()

    result = service._resolve_recipients(["to"], ["cc"], ["bcc"])
    assert result == (["dev@ex.com"], ["dev@ex.com"], ["dev@ex.com"])

