from datetime import timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..checker import run_check, validate_url
from ..database import get_db
from ..models import CheckResult, Monitor, User, utcnow
from ..schemas import MonitorCreate, MonitorOut, MonitorUpdate, ResultOut

router = APIRouter(prefix="/api/monitors", tags=["monitors"])


def _get_owned(db: Session, user: User, monitor_id: int) -> Monitor:
    monitor = (
        db.query(Monitor)
        .filter(Monitor.id == monitor_id, Monitor.user_id == user.id)
        .first()
    )
    if monitor is None:  # also hides other users' monitors (404, not 403)
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Monitor not found")
    return monitor


def _with_uptime(db: Session, monitors: List[Monitor]) -> List[MonitorOut]:
    """Attach 24h uptime % using ONE grouped query instead of one per monitor."""
    since = utcnow() - timedelta(hours=24)
    ids = [m.id for m in monitors]
    stats = {}
    if ids:
        rows = (
            db.query(
                CheckResult.monitor_id,
                func.count(CheckResult.id),
                func.sum(case((CheckResult.is_up.is_(True), 1), else_=0)),
            )
            .filter(CheckResult.monitor_id.in_(ids), CheckResult.checked_at >= since)
            .group_by(CheckResult.monitor_id)
            .all()
        )
        stats = {mid: (total, up or 0) for mid, total, up in rows}

    out = []
    for m in monitors:
        item = MonitorOut.model_validate(m)
        total, up = stats.get(m.id, (0, 0))
        item.uptime_24h = round(up / total * 100, 2) if total else None
        out.append(item)
    return out


@router.get("", response_model=List[MonitorOut])
def list_monitors(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    monitors = (
        db.query(Monitor).filter(Monitor.user_id == user.id).order_by(Monitor.created_at.desc()).all()
    )
    return _with_uptime(db, monitors)


@router.post("", response_model=MonitorOut, status_code=status.HTTP_201_CREATED)
def create_monitor(
    data: MonitorCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    problem = validate_url(data.url)
    if problem:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, problem)
    if db.query(Monitor).filter(Monitor.user_id == user.id).count() >= 20:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Monitor limit (20) reached")
    monitor = Monitor(
        user_id=user.id, name=data.name.strip(), url=data.url.strip(),
        interval_seconds=data.interval_seconds,
    )
    db.add(monitor)
    db.commit()
    db.refresh(monitor)
    return _with_uptime(db, [monitor])[0]


@router.patch("/{monitor_id}", response_model=MonitorOut)
def update_monitor(
    monitor_id: int, data: MonitorUpdate,
    db: Session = Depends(get_db), user: User = Depends(get_current_user),
):
    monitor = _get_owned(db, user, monitor_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(monitor, field, value)
    db.commit()
    db.refresh(monitor)
    return _with_uptime(db, [monitor])[0]


@router.delete("/{monitor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_monitor(
    monitor_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    db.delete(_get_owned(db, user, monitor_id))
    db.commit()


@router.get("/{monitor_id}/results", response_model=List[ResultOut])
def get_results(
    monitor_id: int, limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db), user: User = Depends(get_current_user),
):
    _get_owned(db, user, monitor_id)
    return (
        db.query(CheckResult)
        .filter(CheckResult.monitor_id == monitor_id)
        .order_by(CheckResult.checked_at.desc())
        .limit(limit)
        .all()
    )


@router.post("/{monitor_id}/check", response_model=ResultOut)
def check_now(
    monitor_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return run_check(db, _get_owned(db, user, monitor_id))
