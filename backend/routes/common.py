from flask import g

from backend.db import new_session


def db():
    """One SQLAlchemy session per request (closed in app teardown)."""
    if "db" not in g:
        g.db = new_session()
    return g.db
