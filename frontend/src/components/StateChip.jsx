import { COLORS } from "../lib/outcomes.js";

const tones = {
  new: "bg-indigo-50 text-indigo-700",
  scheduled: "bg-sky-50 text-sky-700",
  won: "bg-emerald-50 text-emerald-700",
  closed: "bg-zinc-100 text-zinc-500",
};

// Colour follows the last outcome when there is one, so the chip in the
// queue speaks the same colour language as the outcome buttons.
export function chipClass(lead) {
  if (lead.last_attempt) return COLORS[lead.last_attempt.outcome].chip;
  if (lead.status === "closed") return tones.closed;
  if (!lead.in_today_queue) return tones.scheduled;
  return tones.new;
}

export default function StateChip({ lead }) {
  return (
    <span className={`whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-medium ${chipClass(lead)}`}>
      {lead.state_label}
    </span>
  );
}
