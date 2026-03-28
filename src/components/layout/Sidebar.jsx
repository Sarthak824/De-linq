// src/components/layout/Sidebar.jsx
import { NavLink } from "react-router-dom";
import { LayoutDashboard, Users, ShieldAlert, Activity, FileText } from "lucide-react";

const navItems = [
  { name: "Dashboard", path: "/", icon: LayoutDashboard },
  { name: "Customers", path: "/customers", icon: Users },
  { name: "Risk Intelligence", path: "/risk-intelligence", icon: ShieldAlert },
  { name: "Interventions", path: "/interventions", icon: Activity },
  { name: "Reports", path: "/reports", icon: FileText },
];

export default function Sidebar() {
  return (
    <div className="w-64 h-screen bg-slate-900/80 backdrop-blur-xl border-r border-slate-700/50 flex flex-col hidden md:flex z-20">
      <div className="p-6">
        <h1 className="text-xl font-bold text-white tracking-wider flex items-center gap-2">
          <ShieldAlert className="w-6 h-6 text-cyan-400" />
          <span>DE-LINQ</span>
        </h1>
      </div>
      <nav className="flex-1 px-4 space-y-2 mt-4">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.name}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${
                  isActive
                    ? "bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-[0_0_15px_rgba(6,182,212,0.1)]"
                    : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-200"
                }`
              }
            >
              <Icon className="w-5 h-5" />
              <span className="font-medium">{item.name}</span>
            </NavLink>
          );
        })}
      </nav>
    </div>
  );
}
