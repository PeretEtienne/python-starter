from email.message import EmailMessage
from pathlib import Path

from redmail.email.sender import EmailSender

from app.services.email.dto import EmailMessageData
from app.settings import settings


class EmailService:
    host: str = settings.smtp_host
    port: int = settings.smtp_port
    username: str = settings.smtp_user
    password: str = settings.smtp_password
    use_starttls: bool = True

    def __init__(self, sender: str = settings.smtp_user) -> None:
        self.sender = sender

    def send(self, message: EmailMessageData) -> EmailMessage | None:
        """Send email using the provided EmailMessageData DTO."""
        html = message.html or self._render_template(message)
        to, cc, bcc = self._resolve_recipients(
            message.receivers,
            message.cc or [],
            message.bcc or [],
        )

        email = EmailSender(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            use_starttls=self.use_starttls,
        )

        return email.send(
            sender=self.sender,
            receivers=to,
            cc=cc,
            bcc=bcc,
            subject=message.subject,
            html=html,
        )

    def _render_template(self, message: EmailMessageData) -> str:
        """Render template with provided data."""
        if not message.tpl or not message.data:
            raise ValueError(
                "Either 'html' must be provided, or both 'tpl' and 'data' must be set.",
            )

        data = message.data.copy()
        data.setdefault("static_host", settings.static_host)

        tpl_name = message.tpl.removesuffix(".html") + ".html"
        template_path = Path(settings.static_dir) / "email_tpl" / tpl_name

        with template_path.open("r") as f:
            template = f.read()

        return template.format(**data)

    def _resolve_recipients(
        self,
        to: list[str],
        cc: list[str],
        bcc: list[str],
    ) -> tuple[list[str], list[str], list[str]]:
        """Override all recipients with dev_email if defined."""
        if settings.dev_email:
            return [settings.dev_email], [settings.dev_email], [settings.dev_email]
        return to, cc, bcc
