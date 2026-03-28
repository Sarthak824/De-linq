import React, { useMemo, useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ShieldAlert, Info, TrendingUp, AlertTriangle, Search, Filter, Download, UserMinus, ArrowUpDown, Loader2 } from 'lucide-react';

const ProgressBar = ({ value, type }) => {
  // Normalize value to 0-100 scale if it's currently 0-1
  const numericValue = Number(value) || 0;
  const displayValue = numericValue <= 1 && numericValue > 0 ? (numericValue * 100) : numericValue;
  const roundedValue = Math.min(100, Math.max(0, Number(displayValue.toFixed(1))));

  let colorClass = 'bg-cyan-500';
  if (type === 'health' || type === 'stability') {
    colorClass = roundedValue < 40 ? 'bg-rose-500' : roundedValue < 70 ? 'bg-amber-500' : 'bg-emerald-500';
  } else if (type === 'utilization') {
    colorClass = roundedValue > 80 ? 'bg-rose-500' : roundedValue > 50 ? 'bg-amber-500' : 'bg-emerald-500';
  }

  return (
    <div className="flex items-center gap-2">
      <span className="w-10 text-right font-mono text-[10px] text-slate-400">{roundedValue}{type === 'utilization' ? '%' : ''}</span>
      <div className="w-12 h-1 bg-slate-800 rounded-full overflow-hidden flex-shrink-0">
        <div className={`h-full rounded-full ${colorClass}`} style={{ width: `${roundedValue}%` }} />
      </div>
    </div>
  );
};

const PillBadge = ({ value, type }) => {
  if (!value || value === "No" || value === "Normal" || value === "Healthy" || value === "On-Time" || value === "Low") {
    return <span className="text-slate-400">{value}</span>;
  }
  
  const isHighRisk = value === "Yes" || value === "High" || value === "Erratic" || value === "High Risk" || value === "Suspected";
  const isMediumRisk = value === "Medium Risk" || value === "Moderate" || value === "Delayed" || value === "Medium";
  
  const colorClass = isHighRisk 
    ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' 
    : isMediumRisk 
      ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' 
      : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
      
  const displayValue = typeof value === 'number' ? value.toFixed(1) : value;

  return (
    <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border ${colorClass}`}>
      {displayValue}
    </span>
  );
}

export default function Customers() {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [riskFilter, setRiskFilter] = useState('All');
  const [shockFilter, setShockFilter] = useState('All');
  
  // Sort State: { key: column_name, direction: 'asc' | 'desc' }
  const [sortConfig, setSortConfig] = useState({ key: 'risk_score', direction: 'desc' });

  useEffect(() => {
    const fetchCustomers = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/customers?limit=1000');
        const data = await response.json();
        // Backend returns { customers: [...] }
        setCustomers(data.customers || []);
      } catch (err) {
        console.error("Failed to fetch customers:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchCustomers();
  }, []);

  const handleSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  const processedData = useMemo(() => {
    // 1. Filter
    let filtered = customers.filter(item => {
      const customerId = item.customer_id || "";
      const matchSearch = customerId.toLowerCase().includes(searchTerm.toLowerCase());
      
      // Backend uses 'High', 'Medium', 'Low'
      const matchRisk = riskFilter === 'All' || item.risk_band === riskFilter;
      
      // Backend uses 1 and 0 for shock_flag
      const shockVal = item.shock_flag === 1 ? 'Yes' : 'No';
      const matchShock = shockFilter === 'All' || shockVal === shockFilter;
      
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
  }, [customers, searchTerm, riskFilter, shockFilter, sortConfig]);

  const Th = ({ label, sortKey, align = "left", tooltip }) => (
    <th 
      className={`px-4 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest whitespace-nowrap cursor-pointer hover:bg-white/5 transition-all group ${align === 'right' ? 'text-right' : 'text-left'}`}
      onClick={() => handleSort(sortKey)}
    >
      <div className={`flex items-center gap-1.5 ${align === 'right' ? 'justify-end' : ''} relative`}>
        {label}
        {tooltip && (
          <div className="opacity-0 group-hover:opacity-100 absolute top-full left-0 mt-2 w-48 p-3 bg-slate-900 border border-white/10 rounded-xl shadow-2xl pointer-events-none transition-all z-[100] transform -translate-y-1 group-hover:translate-y-0">
            <p className="normal-case text-[10px] leading-relaxed font-medium text-slate-300 tracking-tight whitespace-normal">{tooltip}</p>
          </div>
        )}
        {sortConfig.key === sortKey && (
          <ArrowUpDown className={`w-3 h-3 ${sortConfig.direction === 'asc' ? 'text-cyan-400' : 'text-cyan-400 rotate-180'} transition-transform`} />
        )}
        {sortConfig.key !== sortKey && <ArrowUpDown className="w-3 h-3 text-slate-600 opacity-0 group-hover:opacity-100" />}
      </div>
    </th>
  );

  const formatCurrency = (val) => {
    if (val === null || val === undefined) return "₹0";
    return `₹${Number(val).toLocaleString()}`;
  };

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
            <option value="High">High Risk</option>
            <option value="Medium">Medium Risk</option>
            <option value="Low">Healthy</option>
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
                <Th label="Risk Band" sortKey="risk_band" />
                
                {/* Income & Obligations */}
                <Th label="Monthly Income" sortKey="monthly_income" align="right" />
                <Th label="EMI" sortKey="emi" align="right" />
                <Th label="CC Due" sortKey="credit_card_due" align="right" />
                <Th label="Total Oblig." sortKey="total_obligations" align="right" />
                
                {/* Risk Ratios */}
                <Th label="EMI / Income" sortKey="emi_to_income_ratio" align="right" tooltip="Relationship between fixed monthly installments and base income. >45% is critical." />
                <Th label="Debt Stress" sortKey="debt_stress_ratio" align="right" tooltip="Composite stress based on credit cards, personal loans, and buy-now-pay-later exposure." />
                <Th label="Credit Util." sortKey="credit_utilization" tooltip="Percent of limit used across all active cards. High utilization is a primary distress signal." />
                
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
                <Th label="Health Score" sortKey="financial_health_score" tooltip="Overall financial wellness score. Derived from stability, discipline, and income security." />
                <Th label="Coping" sortKey="coping_index" align="right" tooltip="Measures liquidity resilience—how long the customer can survive a sudden stop in income." />
                <Th label="Exposure" sortKey="exposure_index" align="right" tooltip="Total risk exposure based on secondary borrowing and P2P dependency." />
                <Th label="Asset Util." sortKey="asset_utilization" align="right" tooltip="Ratio of liquid assets to active debt. Lower values indicate higher fragile liquidity." />
                <Th label="Early Risk" sortKey="early_risk_flag" />
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {processedData.length > 0 ? (
                processedData.map((row) => (
                  <tr key={row.customer_id} className="hover:bg-slate-800/40 transition-colors cursor-default whitespace-nowrap">
                    {/* Customer Profile */}
                    <td className="px-4 py-3 text-sm font-mono border-r border-white/5 relative group/cid">
                      <div className="flex flex-col gap-1">
                        <Link to={`/customer/${row.customer_id}`} className="text-cyan-400 hover:text-cyan-300 hover:underline transition-colors font-bold">
                          {row.customer_id}
                        </Link>
                        {row.risk_score * 100 > 85 && (
                          <span className="flex items-center gap-1 text-[9px] font-black uppercase tracking-tighter text-rose-400 animate-pulse bg-rose-500/10 px-1.5 py-0.5 rounded border border-rose-500/20 w-fit">
                            <ShieldAlert className="w-2.5 h-2.5" />
                            Priority Caller
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-300 text-right">{row.age}</td>
                    <td className="px-4 py-3 text-sm text-slate-300">{row.account_tenure || 'N/A'}</td>
                    <td className="px-4 py-3 text-sm border-r border-white/5"><PillBadge value={row.risk_band} /></td>

                    {/* Income & Obligations */}
                    <td className="px-4 py-3 text-sm text-slate-300 text-right font-medium">{formatCurrency(row.monthly_income)}</td>
                    <td className="px-4 py-3 text-sm text-amber-200/80 text-right">{formatCurrency(row.emi)}</td>
                    <td className="px-4 py-3 text-sm text-rose-200/80 text-right">{formatCurrency(row.credit_card_due)}</td>
                    <td className="px-4 py-3 text-sm text-slate-100 font-bold text-right border-r border-white/5">{formatCurrency(row.total_obligations)}</td>

                    {/* Risk Ratios */}
                    <td className="px-4 py-3 text-sm text-right">
                      <span className={row.emi_to_income_ratio > 40 ? 'text-rose-400 font-bold' : 'text-slate-300'}>
                        {Number(row.emi_to_income_ratio || 0).toFixed(1)}%
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-right">
                      <span className={row.debt_stress_ratio > 60 ? 'text-rose-400 font-bold' : 'text-slate-300'}>
                        {Number(row.debt_stress_ratio || 0).toFixed(1)}%
                      </span>
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
                        {row.spending_change > 0 ? '+' : ''}{Number(row.spending_change || 0).toFixed(1)}%
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
                      <span className={row.balance_drop_ratio > 30 ? 'text-rose-400 font-bold' : 'text-slate-300'}>{Number(row.balance_drop_ratio || 0).toFixed(1)}%</span>
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

