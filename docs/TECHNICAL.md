🇬🇧 English · [🇪🇸 Español](TECNICO.md)

# Technical annex

This page is for developers. For a plain explanation, read the [README](../README.md). To run the app, read [SETUP.md](../SETUP.md).

## How it is built

```
React screen (Vite) ──HTTP + JWT──► Flask routes ──┐
                                                   ├──► backend/services/leads.py ──► SQLite
AI assistant (Cursor / Claude) ──stdio──► MCP server ┘        (all the rules)
```

- **One place for the rules:** `backend/services/leads.py`. The Flask routes and the MCP server only call its functions. Same validations, same messages, same effect on the database.
- **The MCP server does not call the API over HTTP.** It imports `backend.services` and opens the same SQLite file (`DATABASE_URL`).
- **"Today" is always Miami's today** (`APP_TZ=America/New_York`), never the server clock's time zone. All date logic goes through `backend/timeutil.py`.
- **SQLite in WAL mode** so the API and the MCP server can read while the other one writes.

| Layer | Technology |
|---|---|
| API | Flask 3, Flask-JWT-Extended, flask-cors |
| Data | SQLAlchemy 2, SQLite (WAL) |
| MCP | Official Python SDK `mcp` 2.x (`MCPServer`), stdio transport |
| Screen | React 19, Vite, Tailwind CSS 4, React Router |
| Tests | pytest |

## Folders

```
backend/
  app.py              Flask app, JWT, error handling (port API_PORT, default 5050)
  config.py           Settings shared by API and MCP (env variables)
  db.py               Engine and sessions (SQLite WAL, foreign keys)
  models.py           Tables
  seed.py             Day-1 data, test user, in-place column upgrade
  timeutil.py         Today, business days, labels — always in APP_TZ
  services/leads.py   Queue, contacted list, detail, log_contact, undo_contact, intake
  services/courses.py Courses with open-lead counts
  services/users.py   Sign-in check
  routes/             Thin REST wrappers (auth, courses, leads)
  tests/              pytest
mcp_server/server.py  MCP server: list_leads, get_lead, log_contact
frontend/src/         Screens: SignIn, Inbox (tabs, rows, outcome bar, filters, panel), Courses
```

## REST API

All routes except login need `Authorization: Bearer <token>`. Errors always come back as `{"error": "<plain message>"}`.

| Method | Path | What it does |
|---|---|---|
| `POST` | `/api/auth/login` | `{email, password}` → `{token, user}` (token lasts `JWT_HOURS`, default 8) |
| `GET` | `/api/auth/me` | Current user |
| `GET` | `/api/courses` | Courses with status and open leads |
| `GET` | `/api/leads` | Today's queue, ordered, plus `contacted_today` and `next_return_label` |
| `GET` | `/api/leads?scope=contacted&from=YYYY-MM-DD&to=YYYY-MM-DD&by=contact\|arrival` | Leads with at least one attempt, filtered by last-contact day or arrival day |
| `GET` | `/api/leads/{id}` | One lead with attempts (newest first) and "also asked about" |
| `POST` | `/api/leads/{id}/contacts` | **Log contact** — `{outcome, channel?, note?, follow_up_on?}` → `{lead, attempt, message}` |
| `DELETE` | `/api/leads/{id}/contacts/{attempt_id}` | Undo the lead's last attempt (within 10 minutes) |
| `POST` | `/api/leads` | Intake that stands in for the landing form; draft courses reject new leads |

## MCP tools

| Tool | Parameters | Returns |
|---|---|---|
| `list_leads` | — | Today's queue in working order: id, name, course, contact, state, arrival |
| `get_lead` | `lead_id` | Contacts, course, state, in today's queue (yes/no), attempts, other courses for the same email |
| `log_contact` | `lead_id`, `outcome`, `channel?`, `note?`, `follow_up_on?` | Plain confirmation + the lead's new detail |

Errors are raised as `ToolError` with the same plain message the screen shows. Logs go to stderr only (stdout is the JSON-RPC channel).

## The rules of «Log contact»

| Outcome | Phone label | Email label | Needs | Effect |
|---|---|---|---|---|
| `no_response` | No answer | Sent, no reply | — | Next business day; 3rd `no_response` → closed `no_response` |
| `follow_up` | Call back | Follow up | `follow_up_on` (tomorrow … +30 days) | Stays open, comes back that day |
| `interested` | Interested | Interested | `note` | Closed `interested` (win) |
| `not_interested` | Not interested | Not interested | — | Closed `not_interested` |
| `bad_contact` | Wrong number | Bounced | — | Marks that channel invalid; another valid channel → stays open, due today; none → closed `unreachable` |

**Validations** (same for REST and MCP): lead must exist, be open, and have the chosen channel valid; outcome must be one of the five; note ≤ 280 characters.

**Today's queue:** `status = open` and (`next_contact_on` is empty or ≤ today). Order: promised follow-ups due → new leads (newest first) → retries (fewest attempts first). Leads without phone are worked by email in the same order.

**Undo:** every attempt stores `prev_state` (the lead's status, next date, close reason and channel flags before the attempt). Undo deletes the attempt and restores that state. Only the lead's last attempt, within 10 minutes.

**Intake:** a draft course rejects new leads (`«…» is a draft and is not accepting new leads.`).

## Data model

**Base (from the brief):**

- `users(id, email, name, password_hash)`
- `courses(id, name, slug UNIQUE, area, status: published|draft)`
- `leads(id, name, email, phone NULL, course_id, created_at)`

**Added by the invented feature:**

- On `leads`: `status` (open|closed), `next_contact_on`, `closed_reason` (interested|not_interested|no_response|unreachable), `phone_invalid`, `email_invalid`
- New table `contact_attempts(id, lead_id, user_id, channel, outcome, note, follow_up_on, created_at, prev_state)`

Dates are stored in UTC and shown in `APP_TZ`. Databases created before Undo get the `prev_state` column added automatically at start-up.

## Environment variables

| Variable | Used by | Default | Purpose |
|---|---|---|---|
| `DATABASE_URL` | API + MCP | `sqlite:///backend/leads.db` | Both must point to the same file |
| `APP_TZ` | API + MCP | `America/New_York` | What "today" means |
| `API_PORT` | API + screen | `5050` | Port of the API (5000 is avoided: macOS uses it) |
| `JWT_SECRET_KEY` | API | dev value | Change it in production |
| `JWT_HOURS` | API | `8` | Session length |
| `OPERATOR_EMAIL` | MCP | `operator@school.test` | Who is recorded as the author of attempts logged by the assistant |

## Tests

```bash
pytest -q backend/tests     # 34 passed
```

They cover the day-1 data, every rule and message of «Log contact», the queue order, the contacted list and its filters, undo, the API and the MCP tools (same effect on the database as the screen).

## More

- [docs/WORKFLOW.md](WORKFLOW.md) — full design notes: workflows step by step and the comparison with Close, Folk, Attio and LeadSquared.
