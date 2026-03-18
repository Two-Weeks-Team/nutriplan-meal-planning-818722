from __future__ import annotations

from collections.abc import Generator
import time

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base

from config import get_database_url

Base = declarative_base()

_engine = None
_engine_url = ""


def _is_sqlite(url: str) -> bool:
    return url.startswith("sqlite")


def get_engine():
    global _engine, _engine_url
    url = get_database_url()
    if _engine is None or _engine_url != url:
        connect_args = {"check_same_thread": False} if _is_sqlite(url) else {}
        _engine = create_engine(
            url, future=True, pool_pre_ping=True, connect_args=connect_args
        )
        _engine_url = url
    return _engine


def reset_engine() -> None:
    global _engine, _engine_url
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _engine_url = ""


def init_db() -> None:
    import models  # noqa: F401

    last_error = None
    for _ in range(20):
        try:
            Base.metadata.create_all(bind=get_engine())
            return
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            reset_engine()
            time.sleep(1)
    if last_error is not None:
        raise last_error


def get_db() -> Generator[Session, None, None]:
    db = Session(get_engine())
    try:
        yield db
    finally:
        db.close()
