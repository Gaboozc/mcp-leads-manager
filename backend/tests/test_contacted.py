from datetime import timedelta

import pytest

from backend import timeutil
from backend.models import ContactAttempt
from backend.services import leads as svc
from backend.services.errors import ServiceError
from backend.tests.conftest import lead_by


def test_only_contacted_leads_newest_contact_first(session, user_id):
    assert svc.list_contacted(session)["count"] == 0
    first = lead_by(session, "Jorge Diaz")
    second = lead_by(session, "Laura Torres")
    svc.log_contact(session, first.id, "no_response", user_id)
    svc.log_contact(session, second.id, "not_interested", user_id)
    # Make the order deterministic: Laura contacted a minute later.
    second.attempts[-1].created_at = first.attempts[-1].created_at + timedelta(minutes=1)
    session.flush()

    data = svc.list_contacted(session)
    assert [l["name"] for l in data["leads"]] == ["Laura Torres", "Jorge Diaz"]
    assert data["leads"][0]["last_attempt"]["outcome"] == "not_interested"
    assert data["leads"][1]["last_attempt"]["outcome_label"] == "No answer"


def test_filter_by_contact_date(session, user_id):
    today = timeutil.today()
    lead = lead_by(session, "Jorge Diaz")
    svc.log_contact(session, lead.id, "no_response", user_id)
    lead.attempts[-1].created_at -= timedelta(days=2)
    session.flush()

    assert svc.list_contacted(session, today, today)["count"] == 0
    two_days_ago = today - timedelta(days=2)
    assert svc.list_contacted(session, two_days_ago, two_days_ago)["count"] == 1


def test_filter_by_arrival_date(session, user_id):
    lead = lead_by(session, "Isabel Castro")  # arrived 9 days ago
    svc.log_contact(session, lead.id, "not_interested", user_id)
    arrived = timeutil.to_local(lead.created_at).date()
    today = timeutil.today()
    assert svc.list_contacted(session, today, today, by="arrival")["count"] == 0
    assert svc.list_contacted(session, arrived, arrived, by="arrival")["count"] == 1
    assert svc.list_contacted(session, today, today, by="contact")["count"] == 1


def test_invalid_range(session):
    with pytest.raises(ServiceError, match="Pick a valid date range"):
        svc.list_contacted(session, "2026-10-05", "2026-10-01")
    with pytest.raises(ServiceError, match="Pick a valid date range"):
        svc.list_contacted(session, "yesterday")


def test_queue_reports_contacted_today(session, user_id):
    assert svc.list_today_queue(session)["contacted_today"] == 0
    svc.log_contact(session, lead_by(session, "Jorge Diaz").id, "no_response", user_id)
    assert svc.list_today_queue(session)["contacted_today"] == 1


def test_contacted_api(client, auth, session, user_id):
    lead = lead_by(session, "Valeria Gomez")
    client.post(f"/api/leads/{lead.id}/contacts", json={"outcome": "no_response"}, headers=auth)
    today = timeutil.today().isoformat()
    res = client.get(f"/api/leads?scope=contacted&from={today}&to={today}", headers=auth)
    assert [l["name"] for l in res.get_json()["leads"]] == ["Valeria Gomez"]
    bad = client.get("/api/leads?scope=contacted&from=nope", headers=auth)
    assert bad.status_code == 400 and bad.get_json()["error"] == "Pick a valid date range."
