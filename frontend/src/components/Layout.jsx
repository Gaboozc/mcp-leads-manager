import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../auth.jsx";

const tab = ({ isActive }) =>
  `pressable rounded-lg px-3 py-1.5 text-sm font-medium ${
    isActive ? "bg-zinc-900 text-white" : "text-zinc-600 hover:bg-zinc-200/70 hover:text-zinc-900"
  }`;

export default function Layout() {
  const { signOut } = useAuth();
  return (
    <div className="flex h-screen flex-col">
      <header className="flex h-14 shrink-0 items-center gap-4 sm:gap-6 border-b border-zinc-200 bg-white px-4 sm:px-6">
        <div className="flex items-center gap-2">
          <img src="/favicon.svg" alt="" className="h-6 w-6" />
          <span className="hidden font-semibold sm:inline">Leads Inbox</span>
        </div>
        <nav className="flex gap-1">
          <NavLink to="/" end className={tab}>
            Inbox
          </NavLink>
          <NavLink to="/courses" className={tab}>
            Courses
          </NavLink>
        </nav>
        <button
          onClick={() => signOut()}
          className="pressable ml-auto whitespace-nowrap rounded-lg px-3 py-1.5 text-sm text-zinc-500 hover:bg-zinc-100 hover:text-zinc-900"
        >
          Sign out
        </button>
      </header>
      <div className="min-h-0 flex-1">
        <Outlet />
      </div>
    </div>
  );
}
