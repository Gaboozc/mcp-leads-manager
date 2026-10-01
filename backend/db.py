from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from backend import config


class Base(DeclarativeBase):
    pass


_engine = None
_Session = None


def _configure_sqlite(dbapi_conn, _record):
    cur = dbapi_conn.cursor()
    # WAL lets the API and the MCP server read while the other one writes.
    cur.execute("PRAGMA journal_mode=WAL")
    cur.execute("PRAGMA foreign_keys=ON")
    cur.execute("PRAGMA busy_timeout=5000")
    cur.close()


def init_engine(url: str | None = None):
    """(Re)create the engine. Tests call this with a temporary database."""
    global _engine, _Session
    url = url or config.DATABASE_URL
    _engine = create_engine(url, future=True)
    if url.startswith("sqlite"):
        event.listen(_engine, "connect", _configure_sqlite)
    _Session = sessionmaker(bind=_engine, expire_on_commit=False, future=True)
    return _engine


def get_engine():
    if _engine is None:
        init_engine()
    return _engine


def new_session():
    if _Session is None:
        init_engine()
    return _Session()


@contextmanager
def session_scope():
    session = new_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
