import { useEffect, useState } from "react";
import { api } from "../api.js";

export default function Courses() {
  const [courses, setCourses] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api("/courses")
      .then((d) => setCourses(d.courses))
      .catch((e) => setError(e.message));
  }, []);

  return (
    <main className="mx-auto h-full max-w-3xl overflow-y-auto px-4 py-8 sm:px-6">
      <h1 className="text-xl font-semibold">Courses</h1>
      <p className="mt-1 text-sm text-zinc-500">Draft courses don't take new leads, but keep the ones they already had.</p>

      {error && <p className="mt-6 text-sm text-rose-600">{error}</p>}
      {!courses && !error && <p className="mt-6 text-sm text-zinc-400">Loading…</p>}

      {courses && (
        <ul className="mt-6 divide-y divide-zinc-100 overflow-hidden rounded-2xl bg-white ring-1 ring-zinc-200">
          {courses.map((c) => (
            <li key={c.id} className="flex cursor-default items-center gap-4 px-5 py-4">
              <div className="min-w-0 flex-1">
                <p className="truncate font-medium">{c.name}</p>
                <p className="text-sm text-zinc-500">
                  {c.area} · <span className="font-mono text-xs">/{c.slug}</span>
                </p>
              </div>
              <span className="hidden text-sm text-zinc-500 sm:block">
                {c.open_leads} open {c.open_leads === 1 ? "lead" : "leads"}
              </span>
              <span
                className={`rounded-full px-2.5 py-1 text-xs font-medium ${
                  c.status === "published" ? "bg-emerald-50 text-emerald-700" : "bg-zinc-100 text-zinc-500"
                }`}
              >
                {c.status === "published" ? "Published" : "Draft"}
              </span>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
