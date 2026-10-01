"""MCP server for the leads inbox (stdio transport).

It reads and writes the same database as the Flask API by calling the same
functions in backend/services — there is no second copy of the rules.

Never print to stdout here: stdout carries the JSON-RPC stream.
"""

import logging
import sys
from pathlib import Path
from typing import Literal

# Allow `python mcp_server/server.py` from any working directory.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mcp.server.mcpserver import MCPServer  # noqa: E402
from mcp.server.mcpserver.exceptions import ToolError  # noqa: E402

from backend import config  # noqa: E402
from backend.db import session_scope  # noqa: E402
from backend.seed import seed_if_empty  # noqa: E402
from backend.services import leads as svc  # noqa: E402
from backend.services.errors import ServiceError  # noqa: E402
from backend.services.users import get_by_email  # noqa: E402

logging.basicConfig(stream=sys.stderr, level=logging.INFO, format="[leads-inbox] %(message)s")
log = logging.getLogger("leads-inbox")

mcp = MCPServer(
    "leads-inbox",
    instructions=(
        "Tools for a marketing operator working a course-leads inbox. "
        "list_leads shows today's queue in the order to work it. "
        "get_lead shows one lead with its state and attempt history. "
        "log_contact records the outcome of one call or email on one lead."
    ),
)


# --- Formatting (text the assistant reads) ------------------------------------------


def _contact(lead: dict) -> str:
    if lead["preferred_channel"] == "phone":
        return f"phone {lead['phone']}"
    if lead["preferred_channel"] == "email":
        prefix = "email only" if not lead["phone"] else "email (phone invalid)"
        return f"{prefix} ({lead['email']})"
    return "no valid contact"


def _queue_line(i: int, lead: dict) -> str:
    c = lead["course"]
    return (
        f"{i}. #{lead['id']} {lead['name']} · {c['name']} ({c['area']}) · "
        f"{_contact(lead)} · {lead['state_label']} · arrived {lead['arrived_label']}"
    )


def _format_queue(data: dict) -> str:
    if data["count"] == 0:
        tail = f" Next leads come back on {data['next_return_label']}." if data["next_return_label"] else ""
        return "No leads to contact today." + tail
    lines = [f"{data['count']} leads to contact today, in this order:"]
    lines += [_queue_line(i, lead) for i, lead in enumerate(data["leads"], 1)]
    return "\n".join(lines)


def _format_lead(lead: dict) -> str:
    c = lead["course"]
    phone = lead["phone"] or "none"
    if lead["phone"] and lead["phone_invalid"]:
        phone += " (wrong number)"
    email = lead["email"] + (" (bounced)" if lead["email_invalid"] else "")
    course = f"{c['name']} ({c['area']})" + (" — course is a draft" if c["status"] == "draft" else "")
    lines = [
        f"{lead['name']} (#{lead['id']}) — {lead['state_label']}",
        f"In today's queue: {'yes' if lead['in_today_queue'] else 'no'}",
        f"Phone: {phone} · Email: {email}",
        f"Course: {course}",
        f"Arrived: {lead['arrived_label']}",
    ]
    if lead["also_asked_about"]:
        lines.append("Also asked about: " + ", ".join(o["course"] for o in lead["also_asked_about"]))
    if lead["attempts"]:
        lines.append("Attempts (newest first):")
        for a in lead["attempts"]:
            line = f"- {a['created_label']} · {a['channel']} · {a['outcome_label']}"
            if a["follow_up_label"]:
                line += f" · next: {a['follow_up_label']}"
            if a["note"]:
                line += f' · "{a["note"]}"'
            lines.append(line)
    else:
        lines.append("Attempts: none yet")
    return "\n".join(lines)


def _run(fn):
    """Turn rule violations into plain-language tool errors."""
    try:
        return fn()
    except ServiceError as err:
        raise ToolError(err.message) from err
    except Exception as err:  # unexpected: log details to stderr, keep the message clear
        log.exception("tool failed")
        raise ToolError(f"Something went wrong reading the leads database ({config.DATABASE_URL}).") from err


# --- Tools ------------------------------------------------------------------------------


@mcp.tool()
def list_leads() -> str:
    """Today's queue of leads to contact, already ordered: promised follow-ups first,
    then new leads (newest first), then retries. Leads that were closed or scheduled
    for a later day are not included."""

    def go():
        with session_scope() as s:
            return _format_queue(svc.list_today_queue(s))

    return _run(go)


@mcp.tool()
def get_lead(lead_id: int) -> str:
    """One lead in detail: contact data, course, current state (open, scheduled or
    closed), whether it is in today's queue, and the history of contact attempts."""

    def go():
        with session_scope() as s:
            return _format_lead(svc.get_lead(s, lead_id))

    return _run(go)


@mcp.tool()
def log_contact(
    lead_id: int,
    outcome: Literal["no_response", "follow_up", "interested", "not_interested", "bad_contact"],
    channel: Literal["phone", "email"] | None = None,
    note: str | None = None,
    follow_up_on: str | None = None,
) -> str:
    """Record the outcome of one call or email on one lead — the same action as the
    outcome buttons in the inbox, with the same rules.

    outcome:
      no_response    — no answer / email with no reply. Retries next business day; closes after 3.
      follow_up      — they asked to be contacted later. Requires follow_up_on (YYYY-MM-DD, tomorrow to +30 days).
      interested     — wants to enroll or know more. Requires a short note. Closes the lead as a win.
      not_interested — declined. Closes the lead.
      bad_contact    — wrong number / bounced email. Switches to the other channel if there is one, otherwise closes.
    channel: phone or email; defaults to the lead's preferred valid channel.
    """

    def go():
        with session_scope() as s:
            user = get_by_email(s, config.OPERATOR_EMAIL)
            if user is None:
                raise ServiceError(f"No operator with email {config.OPERATOR_EMAIL}. Check OPERATOR_EMAIL.")
            result = svc.log_contact(
                s, lead_id, outcome=outcome, user_id=user.id, channel=channel, note=note, follow_up_on=follow_up_on
            )
            return result["message"] + "\n\n" + _format_lead(result["lead"])

    return _run(go)


def main():
    seed_if_empty()
    log.info("database: %s · timezone: %s", config.DATABASE_URL, config.APP_TZ)
    mcp.run("stdio")


if __name__ == "__main__":
    main()
