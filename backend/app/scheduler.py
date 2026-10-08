import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

from apscheduler.schedulers.background import BackgroundScheduler

from .checker import run_check
from .config import settings
from .database import SessionLocal
from .models import CheckResult, Monitor, utcnow

log = logging.getLogger("uptimewatch.scheduler")
scheduler = BackgroundScheduler(timezone="UTC")


def _check_one(monitor_id: int) -> None:
    db = SessionLocal()  # each worker thread uses its own DB session
    try:
        monitor = db.get(Monitor, monitor_id)
        if monitor and monitor.is_active:
            run_check(db, monitor)
    except Exception:
        log.exception("Check failed for monitor %s", monitor_id)
    finally:
        db.close()


def tick() -> None:
    """Runs every few seconds: finds monitors that are due and checks them in parallel."""
    db = SessionLocal()
    try:
        now = utcnow()
        due_ids = [
            m.id
            for m in db.query(Monitor).filter(Monitor.is_active.is_(True)).all()
            if m.last_checked_at is None
            or (now - m.last_checked_at).total_seconds() >= m.interval_seconds
        ]
    finally:
        db.close()

    if due_ids:
        with ThreadPoolExecutor(max_workers=10) as pool:
            list(pool.map(_check_one, due_ids))


def prune_old_results() -> None:
    """Daily cron job: delete check history older than the retention period."""
    db = SessionLocal()
    try:
        cutoff = utcnow() - timedelta(days=settings.retention_days)
        deleted = db.query(CheckResult).filter(CheckResult.checked_at < cutoff).delete()
        db.commit()
        log.info("Pruned %s old check results", deleted)
    finally:
        db.close()


def start_scheduler() -> None:
    scheduler.add_job(
        tick, "interval", seconds=settings.tick_seconds, id="tick",
        max_instances=1, coalesce=True,  # never run two ticks at once
    )
    scheduler.add_job(prune_old_results, "cron", hour=3, minute=0, id="prune")
    scheduler.start()
    log.info("Scheduler started (tick every %ss)", settings.tick_seconds)


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
