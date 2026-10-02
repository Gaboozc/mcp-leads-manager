"""Leads: the inbox, the lead detail and the invented feature («Log contact»).

This module is the single place where the rules live. The Flask routes and
the MCP server only call these functions.
"""

import json
from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from backend import timeutil
from backend.models import ContactAttempt, Course, Lead
from backend.services.errors import Conflict, NotFound, ServiceError

OUTCOMES = ("no_response", "follow_up", "interested", "not_interested", "bad_contact")
CHANNELS = ("phone", "email")
MAX_NO_RESPONSE = 3
MAX_FOLLOW_UP_DAYS = 30
MAX_NOTE = 280
UNDO_MINUTES = 10

OUTCOME_LABELS = {
    "phone": {
        "no_response": "No answer",
        "follow_up": "Call back",
        "interested": "Interested",
        "not_interested": "Not interested",
        "bad_contact": "Wrong number",
    },
    "email": {
        "no_response": "Sent, no reply",
        "follow_up": "Follow up",
        "interested": "Interested",
        "not_interested": "Not interested",
        "bad_contact": "Bounced",
    },
}

CLOSED_LABELS = {
    "interested": "Interested",
    "not_interested": "Not interested",
    "no_response": f"No response after {MAX_NO_RESPONSE} tries",
    "unreachable": "Unreachable",
}


# --- Derived state -----------------------------------------------------------


def valid_channels(lead: Lead) -> list[str]:
    channels = []
    if lead.phone and not lead.phone_invalid:
        channels.append("phone")
    if lead.email and not lead.email_invalid:
        channels.append("email")
    return channels


def preferred_channel(lead: Lead) -> str | None:
    channels = valid_channels(lead)
    return channels[0] if channels else None


def _last_attempt(lead: Lead) -> ContactAttempt | None:
    return lead.attempts[-1] if lead.attempts else None


def is_due(lead: Lead, today: date) -> bool:
    return lead.status == "open" and (lead.next_contact_on is None or lead.next_contact_on <= today)


def queue_group(lead: Lead) -> str:
    """new | follow_up | retry — used for ordering and the row label."""
    last = _last_attempt(lead)
    if last is None:
        return "new"
    if last.outcome == "follow_up":
        return "follow_up"
    return "retry"


def state_label(lead: Lead, today: date) -> str:
    if lead.status == "closed":
        return f"Closed · {CLOSED_LABELS.get(lead.closed_reason, lead.closed_reason)}"
    if lead.next_contact_on and lead.next_contact_on > today:
        return f"Scheduled · back on {timeutil.fmt_short_day(lead.next_contact_on)}"
    group = queue_group(lead)
    if group == "follow_up":
        return "Follow up · promised for today" if lead.next_contact_on == today else "Follow up · overdue"
    if group == "retry":
        last = _last_attempt(lead)
        if last.outcome == "bad_contact":
            return f"Retry · {OUTCOME_LABELS[last.channel]['bad_contact'].lower()}, try {preferred_channel(lead)}"
        return f"Retry · attempt {len(lead.attempts) + 1}"
    return "New"


def _sort_key(lead: Lead):
    group = queue_group(lead)
    created = lead.created_at.timestamp()
    if group == "follow_up":
        return (0, lead.next_contact_on or date.min, 0)
    if group == "new":
        return (1, date.min, -created)
    return (2, date.min, len(lead.attempts), -created)


# --- Serialization -------------------------------------------------------------


def attempt_dict(a: ContactAttempt) -> dict:
    return {
        "id": a.id,
        "channel": a.channel,
        "outcome": a.outcome,
        "outcome_label": OUTCOME_LABELS[a.channel][a.outcome],
        "note": a.note,
        "follow_up_on": a.follow_up_on.isoformat() if a.follow_up_on else None,
        "follow_up_label": timeutil.fmt_day(a.follow_up_on) if a.follow_up_on else None,
        "created_at": a.created_at.isoformat() + "Z",
        "created_label": timeutil.fmt_datetime(a.created_at),
        "by": a.user.name if a.user else None,
    }


def _attempt_day(a: ContactAttempt) -> date:
    return timeutil.to_local(a.created_at).date()


def _last_attempt_dict(lead: Lead) -> dict | None:
    a = _last_attempt(lead)
    if a is None:
        return None
    return {
        "outcome": a.outcome,
        "outcome_label": OUTCOME_LABELS[a.channel][a.outcome],
        "channel": a.channel,
        "created_on": _attempt_day(a).isoformat(),
        "created_label": timeutil.fmt_datetime(a.created_at),
        "follow_up_label": timeutil.fmt_short_day(a.follow_up_on) if a.follow_up_on else None,
    }


def lead_summary(lead: Lead, today: date) -> dict:
    return {
        "id": lead.id,
        "name": lead.name,
        "email": lead.email,
        "phone": lead.phone,
        "phone_invalid": lead.phone_invalid,
        "email_invalid": lead.email_invalid,
        "channels": valid_channels(lead),
        "preferred_channel": preferred_channel(lead),
        "course": {
            "id": lead.course.id,
            "name": lead.course.name,
            "area": lead.course.area,
            "status": lead.course.status,
        },
        "created_at": lead.created_at.isoformat() + "Z",
        "arrived_label": timeutil.ago(lead.created_at),
        "status": lead.status,
        "closed_reason": lead.closed_reason,
        "next_contact_on": lead.next_contact_on.isoformat() if lead.next_contact_on else None,
        "in_today_queue": is_due(lead, today),
        "group": queue_group(lead),
        "attempts_count": len(lead.attempts),
        "state_label": state_label(lead, today),
        "last_attempt": _last_attempt_dict(lead),
    }


def _lead_query():
    return select(Lead).options(
        selectinload(Lead.course),
        selectinload(Lead.attempts).selectinload(ContactAttempt.user),
    )


# --- Read: inbox and detail ----------------------------------------------------------


def list_today_queue(session: Session) -> dict:
    """Today's queue, ordered by the server: follow-ups due, then new (newest
    first), then retries (fewest attempts first)."""
    today = timeutil.today()
    leads_all = session.scalars(_lead_query()).all()
    leads = [l for l in leads_all if l.status == "open"]
    due = sorted((l for l in leads if is_due(l, today)), key=_sort_key)
    upcoming = [l.next_contact_on for l in leads if l.next_contact_on and l.next_contact_on > today]
    next_return = min(upcoming) if upcoming else None
    contacted_today = sum(1 for l in leads_all if l.attempts and _attempt_day(l.attempts[-1]) == today)
    return {
        "today": today.isoformat(),
        "count": len(due),
        "contacted_today": contacted_today,
        "leads": [lead_summary(l, today) for l in due],
        "next_return_on": next_return.isoformat() if next_return else None,
        "next_return_label": timeutil.fmt_day(next_return) if next_return else None,
    }


def list_all_leads(session: Session) -> dict:
    today = timeutil.today()
    leads = session.scalars(_lead_query().order_by(Lead.created_at.desc())).all()
    return {"today": today.isoformat(), "count": len(leads), "leads": [lead_summary(l, today) for l in leads]}


def list_contacted(session: Session, date_from=None, date_to=None, by: str = "contact") -> dict:
    """Leads that were already contacted at least once (never the untouched ones).

    by="contact": filter on the day of the last attempt; by="arrival": on the
    day the lead arrived. Days are the school's days (APP_TZ). Newest contact first.
    """
    if by not in ("contact", "arrival"):
        raise ServiceError("Filter by contact or arrival date.")
    start, end = _parse_date(date_from), _parse_date(date_to)
    if (date_from and start is None) or (date_to and end is None) or (start and end and start > end):
        raise ServiceError("Pick a valid date range.")

    today = timeutil.today()
    leads = [l for l in session.scalars(_lead_query()).all() if l.attempts]

    def day(l: Lead) -> date:
        if by == "contact":
            return _attempt_day(l.attempts[-1])
        return timeutil.to_local(l.created_at).date()

    leads = [l for l in leads if (start is None or day(l) >= start) and (end is None or day(l) <= end)]
    leads.sort(key=lambda l: l.attempts[-1].created_at, reverse=True)
    return {
        "today": today.isoformat(),
        "count": len(leads),
        "leads": [lead_summary(l, today) for l in leads],
        "from": start.isoformat() if start else None,
        "to": end.isoformat() if end else None,
        "by": by,
    }


def _load(session: Session, lead_id: int) -> Lead:
    lead = session.scalars(_lead_query().where(Lead.id == lead_id)).first()
    if lead is None:
        raise NotFound(f"There is no lead with id {lead_id}.")
    return lead


def get_lead(session: Session, lead_id: int) -> dict:
    lead = _load(session, lead_id)
    today = timeutil.today()
    others = session.scalars(
        select(Lead)
        .options(selectinload(Lead.course))
        .where(func.lower(Lead.email) == lead.email.lower(), Lead.id != lead.id)
    ).all()
    data = lead_summary(lead, today)
    data["attempts"] = [attempt_dict(a) for a in reversed(lead.attempts)]  # newest first
    data["also_asked_about"] = [{"lead_id": o.id, "course": o.course.name} for o in others]
    return data


# --- Write: the invented feature ------------------------------------------------------


def _parse_date(value) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def log_contact(
    session: Session,
    lead_id: int,
    outcome: str,
    user_id: int,
    channel: str | None = None,
    note: str | None = None,
    follow_up_on=None,
) -> dict:
    """Log one contact attempt on one lead and apply the follow-up rule.

    Returns {"lead": <detail>, "attempt": <attempt>, "message": <plain summary>}.
    """
    lead = _load(session, lead_id)
    today = timeutil.today()

    if lead.status == "closed":
        reason = CLOSED_LABELS.get(lead.closed_reason, lead.closed_reason).lower()
        raise Conflict(f"This lead is already closed ({reason}). No more attempts can be logged.")

    if outcome not in OUTCOMES:
        raise ServiceError("Invalid outcome. Use: " + ", ".join(OUTCOMES) + ".")

    channel = channel or preferred_channel(lead)
    if channel not in CHANNELS:
        raise ServiceError("Invalid channel. Use: phone or email.")
    if channel not in valid_channels(lead):
        if channel == "phone":
            raise ServiceError(f"This lead has no valid phone number. Use email: {lead.email}.")
        raise ServiceError(f"This lead's email bounced. Use phone: {lead.phone}.")

    note = (note or "").strip() or None
    if note and len(note) > MAX_NOTE:
        raise ServiceError(f"Keep the note under {MAX_NOTE} characters.")

    max_day = today + timedelta(days=MAX_FOLLOW_UP_DAYS)
    when = None
    if outcome == "follow_up":
        when = _parse_date(follow_up_on)
        if when is None or when <= today or when > max_day:
            raise ServiceError(
                f"Pick a follow-up date between tomorrow and {timeutil.fmt_day(max_day)}."
            )
    if outcome == "interested" and not note:
        raise ServiceError("Add a short note: what they're interested in or what's next.")

    label = OUTCOME_LABELS[channel][outcome]
    first = lead.name
    prev_state = json.dumps(
        {
            "status": lead.status,
            "next_contact_on": lead.next_contact_on.isoformat() if lead.next_contact_on else None,
            "closed_reason": lead.closed_reason,
            "phone_invalid": lead.phone_invalid,
            "email_invalid": lead.email_invalid,
        }
    )

    if outcome == "no_response":
        tries = sum(1 for a in lead.attempts if a.outcome == "no_response") + 1
        if tries >= MAX_NO_RESPONSE:
            lead.status, lead.closed_reason, lead.next_contact_on = "closed", "no_response", None
            message = f"Saved. {first}: {label.lower()} ({tries} of {MAX_NO_RESPONSE}). Lead closed."
        else:
            when = timeutil.next_business_day(today)
            lead.next_contact_on = when
            message = (
                f"Saved. {first}: {label.lower()} ({tries} of {MAX_NO_RESPONSE}). "
                f"Back in the queue on {timeutil.fmt_day(when)}."
            )
    elif outcome == "follow_up":
        lead.next_contact_on = when
        verb = "call back" if channel == "phone" else "follow up"
        message = f"Saved. {first}: {verb} on {timeutil.fmt_day(when)}. Removed from today's queue."
    elif outcome == "interested":
        lead.status, lead.closed_reason, lead.next_contact_on = "closed", "interested", None
        message = f"Saved. {first} is interested. Lead closed as a win."
    elif outcome == "not_interested":
        lead.status, lead.closed_reason, lead.next_contact_on = "closed", "not_interested", None
        message = f"Saved. {first} is not interested. Lead closed."
    else:  # bad_contact
        if channel == "phone":
            lead.phone_invalid = True
        else:
            lead.email_invalid = True
        remaining = preferred_channel(lead)
        if remaining:
            lead.next_contact_on = None
            target = lead.email if remaining == "email" else lead.phone
            verb = "email" if remaining == "email" else "call"
            message = f"Saved. {label} for {first}. Still in today's queue — {verb} {target} instead."
        else:
            lead.status, lead.closed_reason, lead.next_contact_on = "closed", "unreachable", None
            message = f"Saved. {label} for {first}. No other way to reach them — lead closed."

    attempt = ContactAttempt(
        lead_id=lead.id,
        user_id=user_id,
        channel=channel,
        outcome=outcome,
        note=note,
        follow_up_on=when,
        created_at=timeutil.local_to_utc_naive(timeutil.now_local()),
        prev_state=prev_state,
    )
    session.add(attempt)
    session.flush()
    session.refresh(lead)
    session.refresh(attempt)

    return {"lead": get_lead(session, lead.id), "attempt": attempt_dict(attempt), "message": message}


def undo_contact(session: Session, lead_id: int, attempt_id: int) -> dict:
    """Undo the lead's last attempt: delete it and put the lead back exactly as it
    was before. Only the most recent attempt, and only for a few minutes."""
    lead = _load(session, lead_id)
    last = _last_attempt(lead)
    if last is None or last.id != attempt_id:
        raise Conflict("Only the last attempt on a lead can be undone.")
    if last.prev_state is None:
        raise Conflict("This attempt can't be undone.")
    age = timeutil.now_local() - timeutil.to_local(last.created_at)
    if age > timedelta(minutes=UNDO_MINUTES):
        raise Conflict(f"It's too late to undo this attempt (more than {UNDO_MINUTES} minutes ago).")

    prev = json.loads(last.prev_state)
    lead.status = prev["status"]
    lead.next_contact_on = date.fromisoformat(prev["next_contact_on"]) if prev["next_contact_on"] else None
    lead.closed_reason = prev["closed_reason"]
    lead.phone_invalid = prev["phone_invalid"]
    lead.email_invalid = prev["email_invalid"]
    session.delete(last)
    session.flush()
    session.expire(lead)
    return {"lead": get_lead(session, lead.id), "message": f"Undone. {lead.name} is back as before."}


# --- Intake (simulates the landing form) ------------------------------------------------


def create_lead(session: Session, name: str, email: str, course_slug: str, phone: str | None = None) -> dict:
    name, email, phone = (name or "").strip(), (email or "").strip(), (phone or "").strip() or None
    if not name or not email or "@" not in email:
        raise ServiceError("Name and a valid email are required.")
    course = session.scalars(select(Course).where(Course.slug == course_slug)).first()
    if course is None:
        raise NotFound(f"There is no course with slug '{course_slug}'.")
    if course.status != "published":
        raise Conflict(f"«{course.name}» is a draft and is not accepting new leads.")
    lead = Lead(name=name, email=email, phone=phone, course_id=course.id)
    session.add(lead)
    session.flush()
    return get_lead(session, lead.id)
