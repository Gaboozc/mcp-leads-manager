from datetime import timedelta

from backend import timeutil
from backend.services import leads as svc
from backend.tests.conftest import lead_by


def test_queue_starts_with_every_open_lead_newest_first(session):
    q = svc.list_today_queue(session)
    assert q["count"] == 15
    created = [l["created_at"] for l in q["leads"]]
    assert created == sorted(created, reverse=True)
    assert all(l["state_label"] == "New" for l in q["leads"])


def test_leads_without_phone_are_worked_by_email(session):
    q = svc.list_today_queue(session)
    marta = next(l for l in q["leads"] if l["name"] == "Marta Ruiz")
    assert marta["preferred_channel"] == "email"
    assert marta["channels"] == ["email"]


def test_order_follow_up_then_new_then_retry(session, user_id):
    today = timeutil.today()
    retry = lead_by(session, "Luis Perez")
    follow = lead_by(session, "Isabel Castro")
    svc.log_contact(session, retry.id, "no_response", user_id)
    svc.log_contact(session, follow.id, "follow_up", user_id, follow_up_on=today + timedelta(days=1))
    # Move both to "due today" as if days had passed.
    retry.next_contact_on = today
    follow.next_contact_on = today
    session.flush()

    q = svc.list_today_queue(session)
    names = [l["name"] for l in q["leads"]]
    assert names[0] == "Isabel Castro"
    assert names[-1] == "Luis Perez"
    assert q["leads"][0]["state_label"] == "Follow up · promised for today"
    assert q["leads"][-1]["state_label"] == "Retry · attempt 2"


def test_empty_queue_reports_next_return(session, user_id):
    for lead in svc.list_today_queue(session)["leads"]:
        if lead["preferred_channel"]:
            svc.log_contact(session, lead["id"], "no_response", user_id)
    q = svc.list_today_queue(session)
    assert q["count"] == 0
    assert q["next_return_label"] == "Thursday, Oct 1"
