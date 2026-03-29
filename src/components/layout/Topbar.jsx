// src/components/layout/Topbar.jsx
import { Search, Bell, User, X, ArrowUpRight } from "lucide-react";
import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { buildApiUrl } from "../../lib/api";

export default function Topbar() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const searchRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (searchRef.current && !searchRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSearch = async (val) => {
    setQuery(val);
    if (val.length < 2) {
      setResults([]);
      setIsOpen(false);
      return;
    }

    setLoading(true);
    setIsOpen(true);
    try {
      // Fetching all customers for local filtering to keep it super fast after first load
      const res = await fetch(buildApiUrl("/customers"));
      const dataObj = await res.json();
      const customersList = Array.isArray(dataObj.customers) ? dataObj.customers : (Array.isArray(dataObj) ? dataObj : []);
      const filtered = customersList
        .filter(c => 
          (c.customer_id && c.customer_id.toLowerCase().includes(val.toLowerCase())) ||
          (c.intervention && c.intervention.toLowerCase().includes(val.toLowerCase()))
        )
        .slice(0, 5);
      setResults(filtered);
    } catch (err) {
      console.error("Search error:", err);
    } finally {
      setLoading(false);
    }
  };

  const navigateToCustomer = (id) => {
    setIsOpen(false);
    setQuery("");
    navigate(`/customer/${id}`);
  };

  return (
    <header className="h-16 border-b border-slate-700/50 bg-slate-900/50 backdrop-blur-md flex items-center justify-between px-8 sticky top-0 z-50">
      <div className="flex-1 flex justify-start">
        <div className="relative w-96 hidden md:block group" ref={searchRef}>
          <Search className={`absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 transition-colors ${isOpen ? 'text-cyan-400' : 'text-slate-400'}`} />
          <input
            type="text"
            value={query}
            onChange={(e) => handleSearch(e.target.value)}
            onFocus={() => query.length >= 2 && setIsOpen(true)}
            placeholder="Search customers, risks, or intervention..."
            className="w-full bg-slate-800/30 border border-slate-700/50 text-slate-200 text-sm rounded-xl focus:ring-1 focus:ring-cyan-500/50 focus:border-cyan-500/50 block pl-10 p-2.5 outline-none transition-all shadow-inner hover:bg-slate-800/50"
          />
          
          <AnimatePresence>
            {isOpen && (
              <motion.div 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                className="absolute top-full left-0 right-0 mt-2 bg-slate-900 border border-white/10 rounded-2xl shadow-2xl overflow-hidden z-[100] p-2 backdrop-blur-2xl"
              >
                {loading ? (
                  <div className="p-4 text-center text-xs text-slate-500 flex items-center justify-center gap-2">
                    <div className="w-3 h-3 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
                    Searching Intelligence...
                  </div>
                ) : results.length > 0 ? (
                  <div className="space-y-1">
                    <p className="px-3 py-2 text-[10px] font-black uppercase tracking-widest text-slate-500">Suggested Results</p>
                    {results.map((c) => (
                      <button
                        key={c.customer_id}
                        onClick={() => navigateToCustomer(c.customer_id)}
                        className="w-full flex items-center justify-between p-3 rounded-xl hover:bg-white/5 transition-colors group text-left"
                      >
                        <div className="flex items-center gap-3">
                          <div className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold text-[10px] ${
                            c.risk_score > 70 ? 'bg-rose-500/10 text-rose-400' : 
                            c.risk_score > 40 ? 'bg-amber-500/10 text-amber-400' : 
                            'bg-emerald-500/10 text-emerald-400'
                          }`}>
                            {Math.round(c.risk_score)}
                          </div>
                          <div>
                            <p className="text-sm font-bold text-white leading-none">{c.customer_id}</p>
                            <p className="text-[10px] text-slate-500 mt-1 uppercase tracking-tighter">{c.intervention}</p>
                          </div>
                        </div>
                        <ArrowUpRight className="w-4 h-4 text-slate-600 group-hover:text-cyan-400 transition-colors" />
                      </button>
                    ))}
                  </div>
                ) : (
                  <div className="p-8 text-center">
                    <p className="text-sm text-slate-400 font-bold">No matches found</p>
                    <p className="text-[11px] text-slate-500 mt-1 italic">"The behavior you're looking for is currently clear."</p>
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
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
