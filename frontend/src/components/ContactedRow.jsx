import { forwardRef } from "react";
import { outcomeSummary } from "../lib/outcomes.js";

// Read-only row for the «Contacted» tab: colour bar + outcome word + both dates.
const ContactedRow = forwardRef(function ContactedRow({ lead, focused, onFocus }, ref) {
  const s = outcomeSummary(lead);
  if (!s) return null; // never contacted: belongs to «To contact», not here
  return (
    <li
      ref={ref}
      onClick={onFocus}
      className={`relative cursor-pointer border-b border-zinc-100 py-3 pl-6 pr-4 transition-colors sm:pr-5 ${
        focused ? "bg-indigo-50/60" : "bg-white hover:bg-zinc-50"
      }`}
    >
      <span className={`absolute inset-y-2 left-2 w-1 rounded-full ${s.colors.bar}`} aria-hidden />
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:gap-3">
        <div className="min-w-0 flex-1">
          <p className="truncate font-medium text-zinc-900">{lead.name}</p>
          <p className="truncate text-sm text-zinc-500">
            {lead.course.name} · {lead.course.area}
          </p>
          <p className="mt-0.5 text-xs text-zinc-400 sm:truncate">
            Arrived {lead.arrived_label} · Contacted {lead.last_attempt.created_label} by{" "}
            {lead.last_attempt.channel === "phone" ? "phone" : "email"}
          </p>
        </div>
        <span className={`self-start whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-medium sm:self-auto ${s.colors.chip}`}>
          {s.label} · {s.detail}
        </span>
      </div>
    </li>
  );
});

export default ContactedRow;
