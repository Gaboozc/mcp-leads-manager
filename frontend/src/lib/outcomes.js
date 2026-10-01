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

export const byKey = Object.fromEntries(OUTCOMES.map((o) => [o.key, o]));
export const byId = Object.fromEntries(OUTCOMES.map((o) => [o.id, o]));
