from datetime import date, timedelta

import pytest

from backend import timeutil
from backend.services import leads as svc
from backend.services.errors import ServiceError
from backend.tests.conftest import lead_by


def ids_in_queue(session):
    return {l["id"] for l in svc.list_today_queue(session)["leads"]}


def test_no_answer_moves_to_next_business_day_and_closes_after_three(session, user_id):
    lead = lead_by(session, "Jorge Diaz")
    r = svc.log_contact(session, lead.id, "no_response", user_id)
    assert r["lead"]["next_contact_on"] == "2026-10-01"
    assert "Back in the queue on Thursday, Oct 1" in r["message"]
    assert lead.id not in ids_in_queue(session)

    lead.next_contact_on = timeutil.today()
    svc.log_contact(session, lead.id, "no_response", user_id)
    lead.next_contact_on = timeutil.today()
    r = svc.log_contact(session, lead.id, "no_response", user_id)
    assert r["lead"]["status"] == "closed"
    assert r["lead"]["closed_reason"] == "no_response"
    assert len(r["lead"]["attempts"]) == 3


def test_next_business_day_skips_weekend():
    assert timeutil.next_business_day(date(2026, 10, 2)) == date(2026, 10, 5)  # Fri -> Mon


def test_follow_up_requires_valid_date(session, user_id):
    lead = lead_by(session, "Emily Carter")
    with pytest.raises(ServiceError, match="Pick a follow-up date between tomorrow and"):
        svc.log_contact(session, lead.id, "follow_up", user_id)
    with pytest.raises(ServiceError):
        svc.log_contact(session, lead.id, "follow_up", user_id, follow_up_on=timeutil.today())
    with pytest.raises(ServiceError):
        svc.log_contact(session, lead.id, "follow_up", user_id, follow_up_on=timeutil.today() + timedelta(days=31))
    r = svc.log_contact(session, lead.id, "follow_up", user_id, follow_up_on="2026-10-09", note="after 6 pm")
    assert r["message"] == "Saved. Emily Carter: call back on Friday, Oct 9. Removed from today's queue."
    assert r["lead"]["state_label"] == "Scheduled · back on Fri, Oct 9"
    assert lead.id not in ids_in_queue(session)


def test_interested_requires_note_and_closes_as_win(session, user_id):
    lead = lead_by(session, "Carlos Mendez")
    with pytest.raises(ServiceError, match="Add a short note"):
        svc.log_contact(session, lead.id, "interested", user_id)
    r = svc.log_contact(session, lead.id, "interested", user_id, note="Wants the evening group")
    assert r["lead"]["closed_reason"] == "interested"
    assert r["lead"]["state_label"] == "Closed · Interested"


def test_closed_lead_rejects_more_attempts(session, user_id):
    lead = lead_by(session, "Laura Torres")
    svc.log_contact(session, lead.id, "not_interested", user_id)
    with pytest.raises(ServiceError, match=r"already closed \(not interested\)"):
        svc.log_contact(session, lead.id, "no_response", user_id)


def test_wrong_number_falls_back_to_email(session, user_id):
    lead = lead_by(session, "Jorge Diaz")
    r = svc.log_contact(session, lead.id, "bad_contact", user_id)
    assert r["lead"]["status"] == "open"
    assert r["lead"]["preferred_channel"] == "email"
    assert r["lead"]["in_today_queue"] is True
    assert "email jorge.diaz@mail.com instead" in r["message"]
    assert lead.id in ids_in_queue(session)

    r = svc.log_contact(session, lead.id, "bad_contact", user_id)  # bounced
    assert r["lead"]["closed_reason"] == "unreachable"
    assert r["attempt"]["outcome_label"] == "Bounced"


def test_lead_without_phone_rejects_phone_channel(session, user_id):
    lead = lead_by(session, "Marta Ruiz")
    with pytest.raises(ServiceError, match="no valid phone number. Use email: marta.ruiz@mail.com"):
        svc.log_contact(session, lead.id, "no_response", user_id, channel="phone")
    r = svc.log_contact(session, lead.id, "no_response", user_id)
    assert r["attempt"]["channel"] == "email"
    assert r["attempt"]["outcome_label"] == "Sent, no reply"


def test_validations(session, user_id):
    lead = lead_by(session, "Ricardo Silva")
    with pytest.raises(ServiceError, match="There is no lead with id 999"):
        svc.log_contact(session, 999, "no_response", user_id)
    with pytest.raises(ServiceError, match="Invalid outcome"):
        svc.log_contact(session, lead.id, "called", user_id)
    with pytest.raises(ServiceError, match="under 280"):
        svc.log_contact(session, lead.id, "not_interested", user_id, note="x" * 281)


def test_duplicate_email_hint(session):
    lead = lead_by(session, "Ana Lopez", "certified-nursing-assistant")
    data = svc.get_lead(session, lead.id)
    assert [o["course"] for o in data["also_asked_about"]] == ["Intro to Python"]


def test_draft_course_rejects_new_leads(session):
    with pytest.raises(ServiceError, match="draft and is not accepting new leads"):
        svc.create_lead(session, "New Person", "new@mail.com", "small-business-accounting")
    lead = svc.create_lead(session, "New Person", "new@mail.com", "intro-to-python", "305-555-0000")
    assert lead["state_label"] == "New"
