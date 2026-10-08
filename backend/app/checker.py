import ipaddress
import logging
import socket
import time
from typing import Optional, Tuple
from urllib.parse import urlparse

import httpx
from sqlalchemy.orm import Session

from .alerts import send_alert
from .config import settings
from .models import CheckResult, Monitor, utcnow

log = logging.getLogger("uptimewatch.checker")


def validate_url(url: str) -> Optional[str]:
    """Return an error message if the URL must not be monitored, else None.

    Because the *server* makes the request, a user could otherwise point a monitor
    at internal addresses (SSRF). We only allow http(s) and public IPs by default.
    """
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return "URL must start with http:// or https://"
    try:
        infos = socket.getaddrinfo(parsed.hostname, parsed.port or 80, proto=socket.IPPROTO_TCP)
    except socket.gaierror:
        return "Could not resolve host"
    if not settings.allow_private_urls:
        for info in infos:
            ip = ipaddress.ip_address(info[4][0])
            if not ip.is_global:
                return "Private or internal addresses are not allowed"
    return None


def fetch(url: str) -> Tuple[Optional[int], Optional[int], Optional[str]]:
    """Make one HTTP request. Returns (status_code, response_ms, error)."""
    problem = validate_url(url)
    if problem:
        return None, None, problem
    start = time.perf_counter()
    try:
        with httpx.Client(timeout=settings.request_timeout, follow_redirects=False) as client:
            response = client.get(url, headers={"User-Agent": "UptimeWatch/1.0"})
        elapsed = int((time.perf_counter() - start) * 1000)
        return response.status_code, elapsed, None
    except httpx.TimeoutException:
        return None, None, "Timed out"
    except httpx.HTTPError as exc:
        return None, None, type(exc).__name__


def run_check(db: Session, monitor: Monitor) -> CheckResult:
    """Check a monitor once, store the result and alert on a state change."""
    status_code, response_ms, error = fetch(monitor.url)
    is_up = status_code is not None and status_code < 400

    result = CheckResult(
        monitor_id=monitor.id,
        is_up=is_up,
        status_code=status_code,
        response_ms=response_ms,
        error=error,
    )
    db.add(result)

    previous = monitor.status
    if is_up:
        monitor.consecutive_failures = 0
        new_status = "up"
    else:
        monitor.consecutive_failures += 1
        # Only flip to "down" after N failures in a row, to avoid false alarms
        new_status = "down" if monitor.consecutive_failures >= settings.failure_threshold else previous

    monitor.status = new_status
    monitor.last_checked_at = utcnow()
    monitor.last_status_code = status_code
    monitor.last_response_ms = response_ms
    db.commit()
    db.refresh(result)

    changed = new_status != previous and not (previous == "unknown" and new_status == "up")
    if changed:
        send_alert(monitor.name, monitor.url, new_status, monitor.owner.email)
    return result
