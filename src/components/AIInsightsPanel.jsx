import React from 'react';

const AIInsightsPanel = ({ insights }) => {
  return (
    <div className="bg-white rounded border border-[var(--color-barclays-border)] p-5 flex flex-col h-full">
      <h2 className="text-base font-semibold text-[var(--color-barclays-text)] mb-4 border-b border-[var(--color-barclays-border)] pb-2 flex items-center">
        AI Insights
      </h2>
      <div className="flex-1 overflow-y-auto pr-2">
        <ul className="list-disc pl-5 space-y-3">
          {insights.map((insight, index) => (
            <li key={index} className="text-sm text-gray-700">
              {insight}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default AIInsightsPanel;
