// src/components/layout/Layout.jsx
import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";

export default function Layout() {
  return (
    <div className="flex bg-slate-950 min-h-screen text-slate-200 overflow-hidden font-sans selection:bg-cyan-500/30">
      <Sidebar />
      <div className="flex-1 flex flex-col h-screen overflow-hidden relative">
        <Topbar />
        <main className="flex-1 overflow-x-hidden overflow-y-auto p-6 md:p-8 relative">
          {/* Subtle background glow for the entire content area */}
          <div className="absolute top-0 left-0 w-full h-[500px] bg-gradient-to-br from-cyan-500/10 via-transparent to-transparent opacity-50 pointer-events-none mix-blend-screen"></div>
          <div className="relative z-0 h-full">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
