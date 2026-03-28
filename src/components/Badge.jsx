import React from 'react';

const Badge = ({ variant, children }) => {
  const styles = {
    Low: 'bg-[#E6F4EA] text-[#137333] border-[#CEEAD6]', // green text/bg
    Medium: 'bg-[#FEF7E0] text-[#B06000] border-[#FEEFC3]', // orange text/bg
    High: 'bg-[#FCE8E6] text-[#C5221F] border-[#FAD2CF]', // red text/bg
    default: 'bg-gray-100 text-gray-800 border-gray-200',
  };

  const selectedStyle = styles[variant] || styles.default;

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold border ${selectedStyle}`}>
      {children}
    </span>
  );
};

export default Badge;
