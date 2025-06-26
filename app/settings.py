import enum
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict
from yarl import URL


class LogLevel(str, enum.Enum):
    """Possible log levels."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class Settings(BaseSettings):
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """

    app_name: str = "app"

    host: str = "127.0.0.1"
    port: int = 8000
    # quantity of workers for uvicorn
    workers_count: int = 1
    # Enable uvicorn reloading
    reload: bool = False

    # Current environment
    environment: str = "local"
    frontend_url: str = "http://localhost:5173"

    # Logging configuration
    logger_name: str = "uvicorn.error"
    log_level: LogLevel = LogLevel.INFO

    # Variables for the database
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "api"
    db_pass: str = "api"
    db_base: str = "api"
    db_echo: bool = False

    @property
    def db_url(self) -> URL:
        """
        Assemble database URL from settings.

        :return: database URL.
        """
        return URL.build(
            scheme="postgresql+asyncpg",
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_pass,
            path=f"/{self.db_base}",
        )


    # Sentry's configuration.
    sentry_dsn: Optional[str] = None
    sentry_sample_rate: float = 1.0

    # JWT configuration
    auth_secret: str = "secret"
    auth_lifetime_seconds: int = 3600
    auth_refresh_seconds: int = 86400
    auth_reset_seconds: int = 3600
    auth_token_type: str = "bearer"

    reset_mail_link_expiracy: int = 24  # in hours

    # Secret key for the application
    secret_key: str = "my_secret_key"

    # Email configuration
    smtp_host: str = "smtp.example.com"
    smtp_port: int = 587
    smtp_user: str = "user"
    smtp_password: str = "password"
    static_host: str = "http://localhost"
    dev_email: str = "user@example.com"
    vendor_email: str = "vendor@example.com"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="API_",
        env_file_encoding="utf-8",
    )

    # Static directory
    static_dir: str = "static"


settings = Settings()

