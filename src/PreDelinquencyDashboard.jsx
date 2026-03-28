import React from 'react';
import KPICard from './components/KPICard';
import CustomerRiskTable from './components/CustomerRiskTable';
import RiskDistributionChart from './components/RiskDistributionChart';
import AIInsightsPanel from './components/AIInsightsPanel';
import ActivityFeed from './components/ActivityFeed';

import {
  mockCustomers,
  summaryMetrics,
  riskDistributionData,
  aiInsights,
  recentActivity
} from './data/mockData';

const PreDelinquencyDashboard = () => {
  return (
    <div className="min-h-screen bg-[var(--color-barclays-bg)] font-sans antialiased">
      {/* Top Navigation Bar */}
      <header className="bg-white border-b border-[var(--color-barclays-border)]">
        <div className="max-w-[1400px] mx-auto px-6 h-14 flex justify-between items-center">
          {/* Left: Logo Placeholder */}
          <div className="flex items-center">
            <span className="font-bold text-xl tracking-wide text-[var(--color-barclays-blue)]">
              BARCLAYS
            </span>
          </div>

          {/* Center: Search Bar */}
          <div className="flex-1 max-w-lg px-8 hidden md:flex mx-auto">
            <input
              type="text"
              placeholder="Search customer..."
              className="w-full px-4 py-1.5 border border-[var(--color-barclays-border)] rounded-sm bg-white text-sm focus:outline-none focus:border-[var(--color-barclays-blue)]"
            />
          </div>

          {/* Right: Notifications & Profile */}
          <div className="flex items-center space-x-6">
            <button className="text-[var(--color-barclays-text)] relative text-sm font-medium hover:text-[var(--color-barclays-blue)]">
              Alerts
              <span className="absolute -top-1 -right-2 w-2 h-2 bg-[#C5221F] rounded-full"></span>
            </button>
            <div className="flex items-center space-x-2 text-sm">
              <div className="w-7 h-7 bg-gray-200 rounded-full flex items-center justify-center text-gray-600 font-bold text-xs">
                RO
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Dashboard */}
      <main className="max-w-[1400px] mx-auto px-6 py-6">
        <div className="mb-6 flex justify-between items-end">
          <div>
            <h1 className="text-xl font-bold text-[var(--color-barclays-text)]">Financial Risk Monitoring</h1>
            <p className="text-sm text-gray-600 mt-0.5">Internal Dashboard - Confidential</p>
          </div>
        </div>

        {/* KPI Summary Section */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
          <KPICard title="Total Customers" value={summaryMetrics.totalCustomers} />
          <KPICard title="High Risk Customers" value={summaryMetrics.highRiskCustomers} />
          <KPICard title="Avg Stress Score" value={`${summaryMetrics.avgStressScore}/100`} />
          <KPICard title="Avg CIBIL Score" value={summaryMetrics.avgCibilScore} />
          <KPICard title="Active Interventions" value={summaryMetrics.activeInterventions} />
        </div>

        {/* Grid Layout for Main Widgets */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Main Section: Customer Risk Table spans 8 columns on large screens */}
          <div className="lg:col-span-8 flex flex-col space-y-6">
            <div className="flex-1 min-h-[500px] max-h-[600px] shadow-sm rounded">
              <CustomerRiskTable data={mockCustomers} />
            </div>
            
            <div className="h-[250px] shadow-sm rounded">
              <AIInsightsPanel insights={aiInsights} />
            </div>
          </div>

          {/* Right Sidebar: Charts & Activity spans 4 columns */}
          <div className="lg:col-span-4 flex flex-col space-y-6 h-full">
            <div className="h-[350px] shadow-sm rounded">
              <RiskDistributionChart data={riskDistributionData} />
            </div>
            <div className="flex-1 min-h-[400px] shadow-sm rounded">
              <ActivityFeed activities={recentActivity} />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default PreDelinquencyDashboard;
