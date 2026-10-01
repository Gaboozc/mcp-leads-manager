import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../api.js";
import { contactHref } from "../components/ContactLink.jsx";
import LeadPanel from "../components/LeadPanel.jsx";
import LeadRow from "../components/LeadRow.jsx";
import OutcomeBar from "../components/OutcomeBar.jsx";
import { nextBusinessDay, schoolToday } from "../lib/dates.js";
import { byId, byKey } from "../lib/outcomes.js";

const EMPTY_DRAFT = { note: "", date: "" };
const SLIDE_MS = 150;

function isTyping(el) {
  return el && (el.tagName === "INPUT" || el.tagName === "TEXTAREA" || el.isContentEditable);
}

export default function Inbox() {
  const [params, setParams] = useSearchParams();
  const view = params.get("view") === "all" ? "all" : "today";

  const [data, setData] = useState(null); // { leads, count, next_return_label }
  const [loadError, setLoadError] = useState(null);
  const [focusedId, setFocusedId] = useState(null);
  const [detail, setDetail] = useState(null);
  const [detailError, setDetailError] = useState(null);
  const [mobileDetail, setMobileDetail] = useState(false);
  const [channelOverride, setChannelOverride] = useState({});
  const [pending, setPending] = useState(null); // outcome id waiting for note/date
  const [draft, setDraft] = useState(EMPTY_DRAFT);
  const [rowError, setRowError] = useState({});
  const [leaving, setLeaving] = useState(new Set());
  const [toast, setToast] = useState(null);
  const rowRefs = useRef({});

  const leads = useMemo(() => data?.leads ?? [], [data]);
  const focused = leads.find((l) => l.id === focusedId) || null;
  const channelOf = useCallback((lead) => channelOverride[lead.id] || lead.preferred_channel, [channelOverride]);

  // --- Loading -------------------------------------------------------------------

  const load = useCallback(async () => {
    try {
      const d = await api(view === "all" ? "/leads?scope=all" : "/leads");
      setData(d);
      setLoadError(null);
      setFocusedId((cur) => (d.leads.some((l) => l.id === cur) ? cur : d.leads[0]?.id ?? null));
    } catch (e) {
      setLoadError(e.message);
    }
  }, [view]);

  useEffect(() => {
    setData(null);
    load();
  }, [load]);

  const loadDetail = useCallback(async (id) => {
    if (!id) {
      setDetail(null);
      return;
    }
    try {
      setDetailError(null);
      setDetail(await api(`/leads/${id}`));
    } catch (e) {
      setDetailError(e.message);
    }
  }, []);

  useEffect(() => {
    loadDetail(focusedId);
  }, [focusedId, loadDetail]);

  useEffect(() => {
    rowRefs.current[focusedId]?.scrollIntoView({ block: "nearest" });
  }, [focusedId]);

  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(null), 4000);
    return () => clearTimeout(t);
  }, [toast]);

  // --- Focus & channel -------------------------------------------------------------

  const focus = useCallback((id) => {
    setFocusedId(id);
    setPending(null);
    setDraft(EMPTY_DRAFT);
  }, []);

  const move = useCallback(
    (delta) => {
      if (!leads.length) return;
      const i = leads.findIndex((l) => l.id === focusedId);
      const next = leads[Math.min(leads.length - 1, Math.max(0, (i < 0 ? 0 : i) + delta))];
      focus(next.id);
    },
    [leads, focusedId, focus],
  );

  const toggleChannel = useCallback(
    (lead) => {
      if (lead.channels.length < 2) return;
      setChannelOverride((m) => ({ ...m, [lead.id]: channelOf(lead) === "phone" ? "email" : "phone" }));
      setPending(null);
    },
    [channelOf],
  );

  // --- The work: log a contact attempt ------------------------------------------------

  const submit = useCallback(
    async (lead, outcome, extra = {}) => {
      const channel = channelOf(lead);
      const index = leads.findIndex((l) => l.id === lead.id);
      const fallback = outcome === "bad_contact" && lead.channels.length === 2;
      const leavesList = view === "today" && !fallback;

      setRowError((m) => ({ ...m, [lead.id]: null }));
      setPending(null);
      setDraft(EMPTY_DRAFT);

      // Optimistic: slide the row out and focus the next one right away.
      if (leavesList) {
        const next = leads[index + 1] || leads[index - 1];
        setLeaving((s) => new Set(s).add(lead.id));
        setFocusedId(next ? next.id : null);
        setTimeout(() => {
          setData((d) => d && { ...d, leads: d.leads.filter((l) => l.id !== lead.id), count: d.count - 1 });
          setLeaving((s) => {
            const n = new Set(s);
            n.delete(lead.id);
            return n;
          });
        }, SLIDE_MS);
      }

      try {
        const res = await api(`/leads/${lead.id}/contacts`, {
          method: "POST",
          body: { outcome, channel, note: extra.note || null, follow_up_on: extra.date || null },
        });
        setToast(res.message);
        setChannelOverride((m) => ({ ...m, [lead.id]: undefined }));
        if (!leavesList) {
          setData((d) => d && { ...d, leads: d.leads.map((l) => (l.id === lead.id ? { ...l, ...res.lead } : l)) });
          if (focusedId === lead.id) setDetail(res.lead);
        }
        if (view === "today" && res.lead.in_today_queue === false && !leavesList) {
          setData((d) => d && { ...d, leads: d.leads.filter((l) => l.id !== lead.id), count: d.count - 1 });
        }
      } catch (e) {
        // Roll back: put the row where it was, with the message and what was typed.
        setData((d) => {
          if (!d || d.leads.some((l) => l.id === lead.id)) return d;
          const list = [...d.leads];
          list.splice(Math.min(index, list.length), 0, lead);
          return { ...d, leads: list, count: d.count + 1 };
        });
        setLeaving((s) => {
          const n = new Set(s);
          n.delete(lead.id);
          return n;
        });
        setFocusedId(lead.id);
        setRowError((m) => ({ ...m, [lead.id]: e.message }));
        if (byId[outcome].needs) {
          setPending(outcome);
          setDraft({ note: extra.note || "", date: extra.date || "" });
        }
      }
    },
    [channelOf, leads, view, focusedId],
  );

  const pick = useCallback(
    (lead, outcomeId) => {
      if (!lead || lead.status !== "open" || !channelOf(lead)) return;
      const o = byId[outcomeId];
      if (!o.needs) {
        submit(lead, outcomeId);
        return;
      }
      setFocusedId(lead.id);
      setPending(outcomeId);
      setRowError((m) => ({ ...m, [lead.id]: null }));
      setDraft({ note: "", date: o.needs === "date" ? nextBusinessDay(schoolToday()) : "" });
    },
    [channelOf, submit],
  );

  const submitPending = useCallback(() => {
    if (!focused || !pending) return;
    const o = byId[pending];
    if (o.needs === "note" && !draft.note.trim()) {
      setRowError((m) => ({ ...m, [focused.id]: "Add a short note: what they're interested in or what's next." }));
      return;
    }
    if (o.needs === "date" && !draft.date) {
      setRowError((m) => ({ ...m, [focused.id]: "Pick a date to follow up." }));
      return;
    }
    submit(focused, pending, draft);
  }, [focused, pending, draft, submit]);

  // --- Keyboard ---------------------------------------------------------------------------

  const keyState = useRef();
  keyState.current = { focused, move, pick, toggleChannel, channelOf, pending };

  useEffect(() => {
    function onKey(e) {
      if (e.metaKey || e.ctrlKey || e.altKey || isTyping(e.target)) return;
      const { focused, move, pick, toggleChannel, channelOf, pending } = keyState.current;
      if (e.key === "ArrowDown" || e.key === "j") {
        e.preventDefault();
        move(1);
      } else if (e.key === "ArrowUp" || e.key === "k") {
        e.preventDefault();
        move(-1);
      } else if (e.key === "Escape" && pending) {
        setPending(null);
      } else if (!focused) {
        return;
      } else if (e.key === "Enter") {
        const href = contactHref(focused, channelOf(focused));
        if (href) {
          e.preventDefault();
          window.location.href = href;
        }
      } else if (byKey[e.key]) {
        e.preventDefault();
        pick(focused, byKey[e.key].id);
      } else if (e.key === "c") {
        toggleChannel(focused);
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  // --- Render -----------------------------------------------------------------------------

  const setView = (v) => setParams(v === "all" ? { view: "all" } : {});

  return (
    <div className="flex h-full">
      <section className={`flex min-w-0 flex-1 flex-col ${mobileDetail ? "hidden lg:flex" : ""}`}>
        <div className="flex items-end justify-between gap-4 px-4 pb-3 pt-6 sm:px-5">
          <div>
            <h1 className="text-xl font-semibold">
              {view === "today" ? (data ? `${data.count} to contact today` : "Today") : "All leads"}
            </h1>
            <p className="mt-0.5 text-sm text-zinc-500">
              {view === "today" ? "Follow-ups first, then the newest leads." : "Every lead, newest first."}
            </p>
          </div>
          <div className="flex rounded-lg bg-zinc-200/70 p-0.5 text-sm">
            {[
              ["today", "Today"],
              ["all", "All"],
            ].map(([v, label]) => (
              <button
                key={v}
                onClick={() => setView(v)}
                className={`pressable rounded-md px-3 py-1 font-medium ${
                  view === v ? "bg-white text-zinc-900 shadow-sm" : "text-zinc-500 hover:text-zinc-900"
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        <div className="min-h-5 px-4 pb-2 sm:px-5" aria-live="polite">
          {toast && <p className="animate-fade-in text-sm text-emerald-700">✓ {toast}</p>}
        </div>

        <div className="min-h-0 flex-1 overflow-y-auto border-t border-zinc-200 bg-white">
          {loadError && <p className="p-6 text-sm text-rose-600">{loadError}</p>}
          {!data && !loadError && <p className="p-6 text-sm text-zinc-400">Loading…</p>}

          {data && leads.length === 0 && (
            <div className="flex flex-col items-center justify-center px-6 py-24 text-center">
              <p className="text-3xl">🎉</p>
              <p className="mt-3 font-medium">You're all caught up for today</p>
              {data.next_return_label && (
                <p className="mt-1 text-sm text-zinc-500">Next leads come back on {data.next_return_label}.</p>
              )}
            </div>
          )}

          <ul>
            {leads.map((lead) => {
              const isFocused = lead.id === focusedId;
              const canLog = lead.status === "open" && !!channelOf(lead);
              return (
                <LeadRow
                  key={lead.id}
                  ref={(el) => (rowRefs.current[lead.id] = el)}
                  lead={lead}
                  focused={isFocused}
                  leaving={leaving.has(lead.id)}
                  channel={channelOf(lead)}
                  onFocus={() => {
                    if (!isFocused) focus(lead.id);
                  }}
                  onDetails={() => {
                    if (!isFocused) focus(lead.id);
                    setMobileDetail(true);
                  }}
                  onContact={(e) => {
                    e.stopPropagation();
                    if (!isFocused) focus(lead.id);
                  }}
                  onToggleChannel={() => toggleChannel(lead)}
                >
                  {isFocused && canLog ? (
                    <OutcomeBar
                      lead={lead}
                      channel={channelOf(lead)}
                      pending={pending}
                      draft={draft}
                      error={rowError[lead.id]}
                      onPick={(o) => pick(lead, o)}
                      onDraft={setDraft}
                      onSubmit={submitPending}
                      onCancel={() => setPending(null)}
                    />
                  ) : null}
                </LeadRow>
              );
            })}
          </ul>

          {leads.length > 0 && (
            <p className="hidden px-5 py-4 text-xs text-zinc-400 md:block">
              <kbd className="font-sans">↑ ↓</kbd> move · <kbd className="font-sans">Enter</kbd> call or email ·{" "}
              <kbd className="font-sans">1–5</kbd> log outcome · <kbd className="font-sans">C</kbd> switch phone/email
            </p>
          )}
        </div>
      </section>

      <aside
        className={`min-w-0 flex-1 overflow-y-auto border-l border-zinc-200 bg-zinc-50 lg:w-[400px] lg:flex-none xl:w-[440px] ${
          mobileDetail ? "block" : "hidden lg:block"
        }`}
      >
        <LeadPanel
          lead={detail && detail.id === focusedId ? detail : null}
          loading={!!focusedId}
          error={detailError}
          onClose={() => setMobileDetail(false)}
        />
      </aside>
    </div>
  );
}
