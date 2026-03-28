import React, { useMemo, useState } from 'react';
import { ShieldAlert, Info, TrendingUp, AlertTriangle, Search, Filter, Download, UserMinus, ArrowUpDown } from 'lucide-react';

const generateMockData = (count) => {
  return Array.from({ length: count }, (_, i) => {
    // Generate base risk indicators
    const isHighRisk = Math.random() > 0.8;
    const isMediumRisk = !isHighRisk && Math.random() > 0.6;
    
    // CUSTOMER PROFILE
    const customer_id = `CUST-${(101000 + i).toString()}`;
    const age = 22 + Math.floor(Math.random() * 45);
    const account_tenure = `${1 + Math.floor(Math.random() * 10)} yrs`;
    const label = isHighRisk ? "High Risk" : isMediumRisk ? "Medium Risk" : "Healthy";

    // INCOME & OBLIGATIONS
    const monthly_income = 45000 + Math.floor(Math.random() * 150000);
    const emi = isHighRisk ? Math.floor(monthly_income * (0.5 + Math.random() * 0.3)) : Math.floor(monthly_income * (0.1 + Math.random() * 0.3));
    const credit_card_due = isHighRisk ? 50000 + Math.floor(Math.random() * 150000) : Math.floor(Math.random() * 20000);
    const total_obligations = emi + credit_card_due;

    // RISK RATIOS
    const emi_to_income_ratio = Math.round((emi / monthly_income) * 100);
    const debt_stress_ratio = Math.round((total_obligations / monthly_income) * 100);
    const credit_utilization = isHighRisk ? 75 + Math.floor(Math.random() * 24) : 10 + Math.floor(Math.random() * 40);

    // BEHAVIORAL SIGNALS
    const atm_withdrawals = isHighRisk ? 5 + Math.floor(Math.random() * 8) : Math.floor(Math.random() * 3);
    const spending_change = Math.floor(Math.random() * 60) - 20; // -20% to +40%
    const spending_instability = isHighRisk ? "High" : isMediumRisk ? "Moderate" : "Low";

    // PAYMENT BEHAVIOR
    const missed_payments = isHighRisk ? 1 + Math.floor(Math.random() * 4) : 0;
    const bill_delay_count = isHighRisk ? 2 + Math.floor(Math.random() * 5) : (isMediumRisk ? 1 : 0);
    const payment_discipline = isHighRisk ? "Erratic" : (isMediumRisk ? "Delayed" : "On-Time");
    const salary_delay = Math.random() > 0.85 ? "Yes" : "No";

    // FINANCIAL STABILITY
    const avg_balance = isHighRisk ? Math.floor(monthly_income * 0.2) : Math.floor(monthly_income * 1.5);
    const balance_drop_ratio = isHighRisk ? 40 + Math.floor(Math.random() * 50) : Math.floor(Math.random() * 15);
    const liquidity_buffer = avg_balance;
    const stability_score = isHighRisk ? Math.floor(Math.random() * 40) : 60 + Math.floor(Math.random() * 40);

    // RISK INTELLIGENCE
    const financial_health_score = isHighRisk ? Math.floor(Math.random() * 40) : 60 + Math.floor(Math.random() * 40);
    const shock_flag = isHighRisk && Math.random() > 0.5 ? "Yes" : "No";
    const job_loss = isHighRisk && Math.random() > 0.8 ? "Suspected" : "No";
    const credit_dependency = credit_utilization > 80 ? "High" : "Normal";
    const early_risk_flag = (!isHighRisk && debt_stress_ratio > 50) ? "Yes" : "No";

    return {
      customer_id, age, monthly_income, emi, credit_card_due, emi_to_income_ratio, credit_utilization,
      missed_payments, salary_delay, job_loss, avg_balance, balance_drop_ratio, atm_withdrawals,
      spending_change, bill_delay_count, account_tenure, label, total_obligations, debt_stress_ratio,
      liquidity_buffer, spending_instability, payment_discipline, financial_health_score, shock_flag,
      credit_dependency, early_risk_flag, stability_score
    };
  });
};

const ProgressBar = ({ value, type }) => {
  let colorClass = 'bg-cyan-500';
  if (type === 'health' || type === 'stability') {
    colorClass = value < 40 ? 'bg-rose-500' : value < 70 ? 'bg-amber-500' : 'bg-emerald-500';
  } else if (type === 'utilization') {
    colorClass = value > 80 ? 'bg-rose-500' : value > 50 ? 'bg-amber-500' : 'bg-emerald-500';
  }

  return (
    <div className="flex items-center gap-2">
      <span className="w-8 text-right font-medium">{value}{type === 'utilization' ? '%' : ''}</span>
      <div className="w-16 h-1.5 bg-slate-800 rounded-full overflow-hidden flex-shrink-0">
        <div className={`h-full rounded-full ${colorClass}`} style={{ width: `${Math.min(100, Math.max(0, value))}%` }} />
      </div>
    </div>
  );
};

const PillBadge = ({ value, type }) => {
  if (!value || value === "No" || value === "Normal" || value === "Healthy" || value === "On-Time" || value === "Low") {
    return <span className="text-slate-400">{value}</span>;
  }
  
  const isHighRisk = value === "Yes" || value === "High" || value === "Erratic" || value === "High Risk" || value === "Suspected";
  const isMediumRisk = value === "Medium Risk" || value === "Moderate" || value === "Delayed";
  
  const colorClass = isHighRisk 
    ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' 
    : isMediumRisk 
      ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' 
      : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
      
  return (
    <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border ${colorClass}`}>
      {value}
    </span>
  );
}

export default function Customers() {
  const [searchTerm, setSearchTerm] = useState('');
  const [riskFilter, setRiskFilter] = useState('All');
  const [shockFilter, setShockFilter] = useState('All');
  
  // Sort State: { key: column_name, direction: 'asc' | 'desc' }
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });

  const mockData = useMemo(() => generateMockData(50), []);

  const handleSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  const processedData = useMemo(() => {
    // 1. Filter
    let filtered = mockData.filter(item => {
      const matchSearch = item.customer_id.toLowerCase().includes(searchTerm.toLowerCase());
      const matchRisk = riskFilter === 'All' || item.label === riskFilter;
      const matchShock = shockFilter === 'All' || item.shock_flag === shockFilter;
      return matchSearch && matchRisk && matchShock;
    });

    // 2. Sort
    if (sortConfig.key) {
      filtered.sort((a, b) => {
        let aValue = a[sortConfig.key];
        let bValue = b[sortConfig.key];
        
        // Handle strings safely
        if (typeof aValue === 'string') {
          aValue = aValue.toLowerCase();
          bValue = bValue.toLowerCase();
          if (aValue < bValue) return sortConfig.direction === 'asc' ? -1 : 1;
          if (aValue > bValue) return sortConfig.direction === 'asc' ? 1 : -1;
          return 0;
        }
        
        // Handle numbers
        return sortConfig.direction === 'asc' ? aValue - bValue : bValue - aValue;
      });
    }

    return filtered;
  }, [mockData, searchTerm, riskFilter, shockFilter, sortConfig]);

  const Th = ({ label, sortKey, align = "left" }) => (
    <th 
      className={`px-4 py-3 text-xs font-bold text-slate-300 uppercase tracking-wider whitespace-nowrap cursor-pointer hover:bg-slate-700/50 transition-colors ${align === 'right' ? 'text-right' : 'text-left'}`}
      onClick={() => handleSort(sortKey)}
    >
      <div className={`flex items-center gap-1 ${align === 'right' ? 'justify-end' : ''}`}>
        {label}
        {sortConfig.key === sortKey && (
          <ArrowUpDown className={`w-3 h-3 ${sortConfig.direction === 'asc' ? 'text-cyan-400' : 'text-cyan-400 rotate-180'} transition-transform`} />
        )}
        {sortConfig.key !== sortKey && <ArrowUpDown className="w-3 h-3 text-slate-600 opacity-0 group-hover:opacity-100" />}
      </div>
    </th>
  );

  const formatCurrency = (val) => `₹${val.toLocaleString()}`;

  return (
    <div className="flex flex-col h-full space-y-6 animate-in fade-in duration-500 pb-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 shrink-0 px-1">
        <div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-blue-500 tracking-tight">
            Customer Intelligence
          </h1>
          <p className="text-slate-400 mt-1">Bank-grade financial risk datagrid with high-density metrics.</p>
        </div>
        <div className="flex gap-3">
          <button className="flex items-center gap-2 px-4 py-2 bg-slate-800/50 hover:bg-slate-700/50 border border-slate-700/50 rounded-xl text-slate-300 transition-all text-sm">
            <Download className="w-4 h-4" />
            Export CSV
          </button>
        </div>
      </div>

      {/* Toolbar */}
      <div className="flex flex-wrap items-center gap-4 bg-slate-900/40 backdrop-blur-md border border-white/5 rounded-2xl p-4 shrink-0 shadow-xl">
        <div className="relative flex-1 min-w-[280px] max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input 
            type="text" 
            placeholder="Search Customer ID..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-800/40 border border-slate-700/50 rounded-xl py-2 pl-10 pr-4 text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-cyan-500/50 transition-colors text-sm"
          />
        </div>
        <div className="flex items-center gap-2 border-l border-white/10 pl-4">
          <span className="text-xs text-slate-500 font-semibold uppercase tracking-wider">Filters:</span>
          <select 
            value={riskFilter} 
            onChange={e => setRiskFilter(e.target.value)}
            className="bg-slate-800/40 border border-slate-700/50 rounded-xl py-1.5 px-3 text-sm text-slate-300 focus:outline-none focus:border-cyan-500/50"
          >
            <option value="All">Risk: All</option>
            <option value="High Risk">High Risk</option>
            <option value="Medium Risk">Medium Risk</option>
            <option value="Healthy">Healthy</option>
          </select>
          <select 
            value={shockFilter} 
            onChange={e => setShockFilter(e.target.value)}
            className="bg-slate-800/40 border border-slate-700/50 rounded-xl py-1.5 px-3 text-sm text-slate-300 focus:outline-none focus:border-cyan-500/50"
          >
            <option value="All">Shock Flag: All</option>
            <option value="Yes">Shock: Yes</option>
            <option value="No">Shock: No</option>
          </select>
        </div>
      </div>

      {/* Data Table */}
      <div className="flex-1 min-h-0 bg-slate-900/60 backdrop-blur-xl border border-white/5 rounded-2xl overflow-hidden shadow-2xl flex flex-col">
        <div className="overflow-auto flex-1 custom-scrollbar relative">
          <table className="w-full text-left border-collapse" style={{ minWidth: '3200px' }}>
            <thead className="sticky top-0 z-20">
              {/* GROUP HEADERS */}
              <tr className="bg-slate-800/95 backdrop-blur-md border-b border-white/10 shadow-lg">
                <th colSpan="4" className="px-4 py-2 text-[10px] font-bold text-cyan-400 uppercase tracking-widest bg-cyan-900/20 border-r border-white/5">Customer Profile</th>
                <th colSpan="4" className="px-4 py-2 text-[10px] font-bold text-emerald-400 uppercase tracking-widest bg-emerald-900/20 border-r border-white/5">Income & Obligations</th>
                <th colSpan="3" className="px-4 py-2 text-[10px] font-bold text-amber-500 uppercase tracking-widest bg-amber-900/20 border-r border-white/5">Risk Ratios</th>
                <th colSpan="3" className="px-4 py-2 text-[10px] font-bold text-purple-400 uppercase tracking-widest bg-purple-900/20 border-r border-white/5">Behavioral Signals</th>
                <th colSpan="4" className="px-4 py-2 text-[10px] font-bold text-orange-400 uppercase tracking-widest bg-orange-900/20 border-r border-white/5">Payment Behavior</th>
                <th colSpan="4" className="px-4 py-2 text-[10px] font-bold text-blue-400 uppercase tracking-widest bg-blue-900/20 border-r border-white/5">Financial Stability</th>
                <th colSpan="5" className="px-4 py-2 text-[10px] font-bold text-rose-400 uppercase tracking-widest bg-rose-900/20">Risk Intelligence</th>
              </tr>
              {/* COLUMN HEADERS */}
              <tr className="bg-slate-800/90 backdrop-blur-md border-b border-white/10 select-none group">
                {/* Customer Profile */}
                <Th label="Customer ID" sortKey="customer_id" />
                <Th label="Age" sortKey="age" align="right" />
                <Th label="Tenure" sortKey="account_tenure" />
                <Th label="Label" sortKey="label" />
                
                {/* Income & Obligations */}
                <Th label="Monthly Income" sortKey="monthly_income" align="right" />
                <Th label="EMI" sortKey="emi" align="right" />
                <Th label="CC Due" sortKey="credit_card_due" align="right" />
                <Th label="Total Oblig." sortKey="total_obligations" align="right" />
                
                {/* Risk Ratios */}
                <Th label="EMI / Income" sortKey="emi_to_income_ratio" align="right" />
                <Th label="Debt Stress" sortKey="debt_stress_ratio" align="right" />
                <Th label="Credit Util." sortKey="credit_utilization" />
                
                {/* Behavioral Signals */}
                <Th label="ATM W/D" sortKey="atm_withdrawals" align="right" />
                <Th label="Spend Change" sortKey="spending_change" align="right" />
                <Th label="Spend Instability" sortKey="spending_instability" />

                {/* Payment Behavior */}
                <Th label="Missed Pmts" sortKey="missed_payments" align="right" />
                <Th label="Bill Delays" sortKey="bill_delay_count" align="right" />
                <Th label="Pmt Discipline" sortKey="payment_discipline" />
                <Th label="Salary Delay" sortKey="salary_delay" />

                {/* Financial Stability */}
                <Th label="Avg Balance" sortKey="avg_balance" align="right" />
                <Th label="Drop Ratio" sortKey="balance_drop_ratio" align="right" />
                <Th label="Liq. Buffer" sortKey="liquidity_buffer" align="right" />
                <Th label="Stability Score" sortKey="stability_score" />

                {/* Risk Intelligence */}
                <Th label="Health Score" sortKey="financial_health_score" />
                <Th label="Shock Flag" sortKey="shock_flag" />
                <Th label="Job Loss" sortKey="job_loss" />
                <Th label="Credit Dep." sortKey="credit_dependency" />
                <Th label="Early Risk" sortKey="early_risk_flag" />
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {processedData.length > 0 ? (
                processedData.map((row) => (
                  <tr key={row.customer_id} className="hover:bg-slate-800/40 transition-colors cursor-default whitespace-nowrap">
                    {/* Customer Profile */}
                    <td className="px-4 py-3 text-sm font-mono text-cyan-400 border-r border-white/5">{row.customer_id}</td>
                    <td className="px-4 py-3 text-sm text-slate-300 text-right">{row.age}</td>
                    <td className="px-4 py-3 text-sm text-slate-300">{row.account_tenure}</td>
                    <td className="px-4 py-3 text-sm border-r border-white/5"><PillBadge value={row.label} /></td>

                    {/* Income & Obligations */}
                    <td className="px-4 py-3 text-sm text-slate-300 text-right font-medium">{formatCurrency(row.monthly_income)}</td>
                    <td className="px-4 py-3 text-sm text-amber-200/80 text-right">{formatCurrency(row.emi)}</td>
                    <td className="px-4 py-3 text-sm text-rose-200/80 text-right">{formatCurrency(row.credit_card_due)}</td>
                    <td className="px-4 py-3 text-sm text-slate-100 font-bold text-right border-r border-white/5">{formatCurrency(row.total_obligations)}</td>

                    {/* Risk Ratios */}
                    <td className="px-4 py-3 text-sm text-right">
                      <span className={row.emi_to_income_ratio > 40 ? 'text-rose-400 font-bold' : 'text-slate-300'}>{row.emi_to_income_ratio}%</span>
                    </td>
                    <td className="px-4 py-3 text-sm text-right">
                      <span className={row.debt_stress_ratio > 60 ? 'text-rose-400 font-bold' : 'text-slate-300'}>{row.debt_stress_ratio}%</span>
                    </td>
                    <td className="px-4 py-3 text-sm border-r border-white/5">
                      <ProgressBar value={row.credit_utilization} type="utilization" />
                    </td>

                    {/* Behavioral Signals */}
                    <td className="px-4 py-3 text-sm text-right">
                      <span className={row.atm_withdrawals > 5 ? 'text-amber-400 font-bold' : 'text-slate-300'}>{row.atm_withdrawals}</span>
                    </td>
                    <td className="px-4 py-3 text-sm text-right">
                      <span className={row.spending_change > 20 ? 'text-rose-400 font-bold' : row.spending_change < -10 ? 'text-emerald-400' : 'text-slate-300'}>
                        {row.spending_change > 0 ? '+' : ''}{row.spending_change}%
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm border-r border-white/5"><PillBadge value={row.spending_instability} /></td>

                    {/* Payment Behavior */}
                    <td className="px-4 py-3 text-sm text-right">
                      <span className={row.missed_payments > 0 ? 'text-rose-500 font-bold' : 'text-slate-400'}>{row.missed_payments}</span>
                    </td>
                    <td className="px-4 py-3 text-sm text-right">
                      <span className={row.bill_delay_count > 1 ? 'text-amber-400 font-bold' : 'text-slate-400'}>{row.bill_delay_count}</span>
                    </td>
                    <td className="px-4 py-3 text-sm"><PillBadge value={row.payment_discipline} /></td>
                    <td className="px-4 py-3 text-sm border-r border-white/5"><PillBadge value={row.salary_delay} /></td>

                    {/* Financial Stability */}
                    <td className="px-4 py-3 text-sm text-slate-300 text-right font-medium">{formatCurrency(row.avg_balance)}</td>
                    <td className="px-4 py-3 text-sm text-right">
                      <span className={row.balance_drop_ratio > 30 ? 'text-rose-400 font-bold' : 'text-slate-300'}>{row.balance_drop_ratio}%</span>
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-300 text-right">{formatCurrency(row.liquidity_buffer)}</td>
                    <td className="px-4 py-3 text-sm border-r border-white/5">
                      <ProgressBar value={row.stability_score} type="stability" />
                    </td>

                    {/* Risk Intelligence */}
                    <td className="px-4 py-3 text-sm">
                      <ProgressBar value={row.financial_health_score} type="health" />
                    </td>
                    <td className="px-4 py-3 text-sm"><PillBadge value={row.shock_flag} /></td>
                    <td className="px-4 py-3 text-sm"><PillBadge value={row.job_loss} /></td>
                    <td className="px-4 py-3 text-sm"><PillBadge value={row.credit_dependency} /></td>
                    <td className="px-4 py-3 text-sm"><PillBadge value={row.early_risk_flag} /></td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="27" className="px-6 py-24 text-center">
                    <div className="flex flex-col items-center gap-3 text-slate-500">
                      <div className="p-4 bg-slate-800/50 rounded-full border border-white/5 shadow-inner">
                        <UserMinus className="w-8 h-8 opacity-50" />
                      </div>
                      <p className="text-lg font-medium text-slate-300">No Target Profiles Found</p>
                      <p className="text-sm">Adjust search or filters to see results.</p>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        
        {/* Footer info */}
        <div className="p-3 border-t border-white/5 bg-slate-800/30 text-xs text-slate-500 flex justify-between items-center shrink-0">
          <p>Displaying {processedData.length} intelligent records</p>
          <div className="flex gap-4">
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 bg-rose-500/20 border border-rose-500/50 rounded-sm" /> High Risk</span>
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 bg-amber-500/20 border border-amber-500/50 rounded-sm" /> Medium Risk</span>
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 bg-emerald-500/20 border border-emerald-500/50 rounded-sm" /> Healthy</span>
          </div>
        </div>
      </div>
    </div>
  );
}

