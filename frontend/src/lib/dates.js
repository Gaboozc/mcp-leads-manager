// "Today" is the school's today (US Eastern), not the browser's timezone.
export const SCHOOL_TZ = "America/New_York";

export function schoolToday() {
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone: SCHOOL_TZ,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date());
  return parts; // YYYY-MM-DD
}

function fromISO(iso) {
  const [y, m, d] = iso.split("-").map(Number);
  return new Date(Date.UTC(y, m - 1, d));
}

function toISO(date) {
  return date.toISOString().slice(0, 10);
}

export function addDays(iso, n) {
  const d = fromISO(iso);
  d.setUTCDate(d.getUTCDate() + n);
  return toISO(d);
}

export function nextBusinessDay(iso) {
  let next = addDays(iso, 1);
  while ([0, 6].includes(fromISO(next).getUTCDay())) next = addDays(next, 1);
  return next;
}

export function prettyDay(iso) {
  return fromISO(iso).toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric", timeZone: "UTC" });
}
