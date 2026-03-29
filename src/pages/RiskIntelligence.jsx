import React, { useState, useEffect } from 'react';
import { 
  ShieldAlert, 
  Activity, 
  Zap, 
  Layers, 
  TrendingUp, 
  AlertTriangle,
  Loader2,
  PieChart as PieIcon,
  BarChart3,
  Waves
} from 'lucide-react';
import { buildApiUrl } from '../lib/api';
import CRSPlotlyChart from '../components/analytics/CRSPlotlyChart';

const IntelligenceCard = ({ title, subtitle, icon: Icon, color, children }) => (
  <div className="bg-[#131b2e]/60 backdrop-blur-xl border border-white/5 rounded-2xl p-6 hover:border-white/10 transition-all group h-full">
    <div className="flex items-center justify-between mb-6">
      <div>
        <h3 className="text-xl font-bold text-slate-100">{title}</h3>
        <p className="text-sm text-slate-400">{subtitle}</p>
      </div>
      <div className={`p-3 rounded-xl bg-${color}-500/10 group-hover:scale-110 transition-transform`}>
        <Icon className={`w-6 h-6 text-${color}-400`} />
      </div>
    </div>
    {children}
  </div>
);

const ProgressBar = ({ value, color, label }) => (
  <div className="space-y-2">
    <div className="flex justify-between text-xs font-semibold">
      <span className="text-slate-400 uppercase tracking-wider">{label}</span>
      <span className={`text-${color}-400`}>{value}%</span>
    </div>
    <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
      <div 
        className={`h-full bg-${color}-500 transition-all duration-1000 ease-out`}
        style={{ width: `${value}%` }}
      />
    </div>
  </div>
);

export default function RiskIntelligence() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch(buildApiUrl('/portfolio-summary'));
        const json = await res.json();
        setData(json);
      } catch (err) {
        console.error("Risk Intelligence fetch failed:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-[#0B1220]">
        <Loader2 className="w-10 h-10 text-cyan-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="flex flex-col space-y-8 animate-in fade-in duration-700 p-8 min-h-screen bg-[#0B1220] text-slate-200">
      <header className="flex flex-col space-y-2">
        <h1 className="text-4xl font-black bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-cyan-400 to-teal-400">
          Portfolio Risk Intelligence
        </h1>
        <p className="text-slate-400 text-lg max-w-2xl">
          Deep-dive behavioral analytics across 8,000 intelligence records. 
          Real-time signals captured from 6 distinct fragility engines.
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Row 1 */}
        <IntelligenceCard 
          title="Hidden Distress Engine" 
          subtitle="Sub-radar stress signals"
          icon={ShieldAlert}
          color="amber"
        >
          <div className="space-y-5">
            <ProgressBar label="Informal Borrowing Signals" value={64} color="amber" />
            <ProgressBar label="Inflow Fragmentation" value={42} color="amber" />
            <ProgressBar label="Patchwork Recovery" value={78} color="amber" />
            <div className="pt-4 border-t border-white/5">
              <p className="text-xs text-slate-500 leading-relaxed italic">
                "Detecting informal borrowing via non-standard P2P inflows."
              </p>
            </div>
          </div>
        </IntelligenceCard>

        <IntelligenceCard 
          title="Exposure Analyzer" 
          subtitle="Portfolio debt fragility"
          icon={Layers}
          color="indigo"
        >
          <div className="space-y-5">
            <ProgressBar label="Unsecured Concentration" value={58} color="indigo" />
            <ProgressBar label="Multi-Lender Overlap" value={35} color="indigo" />
            <ProgressBar label="Leverage Vulnerability" value={82} color="indigo" />
            <div className="pt-4 border-t border-white/5">
              <p className="text-xs text-slate-500 leading-relaxed italic">
                "Identifying 'Leverage Traps' where minor shocks lead to default."
              </p>
            </div>
          </div>
        </IntelligenceCard>

        <IntelligenceCard 
          title="Liquidity Stress" 
          subtitle="Emergency cash generation"
          icon={Waves}
          color="teal"
        >
          <div className="space-y-5">
            <ProgressBar label="Fixed Deposit Breaks" value={31} color="teal" />
            <ProgressBar label="Mutual Fund Liquidations" value={19} color="teal" />
            <ProgressBar label="Overdraft Utilization Max" value={88} color="teal" />
            <div className="pt-4 border-t border-white/5">
              <p className="text-xs text-slate-500 leading-relaxed italic">
                "Tracking asset depletion rates as a leading indicator of stress."
              </p>
            </div>
          </div>
        </IntelligenceCard>

        {/* Row 2 */}
        <IntelligenceCard 
          title="Cash Flow Reliability (CRS)" 
          subtitle="Gig-Economy Stability Matrix"
          icon={Zap}
          color="cyan"
        >
          <div className="h-[200px] -mt-4">
            <CRSPlotlyChart />
          </div>
          <div className="pt-2 border-t border-white/5">
            <p className="text-[10px] text-slate-500 leading-tight">
              Mapping <span className="text-teal-400 font-bold">Reliability</span> vs <span className="text-rose-400 font-bold">Risk</span>. Bottom-right quadrant identifies "Hidden Gems".
            </p>
          </div>
        </IntelligenceCard>

        <IntelligenceCard 
          title="Risk Archetypes" 
          subtitle="Persona distribution"
          icon={PieIcon}
          color="purple"
        >
          <div className="space-y-4">
            <div className="flex justify-between items-center bg-white/5 p-3 rounded-xl">
              <span className="text-sm font-semibold text-teal-400">Stable Gig Worker</span>
              <span className="text-xs text-slate-400">14%</span>
            </div>
            <div className="flex justify-between items-center bg-white/5 p-3 rounded-xl border border-blue-500/20">
              <span className="text-sm font-semibold text-blue-400">Volatile Gig Worker</span>
              <span className="text-xs text-slate-400">31%</span>
            </div>
            <div className="flex justify-between items-center bg-white/5 p-3 rounded-xl border border-rose-500/20">
              <span className="text-sm font-semibold text-rose-400">Declining Gig Worker</span>
              <span className="text-xs text-slate-400">8%</span>
            </div>
          </div>
        </IntelligenceCard>

        <IntelligenceCard 
          title="Severity Triggers" 
          subtitle="Top risk drivers (%)"
          icon={BarChart3}
          color="rose"
        >
          <div className="space-y-4">
            <div className="flex flex-wrap gap-2">
              {['Salary Delay', 'Informal P2P', 'OD Usage', 'Cash-Flow Reliability', 'FD Break'].map(tag => (
                <span key={tag} className={`px-2 py-0.5 bg-white/5 border border-white/10 rounded-full text-[9px] font-bold ${tag === 'Cash-Flow Reliability' ? 'text-cyan-400 border-cyan-500/30' : 'text-slate-400'} uppercase`}>
                  {tag}
                </span>
              ))}
            </div>
            <div className="h-[100px] flex items-end gap-2 px-2">
              {[60, 85, 45, 95, 55, 90, 40].map((h, i) => (
                <div key={i} className={`flex-1 ${i === 3 ? 'bg-cyan-500' : 'bg-rose-500/40'} rounded-t-sm transition-colors`} style={{ height: `${h}%` }} />
              ))}
            </div>
          </div>
        </IntelligenceCard>
      </div>
    </div>
  );
}
