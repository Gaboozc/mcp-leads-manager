from collections import Counter

from backend import timeutil
from backend.models import Course, Lead


def test_seed_matches_the_brief(session):
    courses = session.query(Course).all()
    assert len(courses) == 3
    assert Counter(c.status for c in courses) == {"published": 2, "draft": 1}

    leads = session.query(Lead).all()
    assert len(leads) == 15
    emails = Counter(l.email for l in leads)
    dup = [e for e, n in emails.items() if n == 2]
    assert len(dup) == 1
    assert len({l.course_id for l in leads if l.email == dup[0]}) == 2
    assert sum(1 for l in leads if not l.phone) == 2
    assert sum(1 for l in leads if l.course.status == "draft") == 1

    today = timeutil.today()
    days = [(today - timeutil.to_local(l.created_at).date()).days for l in leads]
    assert sum(1 for d in days if d == 0) >= 3
    assert sum(1 for d in days if 7 <= d <= 13) >= 3
