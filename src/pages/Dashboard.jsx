import { useState, useEffect } from "react";
import { Users, AlertTriangle, Activity, Loader2 } from "lucide-react";
import KPICard from "../components/dashboard/KPICard";
import FinancialStressChart from "./FinancialStressChart";
import RiskTable from "../components/dashboard/RiskTable";
import AIInsights from "../components/dashboard/AIInsights";

// --- Mock Data ---
const mockKPIs = {
  totalCustomers: "124,592",
  atRisk: "12,430",
  avgRisk: 68, // new ML-based probability percentage
};

const mockChartData = {
  dates: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
  stressLevels: [45, 52, 48, 65, 70, 68, 85],
};

const mockRiskCustomers = [
  { id: "CUST-101000", riskScore: 92, category: "High", keyDriver: "High EMI burden", lastActivity: "2 mins ago", action: "Review Credit" },
  { id: "CUST-101001", riskScore: 85, category: "High", keyDriver: "Frequent late payments", lastActivity: "1 hour ago", action: "Initiate Restructure" },
  { id: "CUST-101002", riskScore: 78, category: "Medium", keyDriver: "Salary delay detected", lastActivity: "3 hours ago", action: "Send EMI Reminder" },
  { id: "CUST-101003", riskScore: 88, category: "High", keyDriver: "Spending spike", lastActivity: "5 hours ago", action: "Schedule Call" },
];

const mockInsights = [
  { type: "alert", message: "Spike in EMI defaults in salaried segment observed across Tier 2 cities.", time: "1 hour ago" },
  { type: "trend", message: "Customer intervention success rate improved by 4.2% following the new automated SMS campaign.", time: "3 hours ago" },
  { type: "info", message: "145 customers are eligible for the pre-approved restructuring scheme.", time: "5 hours ago" },
  { type: "alert", message: "High variance in credit utilization for 500+ unverified accounts.", time: "6 hours ago" },
  { type: "trend", message: "Overall risk prediction accuracy increased by 1.8% in the latest model retrain.", time: "12 hours ago" },
];
// -----------------

export default function Dashboard() {
  const [stats, setStats] = useState({ totalCustomers: "0", atRisk: "0", avgRisk: 0 });
  const [topRisks, setTopRisks] = useState([]);
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [statsRes, risksRes, insightsRes] = await Promise.all([
          fetch('http://127.0.0.1:8000/portfolio-summary'),
          fetch('http://127.0.0.1:8000/analytics/top-risks?limit=6'),
          fetch('http://127.0.0.1:8000/analytics/insights')
        ]);
        
        const statsData = await statsRes.json();
        const risksData = await risksRes.json();
        const insightsData = await insightsRes.json();
        
        setStats({
          totalCustomers: (statsData.total_customers || 0).toLocaleString(),
          atRisk: (statsData.at_risk_customers || 0).toLocaleString(),
          avgRisk: Math.round((statsData.average_risk_score || 0) * 100)
        });
        
        setInsights(insightsData);
        
        setTopRisks(risksData.customers.map(c => {
          let drivers = c.top_reason_codes || "Multi-factor risk";
          if (typeof drivers === 'string') drivers = drivers.split(',')[0];
          else if (Array.isArray(drivers) && drivers.length > 0) drivers = drivers[0];
          else drivers = "Multi-factor risk";

          return {
            id: c.customer_id,
            riskScore: Math.round((c.risk_score || 0) * 100),
            category: c.risk_band || "Low",
            keyDriver: drivers.replace(/_/g, ' '),
            lastActivity: "Updated now",
            action: "Review Profile"
          };
        }));
      } catch (err) {
        console.error("Dashboard fetch failed:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <Loader2 className="w-12 h-12 text-cyan-500 animate-spin" />
        <p className="text-slate-400 font-medium">Synchronizing Portfolio Intelligence...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500 pb-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Dashboard</h1>
          <p className="text-slate-400 mt-1">Overview of risk metrics and recent activity.</p>
        </div>
        <div className="flex gap-3">
          <button className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg border border-slate-700 transition-colors text-sm font-medium">
            Export Report
          </button>
          <button className="px-4 py-2 bg-cyan-500 hover:bg-cyan-400 text-slate-950 rounded-lg transition-colors text-sm font-medium shadow-[0_0_15px_rgba(6,182,212,0.3)]">
            Run AI Analysis
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <KPICard 
          title="Total Customers" 
          value={stats.totalCustomers} 
          trend={2.4} 
          trendLabel="vs last month" 
          icon={Users} 
        />
        <KPICard 
          title="At-Risk Customers" 
          value={stats.atRisk} 
          trend={12.5} 
          trendLabel="vs last month" 
          icon={AlertTriangle} 
          trendUpIsGood={false}
        />
        <KPICard 
          title="Average Risk Score" 
          value={`${stats.avgRisk}%`} 
          trend={1.2} 
          trendLabel="vs last month" 
          icon={Activity} 
          trendUpIsGood={false}
          valueColor="text-amber-400"
          secondaryLabel="Medium Risk"
          tooltip="Average predicted probability of default across all customers"
          progressValue={stats.avgRisk}
          progressColor="bg-amber-400"
        />
      </div>

      {/* Analytics Main */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-3 min-h-[400px]">
          <FinancialStressChart data={mockChartData} />
        </div>
      </div>

      {/* Table & Insights Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <RiskTable customers={topRisks} />
        </div>
        <div className="lg:col-span-1 h-full min-h-[350px]">
          <AIInsights insights={insights} />
        </div>
      </div>
    </div>
  );
}
