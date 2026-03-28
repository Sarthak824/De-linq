import React from 'react';

const ActivityFeed = ({ activities }) => {
  return (
    <div className="bg-white rounded border border-[var(--color-barclays-border)] p-5 flex flex-col h-full">
      <h2 className="text-base font-semibold text-[var(--color-barclays-text)] mb-4 border-b border-[var(--color-barclays-border)] pb-2">
        Recent Activity
      </h2>
      
      <div className="flex-1 overflow-y-auto pr-2">
        <ul className="divide-y divide-[var(--color-barclays-border)]">
          {activities.map((activity) => (
            <li key={activity.id} className="py-3 px-1 hover:bg-[var(--color-barclays-light)] transition-colors">
              <p className="text-sm text-[var(--color-barclays-text)] font-medium">{activity.action}</p>
              <span className="text-xs text-gray-500 mt-1 block">{activity.timestamp}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default ActivityFeed;
