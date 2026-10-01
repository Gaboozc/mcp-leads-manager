from backend.tests.conftest import lead_by


def test_login_errors_are_plain(client):
    res = client.post("/api/auth/login", json={"email": "operator@school.test", "password": "nope"})
    assert res.status_code == 401
    assert res.get_json()["error"] == "Wrong email or password."


def test_endpoints_require_a_session(client):
    assert client.get("/api/leads").status_code == 401
    res = client.get("/api/leads", headers={"Authorization": "Bearer garbage"})
    assert res.get_json()["error"] == "Your session expired. Sign in again."


def test_courses(client, auth):
    courses = client.get("/api/courses", headers=auth).get_json()["courses"]
    assert {c["status"] for c in courses} == {"published", "draft"}


def test_log_contact_via_api_persists(client, auth, session):
    lead = lead_by(session, "Valeria Gomez")
    res = client.post(f"/api/leads/{lead.id}/contacts", json={"outcome": "no_response"}, headers=auth)
    assert res.status_code == 201
    queue = client.get("/api/leads", headers=auth).get_json()
    assert lead.id not in [l["id"] for l in queue["leads"]]
    detail = client.get(f"/api/leads/{lead.id}", headers=auth).get_json()
    assert detail["attempts"][0]["outcome_label"] == "No answer"


def test_api_validation_message(client, auth, session):
    lead = lead_by(session, "Valeria Gomez")
    res = client.post(f"/api/leads/{lead.id}/contacts", json={"outcome": "follow_up"}, headers=auth)
    assert res.status_code == 400
    assert res.get_json()["error"].startswith("Pick a follow-up date")
    assert client.get("/api/leads/999", headers=auth).get_json()["error"] == "There is no lead with id 999."
