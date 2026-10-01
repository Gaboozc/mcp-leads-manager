from datetime import datetime

import pytest

from backend import db as dbmod
from backend import timeutil

# A fixed "now": Wednesday, Sep 30 2026, 10:00 in Miami.
FIXED_NOW = datetime(2026, 9, 30, 10, 0, tzinfo=timeutil.tz())


@pytest.fixture(autouse=True)
def fixed_clock(monkeypatch):
    monkeypatch.setattr(timeutil, "now_local", lambda: FIXED_NOW)
    return FIXED_NOW


@pytest.fixture()
def database(tmp_path, monkeypatch):
    url = f"sqlite:///{tmp_path / 'test.db'}"
    dbmod.init_engine(url)
    from backend.seed import seed_if_empty

    seed_if_empty()
    yield url


@pytest.fixture()
def session(database):
    s = dbmod.new_session()
    yield s
    s.close()


@pytest.fixture()
def user_id(session):
    from backend.services.users import get_by_email
    from backend import config

    return get_by_email(session, config.TEST_USER_EMAIL).id


@pytest.fixture()
def client(database):
    from backend.app import create_app

    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


@pytest.fixture()
def token(client):
    res = client.post("/api/auth/login", json={"email": "operator@school.test", "password": "demo1234"})
    return res.get_json()["token"]


@pytest.fixture()
def auth(token):
    return {"Authorization": f"Bearer {token}"}


def lead_by(session, name, course_slug=None):
    from backend.models import Course, Lead

    q = session.query(Lead).join(Course).filter(Lead.name == name)
    if course_slug:
        q = q.filter(Course.slug == course_slug)
    return q.first()
