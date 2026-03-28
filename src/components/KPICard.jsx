import React from 'react';

const KPICard = ({ title, value, trend, trendValue }) => {
  return (
    <div className="bg-white rounded border border-[var(--color-barclays-border)] p-4 flex flex-col">
      <h3 className="text-sm font-semibold text-gray-600 mb-2 uppercase tracking-wide">{title}</h3>
      <div className="mt-auto flex items-end justify-between">
        <p className="text-2xl font-bold text-[var(--color-barclays-text)]">{value}</p>
        {trend && (
          <div className="flex items-center text-xs font-medium pb-1">
            <span
              className={`${
                trend === 'up' && title !== 'High Risk Customers' ? 'text-[#137333]' : 
                trend === 'down' && title === 'Avg CIBIL Score' ? 'text-[#C5221F]' :
                trend === 'up' && title === 'High Risk Customers' ? 'text-[#C5221F]' : 'text-gray-500'
              }`}
            >
              {trend === 'up' ? '▲' : trend === 'down' ? '▼' : '▬'} {trendValue}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export default KPICard;
