import { useMemo, useState } from 'react';
import { ShieldAlert, Info, TrendingUp, AlertTriangle, Search, Filter, Download, UserMinus } from 'lucide-react';

const generateMockData = (count) => {
  const names = ["Rahul Sharma", "Priya Desai", "Amit Kumar", "Neha Gupta", "Vikram Singh", "Anjali Verma", "Rohan Mehta", "Sneha Iyer", "Karan Chawla", "Pooja Reddy", "Sanjay Dutt", "Meera Nair", "Arjun Kapoor", "Deepa Rani", "Rishi Kapoor", "Kiran Mazumdar", "Aditya Birla", "Sunita Williams", "Manish Malhotra", "Shobhaa De"];
  const locations = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Pune", "Chennai", "Kolkata", "Ahmedabad", "Gurgaon", "Noida"];
  const statuses = ["Active", "Dormant", "Under Review"];
  const reasons = ["High EMI burden", "Frequent late payments", "Spending spike", "Salary delay detected", "High credit utilization"];

  return Array.from({ length: count }, (_, i) => {
    const riskScore = Math.floor(Math.random() * 100);
    let category = "Low";
    if (riskScore > 70) category = "High";
    else if (riskScore > 40) category = "Medium";

    return {
      id: `CUST-${(101000 + i).toString()}`,
      name: names[i % names.length],
      age: 22 + Math.floor(Math.random() * 40),
      gender: i % 2 === 0 ? "M" : "F",
      location: locations[i % locations.length],
      income: 45000 + Math.floor(Math.random() * 150000),
      emiBurden: Math.floor(Math.random() * 60),
      creditUtil: Math.floor(Math.random() * 95),
      totalLoans: 1 + Math.floor(Math.random() * 4),
      avgSpend: 15000 + Math.floor(Math.random() * 50000),
      latePayments: Math.floor(Math.random() * 5),
      salaryDelay: Math.random() > 0.8 ? "Yes" : "No",
      cashFreq: ["Daily", "Weekly", "Bi-weekly", "Monthly"][Math.floor(Math.random() * 4)],
      lastTxnDate: "2026-03-" + (10 + (i % 15)).toString().padStart(2, '0'),
      txnFreq: 5 + Math.floor(Math.random() * 25),
      avgTxnValue: 800 + Math.floor(Math.random() * 5000),
      riskScore,
      category,
      keyReason: category === "Low" ? "Stable History" : reasons[Math.floor(Math.random() * reasons.length)],
      status: statuses[Math.floor(Math.random() * statuses.length)],
      lastActivity: (i % 12) + " hours ago"
    };
  });
};

export default function Customers() {
  const [searchTerm, setSearchTerm] = useState('');
  const mockData = useMemo(() => generateMockData(25), []);

  const filteredData = useMemo(() => {
    if (!searchTerm.trim()) return mockData;
    
    const term = searchTerm.toLowerCase();
    return mockData.filter(item => 
      item.id.toLowerCase().includes(term) || 
      item.name.toLowerCase().includes(term)
    ).sort((a, b) => {
      // Prioritize exact ID matches
      const aId = a.id.toLowerCase();
      const bId = b.id.toLowerCase();
      if (aId === term && bId !== term) return -1;
      if (bId === term && aId !== term) return 1;
      return 0;
    });
  }, [mockData, searchTerm]);

  return (
    <div className="flex flex-col h-full space-y-6 animate-in fade-in duration-500 pb-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 shrink-0 px-1">
        <div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-blue-500 tracking-tight">
            Customer Intelligence
          </h1>
          <p className="text-slate-400 mt-1">Investigative datagrid with behavioral and risk-driven insights.</p>
        </div>
        <div className="flex gap-3">
          <button className="flex items-center gap-2 px-4 py-2 bg-slate-800/50 hover:bg-slate-700/50 border border-slate-700/50 rounded-xl text-slate-300 transition-all text-sm">
            <Download className="w-4 h-4" />
            Export Data
          </button>
        </div>
      </div>

      {/* Toolbar */}
      <div className="flex flex-wrap items-center gap-4 bg-slate-900/40 backdrop-blur-md border border-white/5 rounded-2xl p-4 shrink-0 shadow-xl">
        <div className="relative flex-1 min-w-[280px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input 
            type="text" 
            placeholder="Search by name, account number..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-800/40 border border-slate-700/50 rounded-xl py-2 pl-10 pr-4 text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-cyan-500/50 transition-colors text-sm"
          />
        </div>
        <div className="flex items-center gap-2">
          <button className="p-2 bg-slate-800/40 border border-slate-700/50 rounded-xl text-slate-400 hover:text-cyan-400 transition-colors">
            <Filter className="w-4 h-4" />
          </button>
          <select className="bg-slate-800/40 border border-slate-700/50 rounded-xl py-2 px-3 text-sm text-slate-300 focus:outline-none focus:border-cyan-500/50">
            <option>All Risk Categories</option>
            <option>High Risk</option>
            <option>Medium Risk</option>
            <option>Low Risk</option>
          </select>
        </div>
      </div>

      {/* Data Table Container */}
      <div className="flex-1 min-h-0 bg-slate-900/60 backdrop-blur-md border border-white/5 rounded-2xl overflow-hidden shadow-2xl flex flex-col">
        <div className="overflow-auto flex-1 custom-scrollbar relative">
          <table className="w-full text-left border-collapse min-w-[2400px]">
            <thead className="sticky top-0 z-20">
              <tr className="bg-slate-800/95 backdrop-blur-md border-b border-white/10 shadow-lg">
                {/* IDENTITY GROUP */}
                <th colSpan="4" className="px-6 py-2 text-[10px] font-bold text-cyan-500 uppercase tracking-widest bg-cyan-500/5 border-r border-white/5">Identity</th>
                {/* FINANCIAL GROUP */}
                <th colSpan="4" className="px-6 py-2 text-[10px] font-bold text-emerald-500 uppercase tracking-widest bg-emerald-500/5 border-r border-white/5">Location & Financial</th>
                {/* BEHAVIORAL GROUP */}
                <th colSpan="8" className="px-6 py-2 text-[10px] font-bold text-amber-500 uppercase tracking-widest bg-amber-500/5 border-r border-white/5">Behavioral & Transactional</th>
                {/* RISK GROUP */}
                <th colSpan="3" className="px-6 py-2 text-[10px] font-bold text-rose-500 uppercase tracking-widest bg-rose-500/5 border-r border-white/5">Risk Intelligence</th>
                {/* SYSTEM GROUP */}
                <th colSpan="2" className="px-6 py-2 text-[10px] font-bold text-slate-400 uppercase tracking-widest bg-slate-400/5">System Status</th>
              </tr>
              <tr className="bg-slate-800/80 backdrop-blur-md border-b border-white/10">
                {/* IDENTITY */}
                <th className="px-6 py-4 text-xs font-bold text-slate-300 uppercase tracking-wider">Account #</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-300 uppercase tracking-wider">Name</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-300 uppercase tracking-wider">Age</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-300 uppercase tracking-wider border-r border-white/5">Gender</th>
                
                {/* FINANCIAL */}
                <th className="px-6 py-4 text-xs font-bold text-slate-300 uppercase tracking-wider">Location</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-300 uppercase tracking-wider">Income</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-300 uppercase tracking-wider">EMI Burden</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-300 uppercase tracking-wider border-r border-white/5">Credit Util.</th>

                {/* BEHAVIORAL */}
                <th className="px-6 py-4 text-xs font-bold text-slate-300 uppercase tracking-wider">Loans</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-300 uppercase tracking-wider">Avg Spend</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-300 uppercase tracking-wider">Late Pmts</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-300 uppercase tracking-wider">Salary Delay</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-300 uppercase tracking-wider">Cash Freq.</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-300 uppercase tracking-wider">Last Txn</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-300 uppercase tracking-wider">Txn Freq.</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-300 uppercase tracking-wider border-r border-white/5">Avg Txn Value</th>

                {/* RISK */}
                <th className="px-6 py-4 text-xs font-bold text-slate-300 uppercase tracking-wider">Risk Score</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-300 uppercase tracking-wider">Category</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-300 uppercase tracking-wider border-r border-white/5">Key Reason</th>

                {/* SYSTEM */}
                <th className="px-6 py-4 text-xs font-bold text-slate-300 uppercase tracking-wider">Status</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-300 uppercase tracking-wider">Last Activity</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {filteredData.length > 0 ? (
                filteredData.map((row) => (
                  <tr key={row.id} className="hover:bg-slate-800/40 transition-colors group cursor-default">
                    {/* IDENTITY */}
                    <td className="px-6 py-4 text-sm font-mono text-cyan-400/80">{row.id}</td>
                    <td className="px-6 py-4 text-sm font-medium text-slate-200">{row.name}</td>
                    <td className="px-6 py-4 text-sm text-slate-400">{row.age}</td>
                    <td className="px-6 py-4 text-sm text-slate-400 border-r border-white/5">{row.gender}</td>

                    {/* FINANCIAL */}
                    <td className="px-6 py-4 text-sm text-slate-400">{row.location}</td>
                    <td className="px-6 py-4 text-sm text-slate-300">₹{row.income.toLocaleString()}</td>
                    <td className="px-6 py-4 text-sm text-slate-300">{row.emiBurden}%</td>
                    <td className="px-6 py-4 text-sm text-slate-300 border-r border-white/5">{row.creditUtil}%</td>

                    {/* BEHAVIORAL */}
                    <td className="px-6 py-4 text-sm text-slate-300">{row.totalLoans}</td>
                    <td className="px-6 py-4 text-sm text-slate-300">₹{row.avgSpend.toLocaleString()}</td>
                    <td className="px-6 py-4 text-sm">
                      <span className={row.latePayments > 2 ? "text-rose-400 font-bold" : "text-slate-400"}>
                        {row.latePayments}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <span className={row.salaryDelay === "Yes" ? "text-amber-400 font-bold" : "text-slate-400"}>
                        {row.salaryDelay}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-slate-300">{row.cashFreq}</td>
                    <td className="px-6 py-4 text-sm text-slate-300">{row.lastTxnDate}</td>
                    <td className="px-6 py-4 text-sm text-slate-300">{row.txnFreq}</td>
                    <td className="px-6 py-4 text-sm text-slate-300 border-r border-white/5">₹{row.avgTxnValue.toLocaleString()}</td>

                    {/* RISK */}
                    <td className="px-6 py-4 text-sm">
                      <div className="flex items-center gap-3">
                        <span className={`text-lg font-bold ${
                          row.riskScore > 70 ? 'text-rose-400' : row.riskScore > 40 ? 'text-amber-400' : 'text-emerald-400'
                        }`}>
                          {row.riskScore}
                        </span>
                        <div className="w-12 h-1 bg-slate-800 rounded-full overflow-hidden flex-shrink-0">
                          <div 
                            className={`h-full rounded-full ${
                              row.riskScore > 70 ? 'bg-rose-500' : row.riskScore > 40 ? 'bg-amber-500' : 'bg-emerald-500'
                            }`}
                            style={{ width: `${row.riskScore}%` }}
                          />
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <span className={`px-2 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider border ${
                        row.category === 'High' ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' :
                        row.category === 'Medium' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' :
                        'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                      }`}>
                        {row.category}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm border-r border-white/5 text-slate-400 italic font-light truncate max-w-[150px]" title={row.keyReason}>
                      {row.keyReason}
                    </td>

                    {/* SYSTEM */}
                    <td className="px-6 py-4 text-sm">
                      <span className={`flex items-center gap-1.5 ${row.status === 'Active' ? 'text-emerald-400' : 'text-slate-500'}`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${row.status === 'Active' ? 'bg-emerald-500 animate-pulse' : 'bg-slate-500'}`} />
                        {row.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-slate-500 group-hover:text-cyan-400 transition-colors whitespace-nowrap">{row.lastActivity}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="21" className="px-6 py-24 text-center">
                    <div className="flex flex-col items-center gap-3 text-slate-500">
                      <div className="p-4 bg-slate-800/50 rounded-full border border-white/5 shadow-inner">
                        <UserMinus className="w-8 h-8 opacity-50" />
                      </div>
                      <p className="text-lg font-medium text-slate-300">No Customers Found</p>
                      <p className="text-sm">No matches found for <span className="font-mono text-cyan-400 bg-cyan-400/5 px-2 py-0.5 rounded border border-cyan-500/10">"{searchTerm}"</span></p>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        
        {/* Footer info */}
        <div className="p-4 border-t border-white/5 bg-slate-800/30 text-xs text-slate-500 flex justify-between items-center shrink-0">
          <p>Showing 25 investigation records</p>
          <div className="flex gap-4">
            <span className="flex items-center gap-1"><span className="w-2 h-2 bg-rose-500 rounded-full" /> Critical</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 bg-amber-500 rounded-full" /> Elevated</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 bg-emerald-500 rounded-full" /> Healthy</span>
          </div>
        </div>
      </div>
    </div>
  );
}

