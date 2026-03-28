import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts';

const RiskDistributionChart = ({ data }) => {
  return (
    <div className="bg-white rounded border border-[var(--color-barclays-border)] p-5 flex flex-col h-full">
      <h2 className="text-base font-semibold text-[var(--color-barclays-text)] mb-4 border-b border-[var(--color-barclays-border)] pb-2">
        Risk Distribution
      </h2>
      
      <div className="flex-1 w-full min-h-[220px] pt-4">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
            <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#4B5563' }} />
            <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#4B5563' }} />
            <Tooltip 
              cursor={{ fill: 'var(--color-barclays-light)' }} 
              contentStyle={{ borderRadius: '4px', border: '1px solid var(--color-barclays-border)', boxShadow: 'none' }}
            />
            <Bar dataKey="value" radius={[2, 2, 0, 0]} maxBarSize={50}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default RiskDistributionChart;
