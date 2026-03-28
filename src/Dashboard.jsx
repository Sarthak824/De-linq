import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
} from "recharts";

const riskTrend = [
  { week: "W1", risk: 22 },
  { week: "W2", risk: 28 },
  { week: "W3", risk: 41 },
  { week: "W4", risk: 57 },
];

const spendingData = [
  { category: "Dining", value: 40 },
  { category: "Shopping", value: 65 },
  { category: "Utilities", value: 90 },
  { category: "EMI", value: 120 },
];

const dynamicSignalsPool = [
  "Salary credited later than usual",
  "Savings balance declining",
  "Increased ATM withdrawals",
  "Late utility payments",
  "Balance volatility spike detected",
];

const initialCustomers = [
  { id: 1, name: "Rahul Sharma", risk: "High", score: 78, signal: "Salary delay + Savings drawdown" },
  { id: 2, name: "Neha Verma", risk: "Medium", score: 52, signal: "Late utility payments" },
  { id: 3, name: "Amit Patel", risk: "Low", score: 21, signal: "Stable cash flow" },
  { id: 4, name: "Priya Nair", risk: "Low", score: 18, signal: "Consistent income & savings pattern" },
];

const COLORS = ["#f87171", "#fbbf24", "#34d399"];

export default function Dashboard() {
  const [customers, setCustomers] = useState(initialCustomers);
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [showDrilldown, setShowDrilldown] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");
  const [signals, setSignals] = useState([]);

  useEffect(() => {
    const interval = setInterval(() => {
      setCustomers((prev) =>
        prev.map((c) => {
          const hasStressEvent = Math.random() > 0.7;

          const drift = hasStressEvent
            ? Math.random() * 3.5
            : Math.random() * 0.8;

          const newScore = Math.min(95, c.score + drift);
          const newRisk = newScore > 70 ? "High" : newScore > 40 ? "Medium" : "Low";

          return { ...c, score: Number(newScore.toFixed(1)), risk: newRisk };
        })
      );

      const visibleSignals = dynamicSignalsPool.filter(() => Math.random() > 0.4);
      setSignals(visibleSignals);
    }, 2500);

    return () => clearInterval(interval);
  }, []);

  const openIntervention = (customer) => {
    setSelectedCustomer(customer);
    setShowModal(true);
  };

  const high = customers.filter((c) => c.risk === "High").length;
  const medium = customers.filter((c) => c.risk === "Medium").length;
  const low = customers.filter((c) => c.risk === "Low").length;

  const riskMix = [
    { name: "High", value: high },
    { name: "Medium", value: medium },
    { name: "Low", value: low },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex">
      <div className="w-64 bg-slate-900 border-r border-slate-800 p-6 space-y-6">
        <div>
          <h2 className="text-xl font-bold bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">
            DelinqAI
          </h2>
          <p className="text-xs text-slate-500">Early Risk Intelligence</p>
        </div>

        <div className="space-y-2 text-sm">
          <NavItem label="Overview" active={activeTab === "overview"} onClick={() => setActiveTab("overview")} />
          <NavItem label="Users" active={activeTab === "users"} onClick={() => setActiveTab("users")} />
        </div>
      </div>

      <div className="flex-1 p-8 space-y-6">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-3xl font-bold mb-1">Pre-Delinquency Intervention Engine</h1>
          <p className="text-slate-400 text-sm">Detect financial stress weeks before default</p>
        </motion.div>

        <div className="bg-gradient-to-r from-indigo-500/10 to-cyan-500/10 border border-indigo-500/20 rounded-xl p-4 text-sm">
          ⚡ Live Engine Running • Signal-Driven Risk Recalibration
        </div>

        <AnimatePresence mode="wait">
          {activeTab === "overview" && (
            <motion.div key="overview" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-6">
              <MetricsGrid />

              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <ChartCard title="Portfolio Risk Trend">
                  <ResponsiveContainer width="100%" height={200}>
                    <LineChart data={riskTrend}>
                      <XAxis dataKey="week" stroke="#94a3b8" />
                      <YAxis stroke="#94a3b8" />
                      <Tooltip />
                      <Line type="monotone" dataKey="risk" stroke="#818cf8" strokeWidth={3} />
                    </LineChart>
                  </ResponsiveContainer>
                </ChartCard>

                <ChartCard title="Portfolio Risk Mix">
                  <ResponsiveContainer width="100%" height={200}>
                    <PieChart>
                      <Pie data={riskMix} dataKey="value" outerRadius={70}>
                        {riskMix.map((_, i) => (
                          <Cell key={i} fill={COLORS[i]} />
                        ))}
                      </Pie>
                    </PieChart>
                  </ResponsiveContainer>
                </ChartCard>

                <ChartCard title="AI Recommendation Engine">
                  <div className="space-y-2 text-sm">
                    <InfoBox label="Best Action" value="Offer Repayment Moratorium" highlight />
                    <InfoBox label="Risk Trajectory" value="Increasing (+12%)" />
                    <InfoBox label="Confidence" value="High (91%)" />
                  </div>
                </ChartCard>

                <ChartCard title="Early Warning Signals">
                  <div className="space-y-2 text-sm text-slate-400">
                    {signals.map((s, i) => (
                      <div key={i} className="bg-slate-800 p-2 rounded-lg">• {s}</div>
                    ))}
                  </div>
                </ChartCard>
              </div>
            </motion.div>
          )}

          {activeTab === "users" && (
            <motion.div key="users" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-4">
              <h2 className="font-semibold">At-Risk Users (Live)</h2>

              {customers.map((c) => (
                <motion.div key={c.id} layout className="flex justify-between items-center p-4 bg-slate-900 border border-slate-800 rounded-xl">
                  <div>
                    <p className="font-medium">{c.name}</p>
                    <p className="text-sm text-slate-400">{c.signal}</p>
                  </div>

                  <div className="flex items-center gap-3">
                    <RiskBadge risk={c.risk} score={c.score} />

                    <button className="px-3 py-1 text-sm bg-slate-800 rounded-lg" onClick={() => setShowDrilldown(c)}>
                      View
                    </button>

                    <button className="px-3 py-1 text-sm bg-indigo-500 rounded-lg" onClick={() => openIntervention(c)}>
                      Intervene
                    </button>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {showModal && (
            <Modal onClose={() => setShowModal(false)} title="Intervention Strategy">
              <div className="space-y-3 text-sm">
                <InfoBox
                  label="AI Rationale"
                  value="Salary delay detected • Savings drawdown accelerating • EMI / income ratio rising"
                  highlight
                />

                <ActionButton label="Offer Repayment Moratorium" primary />
                <ActionButton label="Short-Term EMI Reduction" />
                <ActionButton label="Adjust Repayment Schedule" />
                <ActionButton label="Convert to Interest-Only Plan" />
                <ActionButton label="Deferred Payment Arrangement" />
                
                <ActionButton label="Debt Restructuring Program" />
                <ActionButton label="Auto-Debit Retry Alignment" />
              </div>
            </Modal>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {showDrilldown && (
            <Modal onClose={() => setShowDrilldown(null)} title="Analytics">
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={spendingData}>
                  <XAxis dataKey="category" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip />
                  <Bar dataKey="value" />
                </BarChart>
              </ResponsiveContainer>
            </Modal>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

function NavItem({ label, active, onClick }) {
  return (
    <div
      onClick={onClick}
      className={`px-3 py-2 rounded-lg cursor-pointer transition ${
        active ? "bg-indigo-500/20 text-indigo-300" : "text-slate-400"
      }`}
    >
      {label}
    </div>
  );
}

function MetricsGrid() {
  return (
    <div className="grid grid-cols-4 gap-4">
      <Metric label="High Risk Users" value="124" />
      <Metric label="Avg Risk Score" value="46" />
      <Metric label="Loss Prevented" value="₹8.2M" />
      <Metric label="Signals" value="Live" />
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
      <p className="text-sm text-slate-400">{label}</p>
      <p className="text-xl font-semibold">{value}</p>
    </div>
  );
}

function ChartCard({ title, children }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4">
      <h2 className="font-semibold mb-3">{title}</h2>
      {children}
    </div>
  );
}

function RiskBadge({ risk, score }) {
  const trend = Math.random() > 0.5 ? "↑" : "→";

  return (
    <div className="px-3 py-1 rounded-lg text-sm bg-slate-800">
      {risk} • {score} {trend}
    </div>
  );
}

function InfoBox({ label, value, highlight }) {
  return (
    <div className={`p-3 rounded-xl ${highlight ? "bg-indigo-500/10" : "bg-slate-800"}`}>
      <p className="text-xs text-slate-400">{label}</p>
      <p>{value}</p>
    </div>
  );
}

function Modal({ children, onClose, title }) {
  return (
    <motion.div
      className="fixed inset-0 bg-black/60 flex items-center justify-center"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <motion.div
        className="bg-slate-900 border border-slate-800 rounded-2xl p-6 w-[460px] max-h-[80vh] overflow-y-auto"
        initial={{ scale: 0.9 }}
        animate={{ scale: 1 }}
        exit={{ scale: 0.9 }}
      >
        <div className="flex justify-between mb-4">
          <h2 className="font-semibold">{title}</h2>
          <button onClick={onClose}>✕</button>
        </div>
        {children}
      </motion.div>
    </motion.div>
  );
}

function ActionButton({ label, primary }) {
  return (
    <button
      className={`w-full py-2 rounded-lg transition ${
        primary ? "bg-indigo-500 hover:bg-indigo-400" : "bg-slate-800 hover:bg-slate-700"
      }`}
    >
      {label}
    </button>
  );
}
