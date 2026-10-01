const tones = {
  new: "bg-indigo-50 text-indigo-700",
  follow_up: "bg-amber-50 text-amber-800",
  retry: "bg-zinc-100 text-zinc-600",
  scheduled: "bg-sky-50 text-sky-700",
  won: "bg-emerald-50 text-emerald-700",
  closed: "bg-zinc-100 text-zinc-500",
};

export function stateTone(lead) {
  if (lead.status === "closed") return lead.closed_reason === "interested" ? "won" : "closed";
  if (!lead.in_today_queue) return "scheduled";
  return lead.group;
}

export default function StateChip({ lead }) {
  return (
    <span className={`whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-medium ${tones[stateTone(lead)]}`}>
      {lead.state_label}
    </span>
  );
}
