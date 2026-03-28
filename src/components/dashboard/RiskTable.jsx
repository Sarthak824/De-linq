export default function RiskTable({ customers }) {
  return (
    <div className="bg-slate-900/50 backdrop-blur-md border border-slate-700/50 rounded-2xl flex flex-col overflow-hidden">
      <div className="p-6 border-b border-slate-700/50">
        <h3 className="text-lg font-semibold text-white">Top High-Risk Customers</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-800/30 text-slate-400 text-sm border-b border-slate-700/50">
              <th className="px-6 py-4 font-medium">Name</th>
              <th className="px-6 py-4 font-medium">Risk Score</th>
              <th className="px-6 py-4 font-medium">Risk Category</th>
              <th className="px-6 py-4 font-medium">Key Driver</th>
              <th className="px-6 py-4 font-medium">Last Activity</th>
              <th className="px-6 py-4 font-medium">Suggested Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700/50 text-sm">
            {customers.map((c, i) => (
              <tr key={i} className="hover:bg-slate-800/30 transition-colors">
                <td className="px-6 py-4 text-white font-medium">{c.name}</td>
                <td className="px-6 py-4">
                  <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
                    c.riskScore > 80 ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' :
                    c.riskScore > 50 ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
                    'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                  }`}>
                    {c.riskScore}/100
                  </span>
                </td>
                <td className="px-6 py-4 text-slate-300">{c.category}</td>
                <td className="px-6 py-4 text-slate-500 text-sm">{c.keyDriver}</td>
                <td className="px-6 py-4 text-slate-400">{c.lastActivity}</td>
                <td className="px-6 py-4">
                  <button className="text-cyan-400 hover:text-cyan-300 font-medium transition-colors">
                    {c.action}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
