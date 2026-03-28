import { useParams, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { ArrowLeft, AlertTriangle, CheckCircle, Info, Activity, ShieldAlert, Zap, DollarSign, Wallet, CreditCard, Crosshair, Users } from "lucide-react";
import { PieChart, Pie, Cell, Tooltip as RechartsTooltip, BarChart, Bar, XAxis, YAxis, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from "recharts";
import { motion } from "framer-motion";

export default function CustomerDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    const loadCustomer = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:8000/customers/${id}`);
        if (!response.ok) throw new Error("Not found");
        const json = await response.json();
        
        const profile = json.profile || {};
        const prediction = json.prediction || {};
        
        setData({
          id: id,
          riskScore: (prediction.risk_score || 0.5) * 100,
          category: prediction.risk_band || "Medium",
          intervention: prediction.recommended_intervention || "Send payment reminder",
          persona: prediction.persona_label || "Standard User",
          intent: prediction.intent_label || "Stable",
          reasons: prediction.top_reason_codes || ["Stable profile"],
          
          // Core Metrics
          income: profile.monthly_income || 50000,
          emi: profile.emi || 15000,
          creditDue: profile.credit_card_due || 5000,
          creditUtil: (profile.credit_utilization || 0.4) * 100,
          missedPayments: profile.missed_payments || 0,
          
          // Enhanced Metrics
          age: profile.age || 35,
          tenure: profile.account_tenure || 24,
          liquidityBuffer: profile.liquidity_buffer || 15000,
          emiRatio: (profile.emi_to_income_ratio || 0.3) * 100,
          debtStress: (profile.debt_stress_ratio || 0.4) * 100,
          healthScore: (profile.financial_health_score || 0.5) * 100,
          stabilityScore: (profile.stability_score || 0.5) * 100,
          paymentDisc: (profile.payment_discipline || 0.5) * 100,
          avgBalance: profile.avg_balance || 25000,
          jobLoss: profile.job_loss || 0,
          salaryDelay: profile.salary_delay || 0,
          spendingInstability: (profile.spending_instability || 0) * 100,
          shockFlag: profile.shock_flag || 0,
          atmWithdrawals: profile.atm_withdrawals || 0,
          billDelayCount: profile.bill_delay_count || 0,

          // 2nd Layer: Credit Exposure
          exposureLevel: prediction.credit_exposure_level || "Low",
          exposureMessage: prediction.credit_exposure_message || "Stable debt structure.",
          debtStructure: prediction.debt_structure || "Secured",
          activeLoanSummary: prediction.active_loan_summary || "0 active loans",
          exposureScore: (prediction.exposure_score || 0) * 100
        });
      } catch (err) {
        // Deterministic Fallback Mock for UX Testing
        const numId = parseInt(id.replace(/[^0-9]/g, '')) || 101000;
        const seed = numId % 100;
        const risk = 40 + ((seed * 7) % 50);
        
        setData({
          id: id,
          riskScore: risk,
          category: risk > 75 ? "High" : risk > 50 ? "Medium" : "Low",
          intervention: risk > 75 ? "Offer EMI Restructuring & Pause" : risk > 50 ? "Proactive Check-in Call" : "Automated Payment Reminder",
          persona: risk > 75 ? "Credit Dependent Stressed User" : risk > 50 ? "Willing but Overleveraged" : "Stable Planner",
          intent: risk > 75 ? "high_distress" : risk > 50 ? "willing_but_stressed" : "stable",
          reasons: risk > 75 ? ["High EMI burden", "Low liquidity buffer", "Recent salary delay"] : ["Minor credit utilization spike"],
          
          income: 60000 + (seed * 1000),
          emi: 20000 + (seed * 200),
          creditDue: 5000 + (seed * 100),
          creditUtil: 30 + (seed % 60),
          missedPayments: seed % 4,
          
          age: 26 + (seed % 20),
          tenure: 12 + (seed % 48),
          liquidityBuffer: 25000 - (seed * 200),
          emiRatio: 33 + (seed % 20),
          debtStress: 40 + (seed % 30),
          healthScore: 85 - (seed % 40),
          stabilityScore: 90 - (seed % 50),
          paymentDisc: 85 - (seed % 20),
          avgBalance: 30000 - (seed * 100),
          jobLoss: seed % 11 === 0 ? 1 : 0,
          salaryDelay: seed % 7 === 0 ? 1 : 0,
          spendingInstability: (seed % 100),
          shockFlag: seed % 13 === 0 ? 1 : 0,
          atmWithdrawals: seed % 5,
          billDelayCount: seed % 3,

          // Fallback Exposure Mock
          exposureLevel: seed % 7 === 0 ? "High" : seed % 3 === 0 ? "Moderate" : "Low",
          exposureMessage: seed % 7 === 0 ? "High exposure due to multiple unsecured personal loans." : "Stable credit structure.",
          debtStructure: seed % 7 === 0 ? "Unsecured-Heavy" : "Secured",
          activeLoanSummary: `${(seed % 5) + 1} active (${seed % 2}S, ${(seed % 3) + 1}P, 0G)`,
          exposureScore: 20 + (seed % 60)
        });
      } finally {
        setLoading(false);
      }
    };
    loadCustomer();
  }, [id]);

  if (loading) return (
    <div className="flex flex-col items-center justify-center min-h-[600px] gap-4">
      <div className="w-12 h-12 border-4 border-cyan-500/20 border-t-cyan-500 rounded-full animate-spin shadow-[0_0_15px_rgba(6,182,212,0.5)]"></div>
      <p className="text-cyan-400/70 font-mono tracking-widest text-sm animate-pulse">ANALYZING PROFILE...</p>
    </div>
  );

  if (!data) return <div className="p-10 text-rose-400">Failed to load customer profile.</div>;

  const hexColor = data.riskScore > 75 ? "#f43f5e" : data.riskScore > 50 ? "#f59e0b" : "#10b981";
  const glowClass = data.riskScore > 75 ? "shadow-[0_0_30px_rgba(244,63,94,0.15)] border-rose-500/30" : data.riskScore > 50 ? "shadow-[0_0_30px_rgba(245,158,11,0.15)] border-amber-500/30" : "shadow-[0_0_30px_rgba(16,185,129,0.15)] border-emerald-500/30";
  const textClass = data.riskScore > 75 ? "text-rose-400" : data.riskScore > 50 ? "text-amber-400" : "text-emerald-400";
  const bgClass = data.riskScore > 75 ? "bg-rose-500/10" : data.riskScore > 50 ? "bg-amber-500/10" : "bg-emerald-500/10";

  const remainingIncome = data.income - data.emi - data.creditDue;

  // Transform constraints into a visual radar map
  const radarData = [
    { subject: 'Financial Health', value: data.healthScore },
    { subject: 'Income Stability', value: data.stabilityScore },
    { subject: 'Payment Discipline', value: data.paymentDisc },
    { subject: 'Debt Capacity', value: Math.max(0, 100 - data.debtStress) },
    { subject: 'Liquidity Health', value: Math.min(100, (data.liquidityBuffer / 20000) * 100) },
    { subject: 'Credit Buffer', value: Math.max(0, 100 - data.creditUtil) }
  ];

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-8 pb-12">
      
      {/* Header Elements */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 border-b border-white/10 pb-6">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate(-1)} className="p-2.5 bg-slate-800/80 hover:bg-slate-700/80 border border-white/5 backdrop-blur-md rounded-xl text-slate-300 transition-all hover:-translate-x-1">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-4xl font-black tracking-tight text-white flex items-center gap-3">
              {data.id} 
              {data.shockFlag === 1 && <span className="px-2 py-0.5 rounded text-[10px] uppercase tracking-widest bg-rose-500/20 text-rose-400 border border-rose-500/30 animate-pulse">Financial Shock</span>}
            </h1>
            <div className="flex flex-wrap items-center gap-2 mt-3">
              <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider border backdrop-blur-md ${bgClass} ${textClass} border-${hexColor}/30 flex items-center gap-1.5`}>
                {data.category === "High" ? <AlertTriangle className="w-3.5 h-3.5" /> : <CheckCircle className="w-3.5 h-3.5" />}
                {data.category} Risk
              </span>
              <span className="px-3 py-1 bg-slate-800/80 border border-slate-700 rounded-full text-xs text-slate-300 font-medium flex items-center gap-1.5">
                <Users className="w-3.5 h-3.5 text-cyan-400" />
                Persona: <span className="text-cyan-400">{data.persona}</span>
              </span>
              <span className="px-3 py-1 bg-slate-800/80 border border-slate-700 rounded-full text-xs text-slate-300 font-medium flex items-center gap-1.5">
                <Crosshair className="w-3.5 h-3.5 text-purple-400" />
                Intent: <span className="text-purple-400">{data.intent.replace(/_/g, " ")}</span>
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Primary Hero Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Risk Score & Intervention Main Block */}
        <motion.div whileHover={{ scale: 1.01 }} className={`lg:col-span-2 relative overflow-hidden bg-slate-900/40 backdrop-blur-xl rounded-3xl border border-white/10 p-8 flex flex-col md:flex-row items-center gap-8 ${glowClass} transition-all duration-300`}>
          {/* Background Glow */}
          <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-bl from-[var(--risk-color)] to-transparent opacity-10 blur-3xl rounded-full translate-x-1/3 -translate-y-1/3 pointer-events-none" style={{ '--risk-color': hexColor }}></div>
          
          <div className="relative shrink-0 flex items-center justify-center w-40 h-40">
            <svg className="w-full h-full transform -rotate-90 drop-shadow-xl" viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="45" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="10" />
              <motion.circle 
                initial={{ strokeDashoffset: 283 }} 
                animate={{ strokeDashoffset: 283 - ((data.riskScore / 100) * 283) }} 
                transition={{ duration: 1.5, ease: "easeOut" }}
                cx="50" cy="50" r="45" fill="none" stroke={hexColor} strokeWidth="10" 
                strokeDasharray="283" strokeLinecap="round" 
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className={`text-4xl font-black ${textClass}`}>{Math.round(data.riskScore)}</span>
              <span className="text-[10px] uppercase font-bold text-slate-500 tracking-widest mt-1">Score</span>
            </div>
          </div>

          <div className="flex-1 space-y-5">
            <div>
              <p className="text-xs uppercase tracking-widest text-slate-400 font-bold flex items-center gap-2 mb-2"><Zap className="w-4 h-4 text-cyan-400" /> Automated Recommendation</p>
              <h2 className="text-2xl md:text-3xl font-black text-white">{data.intervention}</h2>
            </div>
            <div className="pt-4 border-t border-white/10">
              <p className="text-xs uppercase tracking-widest text-slate-500 font-bold mb-3">Identified Top Triggers</p>
              <div className="flex flex-wrap gap-2">
                {data.reasons.map(r => (
                  <span key={r} className="px-2.5 py-1 bg-white/5 border border-white/10 rounded border-l-2 text-xs font-mono text-slate-300" style={{ borderLeftColor: hexColor }}>
                    {r.replace(/_/g, " ")}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </motion.div>

        {/* Rapid Financial Stats */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-slate-900/40 backdrop-blur-md rounded-2xl border border-white/5 p-5 flex flex-col justify-center">
            <Wallet className="w-6 h-6 text-emerald-400 mb-3" />
            <p className="text-xs text-slate-400 uppercase tracking-widest font-bold mb-1">Total Income</p>
            <p className="text-2xl font-black text-white">₹{data.income.toLocaleString()}</p>
          </div>
          <div className="bg-slate-900/40 backdrop-blur-md rounded-2xl border border-white/5 p-5 flex flex-col justify-center">
            <DollarSign className="w-6 h-6 text-amber-400 mb-3" />
            <p className="text-xs text-slate-400 uppercase tracking-widest font-bold mb-1">Fixed EMI</p>
            <p className="text-2xl font-black text-white">₹{data.emi.toLocaleString()}</p>
          </div>
          <div className="bg-slate-900/40 backdrop-blur-md rounded-2xl border border-white/5 p-5 flex flex-col justify-center">
            <CreditCard className="w-6 h-6 text-cyan-400 mb-3" />
            <p className="text-xs text-slate-400 uppercase tracking-widest font-bold mb-1">CC Debt Due</p>
            <p className="text-2xl font-black text-white">₹{data.creditDue.toLocaleString()}</p>
          </div>
          <div className="bg-slate-900/40 backdrop-blur-md rounded-2xl border border-rose-500/20 p-5 flex flex-col justify-center shadow-[inset_0_0_20px_rgba(244,63,94,0.05)]">
            <Activity className="w-6 h-6 text-rose-400 mb-3" />
            <p className="text-xs text-rose-400/80 uppercase tracking-widest font-bold mb-1">Missed Pmts</p>
            <p className={`text-2xl font-black ${data.missedPayments > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>{data.missedPayments}</p>
          </div>
        </div>

      </div>

      {/* Tabs Menu */}
      <div className="flex border-b border-white/10 gap-8 overflow-x-auto custom-scrollbar pt-4">
        <button onClick={() => setActiveTab('overview')} className={`pb-4 text-sm font-bold uppercase tracking-widest transition-colors border-b-2 whitespace-nowrap ${activeTab === 'overview' ? 'text-cyan-400 border-cyan-400' : 'text-slate-500 border-transparent hover:text-slate-300'}`}>Vis Intelligence</button>
        <button onClick={() => setActiveTab('details')} className={`pb-4 text-sm font-bold uppercase tracking-widest transition-colors border-b-2 whitespace-nowrap ${activeTab === 'details' ? 'text-cyan-400 border-cyan-400' : 'text-slate-500 border-transparent hover:text-slate-300'}`}>Full Data Matrix</button>
      </div>

      {/* Tab: Overview (Charts) */}
      {activeTab === 'overview' && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Credit Exposure Card */}
          <div className="bg-slate-900/40 backdrop-blur-md rounded-3xl border border-white/5 p-6 flex flex-col min-h-[300px]">
            <h3 className="text-xs uppercase tracking-widest text-slate-400 font-bold w-full text-left mb-6 flex items-center gap-2">
              <CreditCard className="w-4 h-4 text-indigo-400" /> Credit Exposure & Debt
            </h3>
            <div className="space-y-6 flex-1 flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-2xl font-black text-white">{data.exposureLevel} Exposure</p>
                  <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold mt-1">Classification Level</p>
                </div>
                <div className="w-16 h-16 relative">
                  <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                    <circle cx="50" cy="50" r="40" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="8" />
                    <circle cx="50" cy="50" r="40" fill="none" stroke="#818cf8" strokeWidth="8" strokeDasharray="251" strokeDashoffset={251 - (data.exposureScore / 100) * 251} strokeLinecap="round" />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center text-xs font-bold text-indigo-300">
                    {Math.round(data.exposureScore)}
                  </div>
                </div>
              </div>

              <div className="p-4 bg-indigo-500/5 border border-indigo-500/20 rounded-2xl">
                <p className="text-xs text-indigo-300 leading-relaxed font-medium italic">
                  "{data.exposureMessage}"
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4 mt-auto">
                <div className="bg-slate-800/40 p-3 rounded-xl border border-white/5">
                  <p className="text-[10px] text-slate-500 uppercase font-bold tracking-widest mb-1">Structure</p>
                  <p className="text-sm font-bold text-slate-200">{data.debtStructure}</p>
                </div>
                <div className="bg-slate-800/40 p-3 rounded-xl border border-white/5 overflow-hidden">
                  <p className="text-[10px] text-slate-500 uppercase font-bold tracking-widest mb-1">Loans</p>
                  <p className="text-[11px] font-bold text-slate-300 truncate">{data.activeLoanSummary}</p>
                </div>
              </div>
            </div>
          </div>
          
          {/* Radar Profile */}
          <div className="bg-slate-900/40 backdrop-blur-md rounded-3xl border border-white/5 p-6 flex flex-col items-center">
            <h3 className="text-xs uppercase tracking-widest text-slate-400 font-bold w-full text-left mb-4 flex items-center gap-2"><ShieldAlert className="w-4 h-4 text-cyan-400" /> Behavioral Blueprint</h3>
            <div className="w-full h-[250px]">
              <ResponsiveContainer>
                <RadarChart data={radarData} margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
                  <PolarGrid stroke="rgba(255,255,255,0.05)" />
                  <PolarAngleAxis dataKey="subject" tick={{ fill: '#cbd5e1', fontSize: 10 }} />
                  <Radar name="Metrics" dataKey="value" stroke="#0ea5e9" fill="#0ea5e9" fillOpacity={0.2} />
                  <RechartsTooltip contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px', color: '#fff' }} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Bar Chart */}
          <div className="bg-slate-900/40 backdrop-blur-md rounded-3xl border border-white/5 p-6 flex flex-col">
            <h3 className="text-xs uppercase tracking-widest text-slate-400 font-bold w-full text-left mb-6">Severity Drivers</h3>
            <div className="w-full h-[250px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={[
                  { name: 'Credit Util', value: data.creditUtil, color: '#f43f5e', grad: 'url(#grad-red)' },
                  { name: 'EMI Burden', value: data.emiRatio, color: '#38BDF8', grad: 'url(#grad-cyan)' },
                  { name: 'Debt Stress', value: data.debtStress, color: '#A78BFA', grad: 'url(#grad-purple)' }
                ]} layout="vertical" margin={{ top: 0, right: 30, left: 20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="grad-red" x1="0" y1="0" x2="1" y2="0">
                      <stop offset="0%" stopColor="#f43fb0" stopOpacity={0.8} />
                      <stop offset="100%" stopColor="#f43f5e" stopOpacity={1} />
                    </linearGradient>
                    <linearGradient id="grad-cyan" x1="0" y1="0" x2="1" y2="0">
                      <stop offset="0%" stopColor="#38bdf8" stopOpacity={0.8} />
                      <stop offset="100%" stopColor="#0ea5e9" stopOpacity={1} />
                    </linearGradient>
                    <linearGradient id="grad-purple" x1="0" y1="0" x2="1" y2="0">
                      <stop offset="0%" stopColor="#a78bfa" stopOpacity={0.8} />
                      <stop offset="100%" stopColor="#8b5cf6" stopOpacity={1} />
                    </linearGradient>
                    <filter id="glow">
                      <feGaussianBlur stdDeviation="2" result="coloredBlur" />
                      <feMerge>
                        <feMergeNode in="coloredBlur" />
                        <feMergeNode in="SourceGraphic" />
                      </feMerge>
                    </filter>
                  </defs>
                  <XAxis type="number" domain={[0, 100]} hide />
                  <YAxis 
                    dataKey="name" 
                    type="category" 
                    axisLine={false} 
                    tickLine={false} 
                    tick={{ fill: '#CBD5F5', fontSize: 13, fontWeight: 600 }} 
                    width={100} 
                  />
                  <RechartsTooltip 
                    cursor={{ fill: 'rgba(255,255,255,0.03)' }} 
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '12px', boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)' }} 
                    itemStyle={{ color: '#E2E8F0', fontSize: '12px', fontWeight: 'bold' } }
                  />
                  <Bar 
                    dataKey="value" 
                    radius={[0, 6, 6, 0]} 
                    barSize={24}
                    animationDuration={1500}
                    animationEasing="ease-out"
                  >
                    { [
                      { grad: 'url(#grad-red)' },
                      { grad: 'url(#grad-cyan)' },
                      { grad: 'url(#grad-purple)' }
                    ].map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.grad} style={{ filter: 'url(#glow)' }} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Pie Chart */}
          <div className="bg-slate-900/40 backdrop-blur-md rounded-3xl border border-white/5 p-6">
            <h3 className="text-xs uppercase tracking-widest text-slate-400 font-bold w-full text-left mb-2">Liquidity Distribution</h3>
            <div className="w-full h-[200px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={[
                    { name: 'EMI Obligations', value: data.emi, color: '#f59e0b' },
                    { name: 'Credit Card Due', value: data.creditDue, color: '#f43f5e' },
                    { name: 'Liquid Cash', value: remainingIncome > 0 ? remainingIncome : 0, color: '#10b981' },
                  ]} cx="50%" cy="50%" innerRadius={50} outerRadius={80} paddingAngle={2} dataKey="value" stroke="none">
                    {[0,1,2].map((i) => <Cell key={i} fill={['#f59e0b', '#f43f5e', '#10b981'][i]} />)}
                  </Pie>
                  <RechartsTooltip formatter={(v) => `₹${v.toLocaleString()}`} contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex justify-center flex-wrap gap-4 mt-4 text-[11px] font-bold tracking-wider uppercase text-slate-400">
              <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-amber-500" /> EMI</span>
              <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-rose-500" /> Credit</span>
              <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-emerald-500" /> Liquid</span>
            </div>
          </div>

        </motion.div>
      )}

      {/* Tab: Detailed Data Matrix */}
      {activeTab === 'details' && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <DetailCard title="Demographics & Setup">
            <Row label="Customer Age" value={`${data.age} yrs`} />
            <Row label="Account Tenure" value={`${data.tenure} mos`} />
            <Row label="Base Monthly Income" value={`₹${data.income.toLocaleString()}`} />
          </DetailCard>
          
          <DetailCard title="Debt Profiling">
            <Row label="Debt Stress Ratio" value={`${data.debtStress.toFixed(1)}%`} highlight={data.debtStress > 60} />
            <Row label="EMI-to-Income Ratio" value={`${data.emiRatio.toFixed(1)}%`} highlight={data.emiRatio > 40} />
            <Row label="Credit Utilization" value={`${data.creditUtil.toFixed(1)}%`} highlight={data.creditUtil > 70} />
          </DetailCard>

          <DetailCard title="Behavior & Volatility">
            <Row label="Financial Health Score" value={`${data.healthScore.toFixed(0)}/100`} />
            <Row label="Spending Instability" value={`${data.spendingInstability.toFixed(1)}%`} highlight={data.spendingInstability > 40} />
            <Row label="ATM Withdrawals" value={data.atmWithdrawals} />
            <Row label="Avg Bank Balance" value={`₹${data.avgBalance.toLocaleString()}`} />
          </DetailCard>

          <DetailCard title="Critical Flags" alert>
            <Row label="Salary Delay Flag" value={data.salaryDelay === 1 ? "TRIGGERED" : "Clear"} highlight={data.salaryDelay === 1} />
            <Row label="Job Loss Signal" value={data.jobLoss === 1 ? "DETECTED" : "Clear"} highlight={data.jobLoss === 1} />
            <Row label="Financial Shock" value={data.shockFlag === 1 ? "SHOCK OCCURRED" : "Clear"} highlight={data.shockFlag === 1} />
            <Row label="Late Bill Payments" value={data.billDelayCount} highlight={data.billDelayCount > 0} />
          </DetailCard>
        </motion.div>
      )}

    </motion.div>
  );
}

function DetailCard({ title, children, alert }) {
  return (
    <div className={`bg-slate-900/40 backdrop-blur-md p-6 rounded-3xl border ${alert ? 'border-rose-500/20 shadow-[0_4px_20px_rgba(244,63,94,0.05)]' : 'border-white/5'} flex flex-col`}>
      <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-6 border-b border-white/5 pb-3">
        {title}
      </h3>
      <div className="space-y-4">
        {children}
      </div>
    </div>
  );
}

function Row({ label, value, highlight }) {
  return (
    <div className="flex items-center justify-between group">
      <span className="text-sm text-slate-500 font-medium group-hover:text-slate-300 transition-colors">{label}</span>
      <span className={`text-sm font-bold ${highlight ? 'text-rose-400' : 'text-slate-200'} transition-colors`}>{value}</span>
    </div>
  );
}
