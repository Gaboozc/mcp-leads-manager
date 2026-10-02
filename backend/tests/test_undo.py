from datetime import timedelta

import pytest

from backend.services import leads as svc
from backend.services.errors import ServiceError
from backend.tests.conftest import lead_by


def test_undo_restores_the_lead_exactly(session, user_id):
    lead = lead_by(session, "Jorge Diaz")
    before = svc.get_lead(session, lead.id)
    r = svc.log_contact(session, lead.id, "bad_contact", user_id)  # wrong number -> email
    assert r["lead"]["phone_invalid"] is True

    u = svc.undo_contact(session, lead.id, r["attempt"]["id"])
    after = u["lead"]
    assert u["message"] == "Undone. Jorge Diaz is back as before."
    for key in ("status", "next_contact_on", "closed_reason", "phone_invalid", "email_invalid", "in_today_queue"):
        assert after[key] == before[key]
    assert after["attempts"] == []


def test_undo_reopens_a_closed_lead(session, user_id):
    lead = lead_by(session, "Laura Torres")
    r = svc.log_contact(session, lead.id, "not_interested", user_id)
    svc.undo_contact(session, lead.id, r["attempt"]["id"])
    assert lead.id in {l["id"] for l in svc.list_today_queue(session)["leads"]}


def test_only_last_attempt_and_only_for_a_while(session, user_id, monkeypatch, fixed_clock):
    lead = lead_by(session, "Emily Carter")
    first = svc.log_contact(session, lead.id, "no_response", user_id)
    lead.next_contact_on = None
    second = svc.log_contact(session, lead.id, "no_response", user_id)
    with pytest.raises(ServiceError, match="Only the last attempt"):
        svc.undo_contact(session, lead.id, first["attempt"]["id"])

    from backend import timeutil

    monkeypatch.setattr(timeutil, "now_local", lambda: fixed_clock + timedelta(minutes=11))
    with pytest.raises(ServiceError, match="too late to undo"):
        svc.undo_contact(session, lead.id, second["attempt"]["id"])


def test_undo_api(client, auth, session):
    lead = lead_by(session, "Valeria Gomez")
    res = client.post(f"/api/leads/{lead.id}/contacts", json={"outcome": "not_interested"}, headers=auth)
    attempt_id = res.get_json()["attempt"]["id"]
    res = client.delete(f"/api/leads/{lead.id}/contacts/{attempt_id}", headers=auth)
    assert res.status_code == 200
    assert res.get_json()["lead"]["status"] == "open"
    again = client.delete(f"/api/leads/{lead.id}/contacts/{attempt_id}", headers=auth)
    assert again.status_code == 409
