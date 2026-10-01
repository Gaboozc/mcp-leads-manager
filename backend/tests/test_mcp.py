"""The MCP tools and the REST API share the rules: same messages, same DB effect."""

import pytest
from mcp.server.mcpserver.exceptions import ToolError

from backend.tests.conftest import lead_by
from mcp_server import server


def test_list_and_get(session):
    text = server.list_leads()
    assert text.startswith("15 leads to contact today")
    assert "email only (marta.ruiz@mail.com)" in text
    lead = lead_by(session, "Ana Lopez", "certified-nursing-assistant")
    detail = server.get_lead(lead.id)
    assert "Also asked about: Intro to Python" in detail
    assert "Attempts: none yet" in detail


def test_log_contact_tool_has_same_effect_as_screen(session, client, auth):
    lead = lead_by(session, "Michael Johnson")
    out = server.log_contact(lead.id, "follow_up", follow_up_on="2026-10-09", note="after work")
    assert out.startswith("Saved. Michael Johnson: call back on Friday, Oct 9.")
    assert "#%d" % lead.id not in server.list_leads()
    detail = client.get(f"/api/leads/{lead.id}", headers=auth).get_json()
    assert detail["next_contact_on"] == "2026-10-09"
    assert detail["attempts"][0]["note"] == "after work"


def test_tool_errors_are_plain_language(session):
    with pytest.raises(ToolError, match="There is no lead with id 999"):
        server.get_lead(999)
    lead = lead_by(session, "Kevin Brooks")
    with pytest.raises(ToolError, match="no valid phone number"):
        server.log_contact(lead.id, "no_response", channel="phone")
