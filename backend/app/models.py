from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


def utcnow() -> datetime:
    """Naive UTC datetime (SQLite does not keep timezone info)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    monitors = relationship("Monitor", back_populates="owner", cascade="all, delete-orphan")


class Monitor(Base):
    __tablename__ = "monitors"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    name = Column(String(100), nullable=False)
    url = Column(String(2048), nullable=False)
    interval_seconds = Column(Integer, default=60, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Latest state (denormalised so the dashboard list is one cheap query)
    status = Column(String(10), default="unknown", nullable=False)  # unknown | up | down
    consecutive_failures = Column(Integer, default=0, nullable=False)
    last_checked_at = Column(DateTime, nullable=True)
    last_status_code = Column(Integer, nullable=True)
    last_response_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    owner = relationship("User", back_populates="monitors")
    results = relationship("CheckResult", back_populates="monitor", cascade="all, delete-orphan")


class CheckResult(Base):
    __tablename__ = "check_results"

    id = Column(Integer, primary_key=True)
    monitor_id = Column(Integer, ForeignKey("monitors.id"), nullable=False)
    checked_at = Column(DateTime, default=utcnow, nullable=False)
    is_up = Column(Boolean, nullable=False)
    status_code = Column(Integer, nullable=True)
    response_ms = Column(Integer, nullable=True)
    error = Column(String(255), nullable=True)

    monitor = relationship("Monitor", back_populates="results")

    __table_args__ = (Index("ix_results_monitor_time", "monitor_id", "checked_at"),)
