import os


def _bool(name: str, default: str) -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "on")


class Settings:
    """All configuration comes from environment variables (12-factor style)."""

    def __init__(self):
        self.secret_key = os.getenv("SECRET_KEY", "dev-secret-change-me")
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./uptimewatch.db")
        self.token_expire_minutes = int(os.getenv("TOKEN_EXPIRE_MINUTES", "1440"))

        # Scheduler
        self.scheduler_enabled = _bool("SCHEDULER_ENABLED", "1")
        self.tick_seconds = int(os.getenv("TICK_SECONDS", "15"))
        self.request_timeout = float(os.getenv("REQUEST_TIMEOUT", "10"))
        self.failure_threshold = int(os.getenv("FAILURE_THRESHOLD", "2"))
        self.retention_days = int(os.getenv("RETENTION_DAYS", "7"))

        # Security: block monitors that point at private / loopback addresses
        self.allow_private_urls = _bool("ALLOW_PRIVATE_URLS", "0")

        # Optional email alerts (if SMTP_HOST is empty, alerts are only logged)
        self.smtp_host = os.getenv("SMTP_HOST", "")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.smtp_from = os.getenv("SMTP_FROM", "alerts@uptimewatch.local")

        self.cors_origins = [
            o.strip()
            for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
            if o.strip()
        ]


settings = Settings()
