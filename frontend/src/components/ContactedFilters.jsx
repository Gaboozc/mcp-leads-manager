import { addDays, schoolToday } from "../lib/dates.js";

export const PRESETS = [
  ["today", "Today"],
  ["yesterday", "Yesterday"],
  ["week", "Last 7 days"],
  ["all", "All time"],
];

// Turns the filter in the URL into the from/to the API expects.
export function rangeFor(range, date) {
  const today = schoolToday();
  switch (range) {
    case "yesterday":
      return { from: addDays(today, -1), to: addDays(today, -1) };
    case "week":
      return { from: addDays(today, -6), to: today };
    case "all":
      return { from: null, to: null };
    case "date":
      return date ? { from: date, to: date } : { from: today, to: today };
    default:
      return { from: today, to: today };
  }
}

const seg = (active) =>
  `pressable rounded-md px-2.5 py-1 text-sm font-medium ${
    active ? "bg-white text-zinc-900 shadow-sm" : "text-zinc-500 hover:text-zinc-900"
  }`;

export default function ContactedFilters({ range, date, by, onChange }) {
  return (
    <div className="flex flex-wrap items-center gap-2 px-4 pb-3 sm:px-5">
      <div className="flex rounded-lg bg-zinc-200/70 p-0.5">
        {PRESETS.map(([value, label]) => (
          <button key={value} className={seg(range === value)} onClick={() => onChange({ range: value, date: null })}>
            {label}
          </button>
        ))}
      </div>
      <input
        type="date"
        aria-label="Pick a date"
        max={schoolToday()}
        value={range === "date" ? date || "" : ""}
        onChange={(e) => e.target.value && onChange({ range: "date", date: e.target.value })}
        className={`rounded-lg border px-2 py-1 text-sm outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 ${
          range === "date" ? "border-indigo-400 text-zinc-900" : "border-zinc-300 text-zinc-500"
        }`}
      />
      <div className="ml-auto flex rounded-lg bg-zinc-200/70 p-0.5" role="group" aria-label="Filter dates by">
        <button className={seg(by === "contact")} onClick={() => onChange({ by: "contact" })}>
          By contact date
        </button>
        <button className={seg(by === "arrival")} onClick={() => onChange({ by: "arrival" })}>
          By arrival date
        </button>
      </div>
    </div>
  );
}
