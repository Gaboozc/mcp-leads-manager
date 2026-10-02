"""Day-1 data: test user, 3 courses, 15 leads.

Run `python -m backend.seed --reset` to wipe and recreate the database
(dates are relative to the moment you seed, so "today" leads are today).
"""

import sys
from datetime import datetime, time, timedelta

from werkzeug.security import generate_password_hash

from sqlalchemy import inspect, text

from backend import config, timeutil
from backend.db import Base, get_engine, session_scope
from backend.models import Course, Lead, User

COURSES = [
    # name, slug, area, status
    ("Certified Nursing Assistant", "certified-nursing-assistant", "Health", "published"),
    ("Intro to Python", "intro-to-python", "Technology", "published"),
    ("Small Business Accounting", "small-business-accounting", "Business", "draft"),
]

# name, email, phone, course slug, (days ago, minutes ago within that day)
# Includes on purpose:
#   - same email in two different courses (Ana Lopez)
#   - two leads without phone (Marta Ruiz, Kevin Brooks)
#   - a lead on the draft course (Daniel Kim — arrived before it became a draft)
#   - several from today and several from last week
LEADS = [
    ("Ana Lopez", "ana.lopez@mail.com", "305-555-0142", "certified-nursing-assistant", 0, 25),
    ("Luis Perez", "luis.perez@mail.com", "786-555-0199", "intro-to-python", 0, 70),
    ("Marta Ruiz", "marta.ruiz@mail.com", None, "intro-to-python", 0, 110),
    ("Jorge Diaz", "jorge.diaz@mail.com", "305-555-0177", "certified-nursing-assistant", 0, 160),
    ("Emily Carter", "emily.carter@mail.com", "954-555-0123", "intro-to-python", 0, 230),
    ("Ana Lopez", "ana.lopez@mail.com", "305-555-0142", "intro-to-python", 1, 300),
    ("Carlos Mendez", "carlos.mendez@mail.com", "786-555-0110", "certified-nursing-assistant", 1, 540),
    ("Sofia Hernandez", "sofia.h@mail.com", "305-555-0165", "intro-to-python", 2, 200),
    ("Kevin Brooks", "kevin.brooks@mail.com", None, "certified-nursing-assistant", 3, 420),
    ("Valeria Gomez", "valeria.gomez@mail.com", "954-555-0188", "intro-to-python", 4, 150),
    ("Daniel Kim", "daniel.kim@mail.com", "786-555-0133", "small-business-accounting", 7, 300),
    ("Laura Torres", "laura.torres@mail.com", "305-555-0101", "certified-nursing-assistant", 7, 480),
    ("Michael Johnson", "m.johnson@mail.com", "786-555-0156", "intro-to-python", 8, 360),
    ("Isabel Castro", "isabel.castro@mail.com", "954-555-0170", "certified-nursing-assistant", 9, 240),
    ("Ricardo Silva", "ricardo.silva@mail.com", "305-555-0194", "intro-to-python", 9, 600),
]


def _arrival(days_ago: int, minutes_ago: int) -> datetime:
    now = timeutil.now_local()
    if days_ago == 0:
        midnight = datetime.combine(now.date(), time(0, 0), tzinfo=now.tzinfo)
        local = max(now - timedelta(minutes=minutes_ago), midnight + timedelta(minutes=minutes_ago % 50 + 1))
        local = min(local, now)
    else:
        day = now.date() - timedelta(days=days_ago)
        local = datetime.combine(day, time(19, 0), tzinfo=now.tzinfo) - timedelta(minutes=minutes_ago)
    return timeutil.local_to_utc_naive(local)


def create_schema():
    engine = get_engine()
    Base.metadata.create_all(engine)
    # Databases created before «Undo» existed lack this column: add it in place.
    columns = {c["name"] for c in inspect(engine).get_columns("contact_attempts")}
    if "prev_state" not in columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE contact_attempts ADD COLUMN prev_state TEXT"))


def seed_if_empty() -> bool:
    """Create tables and day-1 data if the database is empty. Returns True if seeded."""
    create_schema()
    with session_scope() as s:
        if s.query(User).count() > 0:
            return False
        s.add(
            User(
                email=config.TEST_USER_EMAIL,
                name=config.TEST_USER_NAME,
                password_hash=generate_password_hash(config.TEST_USER_PASSWORD),
            )
        )
        by_slug = {}
        for name, slug, area, status in COURSES:
            course = Course(name=name, slug=slug, area=area, status=status)
            s.add(course)
            by_slug[slug] = course
        s.flush()
        for name, email, phone, slug, days, minutes in LEADS:
            s.add(
                Lead(
                    name=name,
                    email=email,
                    phone=phone,
                    course_id=by_slug[slug].id,
                    created_at=_arrival(days, minutes),
                )
            )
    return True


def reset():
    Base.metadata.drop_all(get_engine())
    seed_if_empty()


if __name__ == "__main__":
    if "--reset" in sys.argv:
        reset()
        print("Database reset and seeded.", file=sys.stderr)
    elif seed_if_empty():
        print("Database seeded.", file=sys.stderr)
    else:
        print("Database already has data. Use --reset to start over.", file=sys.stderr)
