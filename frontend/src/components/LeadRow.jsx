import { forwardRef } from "react";
import ContactLink from "./ContactLink.jsx";
import { MailIcon, PhoneIcon } from "./Icons.jsx";
import StateChip from "./StateChip.jsx";

const LeadRow = forwardRef(function LeadRow(
  { lead, focused, leaving, channel, onFocus, onContact, onToggleChannel, onDetails, children },
  ref,
) {
  const both = lead.channels.length === 2 && lead.status === "open";
  return (
    <li
      ref={ref}
      onClick={onFocus}
      className={`group relative cursor-pointer border-b border-zinc-100 px-4 py-3 transition-[background-color,opacity,transform] duration-150 motion-reduce:transition-none sm:px-5 ${
        focused ? "bg-indigo-50/60" : "bg-white hover:bg-zinc-50"
      } ${leaving ? "translate-x-6 opacity-0" : ""}`}
    >
      {/* Focus marker: drawn with a pseudo-bar so it never shifts content. */}
      <span
        className={`absolute inset-y-0 left-0 w-0.5 transition-colors ${focused ? "bg-indigo-500" : "bg-transparent"}`}
      />
      <div className="flex items-center gap-3">
        <div className="min-w-0 flex-1">
          <p className="flex items-center gap-2 truncate">
            <span className="truncate font-medium text-zinc-900">{lead.name}</span>
            {lead.course.status === "draft" && (
              <span className="rounded bg-zinc-100 px-1.5 py-0.5 text-[11px] font-medium text-zinc-500">Draft course</span>
            )}
          </p>
          <p className="truncate text-sm text-zinc-500">
            {lead.course.name} · {lead.course.area} · {lead.arrived_label}
          </p>
        </div>

        <div className="hidden items-center gap-1 md:flex">
          <ContactLink lead={lead} channel={channel} onClick={onContact} />
          {!lead.phone && lead.status === "open" && (
            <span className="text-xs text-zinc-400">No phone</span>
          )}
          {both && (
            <button
              type="button"
              title={`Switch to ${channel === "phone" ? "email" : "phone"} (C)`}
              onClick={(e) => {
                e.stopPropagation();
                onToggleChannel();
              }}
              className="pressable rounded-md p-1.5 text-zinc-400 hover:bg-zinc-200/70 hover:text-zinc-700"
            >
              {channel === "phone" ? <MailIcon size={14} /> : <PhoneIcon size={14} />}
            </button>
          )}
        </div>

        <StateChip lead={lead} />
      </div>

      <div className="mt-1 flex items-center md:hidden">
        <ContactLink lead={lead} channel={channel} onClick={onContact} />
        {!lead.phone && <span className="ml-1 text-xs text-zinc-400">No phone</span>}
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            onDetails();
          }}
          className="pressable ml-auto rounded-lg px-2 py-1 text-sm text-zinc-500 hover:bg-zinc-100 lg:hidden"
        >
          Details
        </button>
      </div>

      {children && <div className="mt-3">{children}</div>}
    </li>
  );
});

export default LeadRow;
