// src/components/layout/Topbar.jsx
import { Search, Bell, User } from "lucide-react";

export default function Topbar() {
  return (
    <header className="h-16 border-b border-slate-700/50 bg-slate-900/50 backdrop-blur-md flex items-center justify-between px-8 sticky top-0 z-10">
      <div className="flex-1 flex justify-start">
        <div className="relative w-96 hidden md:block group">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4 group-focus-within:text-cyan-400 transition-colors" />
          <input
            type="text"
            placeholder="Search customers, risks, or reports..."
            className="w-full bg-slate-800/50 border border-slate-700/50 text-slate-200 text-sm rounded-lg focus:ring-1 focus:ring-cyan-500 focus:border-cyan-500 block pl-10 p-2 outline-none transition-all"
          />
        </div>
      </div>
      
      <div className="flex items-center gap-4 text-slate-400">
        <button className="p-2 hover:bg-slate-800 rounded-lg transition-colors relative">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-cyan-400 shadow-[0_0_8px_rgba(6,182,212,0.8)] rounded-full"></span>
        </button>
        <div className="h-8 w-px bg-slate-700 mx-2"></div>
        <button className="flex items-center gap-2 hover:bg-slate-800 p-1.5 pr-3 rounded-lg transition-colors">
          <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center border border-slate-600">
            <User className="w-4 h-4 text-slate-300" />
          </div>
          <span className="text-sm font-medium hidden sm:block text-slate-300">Admin User</span>
        </button>
      </div>
    </header>
  );
}
