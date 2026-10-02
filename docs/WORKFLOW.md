# Workflow Design — Leads Inbox + «Log contact»

> Design document — **v3**. Status: **implemented** (see README for how to run it).
> v3 changes: timezone fixed to Miami (US Eastern), whole UI and MCP in English, and the feature now works on **every available contact channel** (phone *and* email) — a lead is only given up when no way to reach it is left.

---

## 0. Context

A continuing-education school gets leads from course landing pages. Every morning one marketing operator opens an internal tool at 9:00 with ~40 leads and one hour to work them. They also use an AI assistant (MCP) over the same data.

We build:
- **Part 1 (base, fixed by the brief):** login (JWT), course list, lead inbox + lead detail, Flask REST + SQLite, React UI, Python MCP over stdio with 2 read tools.
- **Part 2 (invented):** **«Log contact»** — after calling or emailing a lead, the operator logs the outcome; the server applies a follow-up rule, stores the attempt, and the lead leaves today's queue, switches channel, or closes. Same logic for the screen and a 3rd MCP tool.

Design principle from the research: **Close's execution loop + Attio/Folk's calm, zero-training UI, minus everything a single operator does not need** (dialer, routing, custom fields, enrichment).

### Global decisions
| Decision | Value |
|---|---|
| Timezone for "today" and business days | `America/New_York` (Miami, US Eastern, DST-aware). Business days = Mon–Fri; US holidays not considered |
| Language | English everywhere: UI, API errors, MCP tools and responses. README keeps the brief's required title «La funcionalidad que inventé» |
| Contact policy | **While any contact channel is valid, the lead stays workable.** No phone → work it by email. Wrong number → switch to email. Closed as unreachable only when every channel failed |

---

## 1. Actors and surfaces

| Actor | Surface | Can do |
|---|---|---|
| Operator | React app | Sign in, see courses, work the inbox, open a lead, log a contact attempt |
| Assistant (LLM in Cursor/Claude) | MCP stdio server | `list_leads`, `get_lead`, `log_contact` |
| Server | Flask + `services/` | Owns all rules. REST and MCP are thin callers of the same functions |

```
React ──HTTP/JWT──► Flask routes ──┐
                                   ├──► services/ (rules) ──► SQLite
Cursor ──stdio────► MCP server ────┘
```

---

## 2. Data model

**Base (from the brief):**
- `users(id, email, password_hash)`
- `courses(id, name, slug UNIQUE, area, status: published|draft)`
- `leads(id, name, email, phone NULL, course_id FK, created_at)`

**Added by the invented feature:**
- `leads.status` — `open | closed` (default `open`)
- `leads.next_contact_on` — DATE, NULL = due now
- `leads.closed_reason` — NULL | `interested` | `not_interested` | `no_response` | `unreachable`
- `leads.phone_invalid` — BOOL (default false), set by «Wrong number»
- `leads.email_invalid` — BOOL (default false), set by «Bounced»
- `contact_attempts(id, lead_id FK, channel: phone|email, outcome, note NULL, follow_up_on NULL, created_at, user_id FK, prev_state NULL)` — `prev_state` is the lead's state before the attempt, used by Undo

Derived (not stored): available channels, preferred channel (phone if valid, else email), attempts count, last outcome, display label (New / Retry / Follow up / Closed).

**Seed (day 1):** 3 courses (2 published, 1 draft) and 15 leads spread over today and the past week, including: same email in two courses, two leads without phone, one lead on the draft course. All seed leads start `open`, no attempts.

---

## 3. Base workflows (Part 1) — step by step

### W1. Sign in
1. Operator opens the app → sign-in screen: email, password, one button «Sign in».
2. Submit → `POST /api/auth/login`.
3. Server checks credentials → returns JWT (8 h expiry).
4. Front stores token, redirects to **Inbox**.
5. **Error:** wrong credentials → inline message under the form «Wrong email or password». Fields keep their value, no layout shift.
6. Expired/invalid token on any call → back to sign-in with «Your session expired. Sign in again.»

Test user created at startup: `operator@school.test` / `demo1234` (in README).

### W2. See courses
1. Top nav: **Inbox** · **Courses**.
2. Courses → `GET /api/courses` → table: name, area chip, status badge (Published green / Draft grey), count of open leads.
3. Read-only. Rows are not clickable (default cursor, no hover).

### W3. Work the inbox
1. Inbox → `GET /api/leads` (today's queue, ordering in §5.5).
2. Each row: name, course + area, time since arrival («2 h ago», «5 days ago»), **primary contact** (phone link, or email link with «No phone» tag), state label.
3. Row hover → subtle background; pointer cursor; clicking the name opens the detail panel on the right (list stays visible).
4. Header count: «12 to contact today».
5. **Empty state:** «You're all caught up for today 🎉» + smaller line «Next leads come back on {date}».

### W4. Open a lead
1. Click name → `GET /api/leads/{id}` → side panel:
   - Name; phone (`tel:` link, large) or «No phone»; email (`mailto:` link). An invalidated channel shows struck-through with «Wrong number» / «Bounced».
   - Course + area; draft course → badge «Draft course».
   - Arrival date.
   - Same email in other leads → «Also asked about {course}».
   - **History** of attempts («No attempts yet» when empty).
   - The «Log contact» bar (Part 2).
2. Not found → «This lead doesn't exist.»

### W5. MCP (base tools)
| Tool | Input | Returns |
|---|---|---|
| `list_leads` | — | Today's queue: id, name, course, contact channel, state, arrival — only what's needed to pick who's next |
| `get_lead` | `lead_id` | Full detail incl. state, next contact date, valid channels, attempt history, duplicate-email hint |

Plain-language errors: «There is no lead with id 99.», «Could not open the database at {path}.»

---

## 4. Industry comparison — base

| Step | Attio | Folk | Close | LeadSquared | **Ours** |
|---|---|---|---|---|---|
| Inbox view | Clean configurable tables | Simple lists | Smart Views feed the queue | Smart Views per agent, dense | One fixed "today" queue, ordered by the server. Zero configuration |
| Lead detail | Record page | Side panel | Lead page + timeline | Heavy lead page | Side panel over the list (Folk) with Close-style timeline |
| Duplicates | Dedup by email/domain | Merge suggestions | Manual | Dedup rules | Hint only («Also asked about…»). Brief leaves identity undecided |
| Draft course | n/a | n/a | n/a | Campaign status | Badge on the lead; lead still workable |

---

## 5. Invented feature — «Log contact»

### 5.1 Problem
At 9:00 with 40 leads the operator needs to answer, per lead: *did I reach them, what happened, when and how do I try again?* Without the tool they track it on paper; leads get contacted twice or forgotten — and leads without a phone are simply skipped. LeadSquared users complain disposition is slow; Folk logs notes but has no rules; Close solves it with a full dialer stack. We do Close's loop in one row, across phone **and** email.

### 5.2 The contact loop — state machine
Telephony states (dialing, active call, hang-up) are **not** detected — no softphone/SIP in scope. The operator uses `tel:` / `mailto:` and the UI waits for the outcome.

```
            ┌──────────────── Esc ─────────────────┐
            ▼                                      │
 [Queue: row focused] ──Enter / click contact──► [Contacting: row expanded, outcome bar]
            ▲                                      │ 1 · 4 · 5 (no note)     │ 2 · 3 (date / note)
            │                                      ▼                         ▼
            │                          [Saved optimistically]  ◄──Enter── [Micro-note inline]
            │                                      │
            └──── auto-advance: next row focused ◄─┘
                         │ server rejects → row slides back with the error inline
```

### 5.3 Operator workflow — step by step
1. **Queue focused.** Inbox opens with the top row focused. `↑/↓` or `J/K` move focus.
2. **One-click contact.** The row shows the lead's **preferred channel**: phone link if valid, otherwise email link. Click it (or `Enter`) → opens `tel:` or `mailto:`. The **focused row is always expanded in place** with the outcome bar, so there is no extra step between calling and logging. A small toggle (📞 / ✉️) switches channel when both are valid. `1–5` work directly on a focused row too.
3. **Outcome bar** — five flat buttons, no dropdown, colour + icon + key hint. Labels adapt to the channel; the stored outcome is the same:

   | Key | Outcome | Phone label | Email label | Extra field |
   |---|---|---|---|---|
   | `1` | `no_response` | ⚪ No answer | ⚪ Sent, no reply | — |
   | `2` | `follow_up` | 🟡 Call back | 🟡 Follow up | date (required, prefilled next business day) + note (optional) |
   | `3` | `interested` | 🟢 Interested | 🟢 Interested | note (required) |
   | `4` | `not_interested` | 🔴 Not interested | 🔴 Not interested | — |
   | `5` | `bad_contact` | ⚫ Wrong number | ⚫ Bounced | — |

4. **Conditional micro-note.** Only `2` and `3` reveal an inline field; `Enter` saves, `Esc` cancels. `1`, `4`, `5` save with one keypress.
5. **Optimistic save.** The row slides out (150 ms), the counter drops, the next row is focused — no blocking spinner. `POST /api/leads/{id}/contacts` runs in the background. The confirmation offers **Undo** (button or `Ctrl+Z`, 8 s on screen): `DELETE /api/leads/{id}/contacts/{attempt_id}` removes that attempt and restores the lead from the `prev_state` saved with it (last attempt only, within 10 minutes). The «Contacted» tab shows the same Undo on each row whose last attempt can still be undone (`last_attempt.can_undo`).
6. **Channel fallback is visible.** «Wrong number» on a lead with a valid email → the row does **not** leave the queue: it flips to the email channel with a short line «Wrong number · email {email} instead».
7. **If the server rejects**, the row slides back with the plain-language error; nothing typed is lost.
8. **No auto-dial.** Auto-advance only focuses the next lead.
9. The side panel always shows the focused lead with its full history (read-only); the outcome bar lives in the row. Two tabs with counters sit above the list: **To contact** (today's queue) and **Contacted** (every lead reached at least once; untouched leads never appear there), so any lead can be opened after it leaves today's queue. «Contacted» rows are read-only, coloured by their last outcome, show the arrival and contact dates, and can be filtered by date (Today · Yesterday · Last 7 days · All time · a specific day), by contact date or by arrival date. The confirmation after saving has a «View» link to that lead in «Contacted».
10. **Reload** → the result persists; the panel and `get_lead` show the attempt.

### 5.4 Server rules (single source of truth)

| Outcome | Required | Effect | Leaves today's queue? |
|---|---|---|---|
| `no_response` | — | 3rd `no_response` in total → `closed`, `no_response`. Otherwise `next_contact_on` = next business day | Yes |
| `follow_up` | `follow_up_on` (tomorrow … +30 days) | stays `open`, `next_contact_on` = date | Yes, returns that day |
| `interested` | `note` | `closed`, `interested` (handed to enrollment — success) | Yes |
| `not_interested` | — | `closed`, `not_interested` | Yes |
| `bad_contact` | — | marks the channel invalid (`phone_invalid` / `email_invalid`). **Another valid channel left → stays `open`, due today, preferred channel switches.** None left → `closed`, `unreachable` | Only if closed |

Every attempt creates one `contact_attempts` row (who, when, channel, outcome, note, follow-up date).

**Validations (same for REST and MCP):**
- Lead must exist → «There is no lead with id {id}.»
- Lead must be `open` → «This lead is already closed ({reason}). No more attempts can be logged.»
- Channel must be available → «This lead has no valid phone number. Use email: {email}.» / «This lead's email bounced. Use phone: {phone}.»
- Outcome must be one of five → «Invalid outcome. Use: no_response, follow_up, interested, not_interested, bad_contact.»
- `follow_up` date missing/out of range → «Pick a follow-up date between tomorrow and {date}.»
- `interested` without note → «Add a short note: what they're interested in or what's next.»
- Note ≤ 280 chars → «Keep the note under 280 characters.»

"Today" and business days computed in `America/New_York`.

### 5.5 Today's queue (inbox and `list_leads`)
In today's queue if `status = open` AND (`next_contact_on` IS NULL OR `next_contact_on` ≤ today).

Ordered by the server — the "playlist" benefit of triage without making the operator triage (§5.10):
1. **Follow up** — promised follow-ups due today/overdue.
2. **New** — never contacted, newest first (speed-to-lead).
3. **Retry** — previous no-response, fewer attempts first.

Leads without phone are **not** pushed to the bottom: they're worked by email in the same order.

### 5.6 Assistant workflow — step by step
1. «Who should I contact first?» → `list_leads` → answer from the ordered queue.
2. «I called Ana, no answer» → `log_contact(lead_id, outcome="no_response")` (channel defaults to the preferred one).
3. Tool confirms in plain language: «Saved. Ana Lopez: 1st attempt, no answer. Back in the queue on Monday, Oct 5.»
4. One lead per call, like the screen; the assistant may repeat it.
5. Errors are the same messages as §5.4.

**MCP tool contract**
```
log_contact(
  lead_id: int,
  outcome: "no_response" | "follow_up" | "interested" | "not_interested" | "bad_contact",
  channel: "phone" | "email" | None = None,   # default: preferred valid channel
  note: str | None = None,                    # required if outcome = interested
  follow_up_on: "YYYY-MM-DD" | None = None    # required if outcome = follow_up
)
```

**REST contract**
```
POST /api/leads/{id}/contacts
{ "outcome": "...", "channel": "phone|email", "note": "...", "follow_up_on": "YYYY-MM-DD" }
201 → { lead (with state), attempt }
400/404/409 → { "error": "<plain-language message>" }
```

### 5.7 Round-trip checks (README, with real assistant output)
- **A. Screen → assistant:** log «No answer» on lead X in the UI → ask «How is lead X doing?» → `get_lead` shows the attempt and return date; `list_leads` no longer includes X.
- **B. Assistant → screen:** ask the assistant to log «Call back on Friday» for lead Y → refresh → Y is gone from today; its panel shows the attempt and the date.
- **C. (channel fallback, optional)** log «Wrong number» on a lead with email → it stays in today's queue on the email channel in both UI and `get_lead`.

### 5.8 Industry comparison — the feature

| Aspect | Close | Folk | LeadSquared | Attio | **Ours** |
|---|---|---|---|---|---|
| Start contact | Click-to-call (VoIP), email in-app | Email/LinkedIn sync | Telephony add-ons | Email sync | `tel:` / `mailto:` in the row, `Enter` from keyboard |
| Log outcome | Disposition after each call | Note + reminder | Disposition form, slow per reviews | Activity/notes | 5 flat buttons, keys 1–5, same outcomes for phone and email |
| Next step | Sequences configured by admin | Manual reminder | Complex automation | Workflows (hard to set up) | Fixed server rules: retry, close after 3, required follow-up date |
| Unreachable channel | Manual | Manual | Rules | Manual | Automatic fallback to the remaining channel |
| Next lead | Auto-dial | — | — | — | Next row focused, optimistic save, no auto-dial |
| AI access | API | AI follow-up assistant | — | AI-native attributes | Same rules via one MCP tool |
| Setup | Admin | Low | High | Medium–high | None |

### 5.9 What we took from the proposed «Quick Call Disposition» flow

| Proposal | Decision | Why |
|---|---|---|
| Clickable phone in the row | **Adopt + extend** | Also `mailto:` when there's no valid phone |
| Inline reveal, no modals | **Adopt** | Brief: one job inside the inbox |
| Flat colour-coded buttons, no dropdowns | **Adopt** | One click / one key |
| Keys `1–4` | **Adapt → `1–5`** | Added «Not interested»: a declined lead needs an honest outcome |
| Conditional micro-note | **Adopt** | Only for «Call back/Follow up» (optional) and «Interested» (required) |
| Auto-advance | **Adopt** (focus only) | The speed multiplier |
| Auto-dial in 3 s | **Reject** | No telephony; repeatedly opening `tel:` hijacks the OS dialer |
| Dialing / active / hang-up states via SIP | **Reject** | No softphone; the row's "contacting" state replaces them |
| Optimistic UI | **Adopt with rollback** | Server validations are mandatory; client pre-checks make rollback rare |
| 🔴 for No answer | **Adapt** | Red = «Not interested»; «No answer» is neutral grey |

### 5.10 Alternative considered (README): Morning Lead Triage
The Superhuman-style triage (separate «Needs Triage» view, keys into High / Standard / Nurture / Trash, «Start Dialing» into an Execution Queue, priorities batched at the end) was **rejected**:

| Triage element | Conflict with the brief |
|---|---|
| Separate view → «Start Dialing» → Execution Queue | «Se termina sin abrir otra sección… nada de varias pantallas o un pipeline aparte» |
| Priority buckets reorder the queue | Main effect is ordering; a single tag change «no cuenta» |
| Batched payload at session end | Each step must persist; MCP tool works one lead at a time with the same DB effect |
| Nurture → automated email sequence | New subsystem, out of scope |
| Next.js + Supabase | Brief fixes Flask + SQL + React |
| Hides contact info during triage | The operator needs the contact to act |

Kept from it: **no strategic decisions during the working block** — the server orders the queue (§5.5). Also considered **merging duplicate emails** — rejected, the brief leaves identity undecided.

---

## 6. UI rules (everywhere)

- **Layout:** top nav (Inbox · Courses · Sign out) → list left (≈60%), detail panel right. Mobile: panel full screen.
- **Hierarchy:** one primary action per region; outcome buttons each with own colour/icon — never identical buttons.
- **Keyboard:** `↑/↓` or `J/K` focus · `Enter` contact · `1–5` outcome · `Enter` save note · `Esc` cancel · `C` toggles 📞/✉️ (Tab is left for normal focus navigation). Key hints as faded badges.
- **Outcome colours** are one system: the same colour per outcome on the buttons, the row chips, the left bar of «Contacted» rows and the history dots — grey no answer · amber call back/follow up · green interested · rose not interested · black wrong number/bounced. The word always accompanies the colour.
- **No dropdowns** in the loop. **No blocking spinners**: optimistic update, rollback on error.
- **Motion:** row slide-out 150 ms; respects `prefers-reduced-motion`.
- **Cursors:** `pointer` on clickable; `not-allowed` on disabled controls (closed lead, invalid channel toggle); `default` on non-actionable rows; `text` in inputs.
- **Hover/press:** shade change + `scale(.98)` on press — no layout shift.
- **States on screen:** empty inbox, sign-in error, «No phone», invalid channel struck-through, draft-course badge, closed lead, rejected save, server error.
- **Copy:** plain operator English (contact, call back, closed). No ids, enums or technical terms on screen.
- Stack: Vite + React + Tailwind, hand-built components.

---

## 7. Repository layout (implementation target)

```
backend/
  app.py             Flask factory, CORS, JWT
  models.py          SQLAlchemy models (§2)
  seed.py            day-1 data + test user
  services/leads.py  list_today_queue, get_lead, log_contact (§5.4)
  routes/            auth.py, courses.py, leads.py — thin wrappers
  tests/             pytest: rules, validations, queue order, channel fallback
mcp_server/server.py FastMCP stdio; imports backend.services
frontend/            Vite React: SignIn, Inbox (+LeadRow, LeadPanel, OutcomeBar), Courses
docs/WORKFLOW.md     this document
README.md            Base setup · MCP in Cursor · «La funcionalidad que inventé» · data model · out of scope
```

## 8. Out of scope (stated in README)
- Base: no public site, no user management (single seeded operator), no lead-creation UI.
- Feature: undo limited to the lead's last attempt and 10 minutes, UI only (no MCP tool — the brief allows one third tool); no real telephony or email sending (we only open `tel:`/`mailto:`), no auto-dial, no triage step, no US-holiday calendar.

## 9. Verification
- `pytest backend/tests` — each rule in §5.4 (incl. channel fallback and `unreachable`), every validation message, queue order §5.5, timezone edge (23:30 ET), MCP tool and REST route producing identical DB effect.
- Manual: run Flask + Vite, sign in, work the queue only with the keyboard, reload → persisted; force a rejection → row rolls back.
- MCP Inspector / Cursor: checks A, B (and C) from §5.7; paste real responses into README.

## 10. Decisions log
- Timezone: `America/New_York` ✔
- Language: English ✔
- Leads without phone: worked by email, same queue ✔ — and «Wrong number»/«Bounced» fall back to the remaining channel ✔
- «Interested» vs «Call back» split ✔

---

## 12. MCP connection

### 12.1 How it runs
The MCP server is a Python process **launched by the client** (Cursor, Claude Desktop, MCP Inspector). Transport is **stdio**: JSON-RPC over stdin/stdout. No port, no HTTP, no OAuth.

```
Cursor ──launches──► .venv/bin/python mcp_server/server.py
   ▲                          │
   └── JSON-RPC stdin/stdout ─┤
                              ▼
                 backend/services/leads.py   (same functions Flask routes call)
                              ▼
                 SQLite file (same DATABASE_URL as Flask)
```

1. Client reads its config and starts the process.
2. Handshake: server announces its 3 tools (name, description, parameter schema).
3. The model picks a tool → client invokes it → server runs the service function → returns plain text.
4. Client closes → process exits.

The MCP **never calls the Flask API and keeps no copy of the data**; it imports `backend.services` directly.

| MCP tool | Service function | REST equivalent |
|---|---|---|
| `list_leads` | `list_today_queue()` | `GET /api/leads` |
| `get_lead` | `get_lead(id)` | `GET /api/leads/{id}` |
| `log_contact` | `log_contact(...)` | `POST /api/leads/{id}/contacts` |

### 12.2 Client configuration (README)
Cursor — `.cursor/mcp.json` (or global `~/.cursor/mcp.json`):
```json
{
  "mcpServers": {
    "leads-inbox": {
      "command": "/ABS/PATH/mcp-leads-manager/.venv/bin/python",
      "args": ["/ABS/PATH/mcp-leads-manager/mcp_server/server.py"],
      "env": {
        "DATABASE_URL": "sqlite:////ABS/PATH/mcp-leads-manager/backend/leads.db",
        "OPERATOR_EMAIL": "operator@school.test",
        "APP_TZ": "America/New_York"
      }
    }
  }
}
```
Cursor → Settings → MCP → «leads-inbox» green with 3 tools. Claude Desktop: same block in `claude_desktop_config.json`. Manual test: `npx @modelcontextprotocol/inspector .venv/bin/python mcp_server/server.py`.

### 12.3 Shared environment variables
| Variable | Used by | Purpose |
|---|---|---|
| `DATABASE_URL` | Flask + MCP | Same SQLite file (absolute path) |
| `APP_TZ` | Flask + MCP | Same "today" and business days (`America/New_York`) |
| `OPERATOR_EMAIL` | MCP only | No JWT over stdio → resolves to the seeded user, stored as `contact_attempts.user_id` |

### 12.4 Response examples
`list_leads()`
```
8 leads to contact today:
1. #4 Ana Lopez · Basic Nursing (Health) · phone 305-555-0142 · Follow up (promised today)
2. #12 Luis Perez · Intro to Python (Technology) · phone 786-555-0199 · New · 2 h ago
…
8. #7 Marta Ruiz · Intro to Python (Technology) · email only (marta@mail.com) · New · 3 days ago
```

`get_lead(4)`
```
Ana Lopez (#4) — Open · back on Mon, Oct 5
Phone: 305-555-0142 · Email: ana@mail.com
Course: Basic Nursing (Health)
Also asked about: Clinic Management
Attempts:
- Oct 1, 9:12 AM · phone · Call back · "prefers after 6 pm"
```

`log_contact(12, "follow_up", follow_up_on="2026-10-09")`
```
Saved. Luis Perez: call back on Friday, Oct 9. Removed from today's queue.
```

`log_contact(5, "bad_contact")` with email available
```
Saved. Wrong number for Jorge Diaz. Still in today's queue — email jorge@mail.com instead.
```

Error (tool text, never a stack trace)
```
This lead is already closed (not interested). No more attempts can be logged.
```

Response rules: only what the assistant needs; ids shown once (`#4`) so it can chain calls; dates in words, Eastern time; no internal enums or raw timestamps.

### 12.5 Known pitfalls
| Pitfall | Cause | Prevention |
|---|---|---|
| Client marks server red / hangs | `print()` or logs on **stdout** corrupt JSON-RPC | All logging to **stderr**; no `print` |
| «no such table» | Process started from another working dir | Absolute paths; shared `DATABASE_URL` |
| `ModuleNotFoundError` | `command: "python"` picks system interpreter | Point to the project `.venv` Python |
| «database is locked» | Flask and MCP write concurrently | SQLite WAL + short transactions |
| Empty DB on first run | Seed never executed | Server creates tables and seeds if empty (same routine as Flask) |
| «Internal error» in assistant | Unhandled exception | Every tool catches domain errors and returns the §5.4 message |
| Wrong "today" | Server machine in UTC | All date logic uses `APP_TZ`, never the system clock's zone |
