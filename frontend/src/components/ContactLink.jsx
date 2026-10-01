import { MailIcon, PhoneIcon } from "./Icons.jsx";

export function contactHref(lead, channel) {
  if (channel === "phone") return `tel:${lead.phone.replace(/[^\d+]/g, "")}`;
  if (channel === "email") return `mailto:${lead.email}`;
  return null;
}

export default function ContactLink({ lead, channel, onClick, large = false }) {
  if (!channel) return <span className="text-sm text-zinc-400">No valid contact</span>;
  const Icon = channel === "phone" ? PhoneIcon : MailIcon;
  const value = channel === "phone" ? lead.phone : lead.email;
  return (
    <a
      href={contactHref(lead, channel)}
      onClick={onClick}
      className={`pressable inline-flex max-w-full items-center gap-2 rounded-lg font-medium text-indigo-700 hover:bg-indigo-50 hover:text-indigo-900 ${
        large ? "px-2 py-1.5 text-lg" : "px-2 py-1 text-sm"
      }`}
    >
      <Icon size={large ? 18 : 15} className="shrink-0" />
      <span className="truncate tabular-nums">{value}</span>
    </a>
  );
}
