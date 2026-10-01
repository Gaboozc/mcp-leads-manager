import { useEffect, useRef } from "react";
import { addDays, schoolToday } from "../lib/dates.js";
import { byId, OUTCOMES } from "../lib/outcomes.js";

export default function OutcomeBar({ lead, channel, pending, draft, error, onPick, onDraft, onSubmit, onCancel }) {
  const noteRef = useRef(null);
  const active = pending ? byId[pending] : null;
  const today = schoolToday();

  useEffect(() => {
    if (active) noteRef.current?.focus();
  }, [active]);

  function onKey(e) {
    if (e.key === "Escape") {
      e.preventDefault();
      onCancel();
    } else if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSubmit();
    }
  }

  return (
    <div className="animate-fade-in space-y-2" onClick={(e) => e.stopPropagation()}>
      <div className="flex flex-wrap gap-1">
        {OUTCOMES.map((o) => {
          const Icon = o.icon;
          const selected = pending === o.id;
          return (
            <button
              key={o.id}
              type="button"
              onClick={() => onPick(o.id)}
              className={`pressable inline-flex items-center gap-1.5 whitespace-nowrap rounded-lg px-2 py-1.5 text-[13px] font-medium ring-1 ${o.tone} ${
                selected ? "ring-2 ring-offset-1 ring-offset-white" : ""
              }`}
            >
              <Icon size={14} />
              {o.label[channel]}
              <kbd className={`ml-0.5 font-sans text-[11px] font-semibold ${o.keyTone}`}>{o.key}</kbd>
            </button>
          );
        })}
      </div>

      {active && (
        <form
          className="animate-fade-in flex flex-wrap items-center gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            onSubmit();
          }}
        >
          {active.needs === "date" && (
            <label className="flex items-center gap-2 text-sm text-zinc-600">
              <span>{channel === "phone" ? "Call back on" : "Follow up on"}</span>
              <input
                type="date"
                required
                min={addDays(today, 1)}
                max={addDays(today, 30)}
                value={draft.date}
                onChange={(e) => onDraft({ ...draft, date: e.target.value })}
                onKeyDown={onKey}
                className="rounded-lg border border-zinc-300 px-2 py-1.5 text-sm outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
              />
            </label>
          )}
          <input
            ref={noteRef}
            type="text"
            maxLength={280}
            required={active.needs === "note"}
            placeholder={active.needs === "note" ? "What are they interested in? (required)" : "Note (optional)"}
            value={draft.note}
            onChange={(e) => onDraft({ ...draft, note: e.target.value })}
            onKeyDown={onKey}
            className="min-w-48 flex-1 rounded-lg border border-zinc-300 px-3 py-1.5 text-sm outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
          />
          <button
            type="submit"
            className="pressable rounded-lg bg-zinc-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-zinc-700"
          >
            Save <span className="ml-1 text-xs text-zinc-400">↵</span>
          </button>
          <button
            type="button"
            onClick={onCancel}
            className="pressable rounded-lg px-2 py-1.5 text-sm text-zinc-500 hover:bg-zinc-100"
          >
            Cancel <span className="ml-1 text-xs text-zinc-400">Esc</span>
          </button>
        </form>
      )}

      {error && (
        <p role="alert" className="animate-fade-in text-sm text-rose-600">
          {error}
        </p>
      )}
    </div>
  );
}
