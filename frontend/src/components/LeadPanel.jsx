import ContactLink from "./ContactLink.jsx";
import { ArrowLeftIcon, MailIcon, PhoneIcon } from "./Icons.jsx";
import StateChip from "./StateChip.jsx";
import { byId } from "../lib/outcomes.js";

function Struck({ icon: Icon, value, reason }) {
  return (
    <p className="flex items-center gap-2 px-2 py-1 text-sm text-zinc-400">
      <Icon size={15} />
      <span className="line-through">{value}</span>
      <span className="text-xs">{reason}</span>
    </p>
  );
}

export default function LeadPanel({ lead, loading, error, onClose }) {
  if (error) return <div className="p-6 text-sm text-rose-600">{error}</div>;
  if (!lead) return <div className="p-6 text-sm text-zinc-400">{loading ? "Loading…" : "Select a lead to see the details."}</div>;

  return (
    <div className="animate-fade-in space-y-6 p-6">
      <div>
        <button
          onClick={onClose}
          className="pressable -ml-2 mb-3 inline-flex items-center gap-1 rounded-lg px-2 py-1 text-sm text-zinc-500 hover:bg-zinc-100 lg:hidden"
        >
          <ArrowLeftIcon size={14} /> Back
        </button>
        <div className="flex items-start justify-between gap-3">
          <h2 className="text-xl font-semibold">{lead.name}</h2>
          <StateChip lead={lead} />
        </div>
        <p className="mt-1 text-sm text-zinc-500">
          {lead.course.name} · {lead.course.area}
          {lead.course.status === "draft" && (
            <span className="ml-2 rounded bg-zinc-100 px-1.5 py-0.5 text-[11px] font-medium text-zinc-500">Draft course</span>
          )}
        </p>
      </div>

      <section className="-mx-2 space-y-0.5">
        {lead.phone && !lead.phone_invalid && <ContactLink lead={lead} channel="phone" large />}
        {lead.phone && lead.phone_invalid && <Struck icon={PhoneIcon} value={lead.phone} reason="Wrong number" />}
        {!lead.phone && (
          <p className="flex items-center gap-2 px-2 py-1 text-sm text-zinc-400">
            <PhoneIcon size={15} /> No phone — reach them by email
          </p>
        )}
        {!lead.email_invalid ? (
          <div>
            <ContactLink lead={lead} channel="email" large={!lead.phone || lead.phone_invalid} />
          </div>
        ) : (
          <Struck icon={MailIcon} value={lead.email} reason="Bounced" />
        )}
      </section>

      <dl className="grid grid-cols-[auto_1fr] gap-x-6 gap-y-2 text-sm">
        <dt className="text-zinc-500">Arrived</dt>
        <dd>{lead.arrived_label}</dd>
        {lead.also_asked_about.length > 0 && (
          <>
            <dt className="text-zinc-500">Also asked about</dt>
            <dd>{lead.also_asked_about.map((o) => o.course).join(", ")}</dd>
          </>
        )}
      </dl>

      <section>
        <h3 className="mb-3 text-sm font-medium text-zinc-500">History</h3>
        {lead.attempts.length === 0 ? (
          <p className="text-sm text-zinc-400">No attempts yet.</p>
        ) : (
          <ol className="relative space-y-4 border-l border-zinc-200 pl-4">
            {lead.attempts.map((a) => {
              const Icon = byId[a.outcome].icon;
              return (
                <li key={a.id} className="relative">
                  <span className="absolute -left-[23px] top-0.5 flex h-3.5 w-3.5 items-center justify-center rounded-full bg-white ring-1 ring-zinc-300">
                    <span className="h-1.5 w-1.5 rounded-full bg-zinc-400" />
                  </span>
                  <p className="flex items-center gap-1.5 text-sm font-medium">
                    <Icon size={14} className="text-zinc-500" />
                    {a.outcome_label}
                    <span className="font-normal text-zinc-400">
                      · {a.channel === "phone" ? "call" : "email"} · {a.created_label}
                    </span>
                  </p>
                  {a.follow_up_label && <p className="text-sm text-zinc-500">Next: {a.follow_up_label}</p>}
                  {a.note && <p className="mt-0.5 text-sm text-zinc-700">“{a.note}”</p>}
                </li>
              );
            })}
          </ol>
        )}
      </section>
    </div>
  );
}
