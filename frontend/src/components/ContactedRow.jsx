import { forwardRef } from "react";
import { outcomeSummary } from "../lib/outcomes.js";

// Read-only row for the «Contacted» tab: colour bar + outcome word + both dates.
const ContactedRow = forwardRef(function ContactedRow({ lead, focused, onFocus, onUndo }, ref) {
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
        <div className="flex items-center gap-2 self-start sm:self-auto">
          <span className={`whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-medium ${s.colors.chip}`}>
            {s.label} · {s.detail}
          </span>
          {lead.last_attempt.can_undo && (
            <button
              type="button"
              title="Undo this attempt (available for 10 minutes)"
              onClick={(e) => {
                e.stopPropagation();
                onUndo(lead.id, lead.last_attempt.id);
              }}
              className="pressable rounded-md border border-zinc-300 bg-white px-2 py-0.5 text-xs font-medium text-zinc-700 hover:bg-zinc-100"
            >
              Undo
            </button>
          )}
        </div>
      </div>
    </li>
  );
});

export default ContactedRow;
