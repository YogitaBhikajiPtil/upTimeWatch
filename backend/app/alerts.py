import logging
import smtplib
from email.message import EmailMessage

from .config import settings

log = logging.getLogger("uptimewatch.alerts")


def send_alert(monitor_name: str, url: str, new_status: str, to_email: str) -> None:
    """Notify the owner when a monitor changes state (up <-> down)."""
    subject = f"[UptimeWatch] {monitor_name} is {new_status.upper()}"
    body = f"Monitor '{monitor_name}' ({url}) is now {new_status.upper()}."
    log.warning("ALERT -> %s | %s", to_email, subject)

    if not settings.smtp_host:
        return  # email not configured: logging only

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from
    msg["To"] = to_email
    msg.set_content(body)
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
            server.starttls()
            if settings.smtp_user:
                server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
    except Exception:  # an alert failure must never crash the checker
        log.exception("Could not send alert email")
