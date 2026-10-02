import { BanIcon, CheckIcon, ClockIcon, MissedIcon, XIcon } from "../components/Icons.jsx";

// Same five outcomes for phone and email; only the words change.
export const OUTCOMES = [
  {
    key: "1",
    id: "no_response",
    label: { phone: "No answer", email: "Sent, no reply" },
    icon: MissedIcon,
    tone: "bg-white text-zinc-700 ring-zinc-200 hover:bg-zinc-100",
    keyTone: "text-zinc-400",
  },
  {
    key: "2",
    id: "follow_up",
    label: { phone: "Call back", email: "Follow up" },
    icon: ClockIcon,
    tone: "bg-amber-50 text-amber-800 ring-amber-200 hover:bg-amber-100",
    keyTone: "text-amber-500",
    needs: "date",
  },
  {
    key: "3",
    id: "interested",
    label: { phone: "Interested", email: "Interested" },
    icon: CheckIcon,
    tone: "bg-emerald-50 text-emerald-800 ring-emerald-200 hover:bg-emerald-100",
    keyTone: "text-emerald-500",
    needs: "note",
  },
  {
    key: "4",
    id: "not_interested",
    label: { phone: "Not interested", email: "Not interested" },
    icon: XIcon,
    tone: "bg-rose-50 text-rose-800 ring-rose-200 hover:bg-rose-100",
    keyTone: "text-rose-400",
  },
  {
    key: "5",
    id: "bad_contact",
    label: { phone: "Wrong number", email: "Bounced" },
    icon: BanIcon,
    tone: "bg-zinc-800 text-white ring-zinc-800 hover:bg-zinc-700",
    keyTone: "text-zinc-400",
  },
];

// One colour per outcome, used for the buttons, chips, row bars and history dots,
// so the colour alone says what happened (the word is always next to it).
export const COLORS = {
  no_response: { chip: "bg-zinc-100 text-zinc-700", bar: "bg-zinc-300", dot: "bg-zinc-400" },
  follow_up: { chip: "bg-amber-50 text-amber-800", bar: "bg-amber-400", dot: "bg-amber-400" },
  interested: { chip: "bg-emerald-50 text-emerald-800", bar: "bg-emerald-500", dot: "bg-emerald-500" },
  not_interested: { chip: "bg-rose-50 text-rose-800", bar: "bg-rose-500", dot: "bg-rose-500" },
  bad_contact: { chip: "bg-zinc-800 text-white", bar: "bg-zinc-800", dot: "bg-zinc-800" },
};

// "Call back · Fri, Oct 9", "No answer · back Fri, Oct 2", "Interested · closed"…
export function outcomeSummary(lead) {
  const a = lead.last_attempt;
  if (!a) return null;
  let detail;
  if (a.outcome === "follow_up") detail = a.follow_up_label;
  else if (lead.status === "closed") {
    detail = { interested: "closed as a win", not_interested: "closed", no_response: "closed after 3 tries" }[a.outcome]
      ?? "no other contact, closed";
  } else if (a.outcome === "bad_contact") detail = `try ${lead.preferred_channel}`;
  else if (lead.next_contact_on && !lead.in_today_queue) detail = `back ${a.follow_up_label}`;
  else detail = "due today";
  return { label: a.outcome_label, detail, colors: COLORS[a.outcome] };
}

export const byKey = Object.fromEntries(OUTCOMES.map((o) => [o.key, o]));
export const byId = Object.fromEntries(OUTCOMES.map((o) => [o.id, o]));
