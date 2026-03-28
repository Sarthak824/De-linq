import React, { useState } from 'react';
import Badge from './Badge';

const CustomerRiskTable = ({ data }) => {
  const [sortConfig, setSortConfig] = useState({ key: 'financialStressScore', direction: 'desc' });
  const [searchTerm, setSearchTerm] = useState('');

  const sortedData = [...data].sort((a, b) => {
    if (a[sortConfig.key] < b[sortConfig.key]) return sortConfig.direction === 'asc' ? -1 : 1;
    if (a[sortConfig.key] > b[sortConfig.key]) return sortConfig.direction === 'asc' ? 1 : -1;
    return 0;
  });

  const filteredData = sortedData.filter(
    (customer) =>
      customer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      customer.persona.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const requestSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  return (
    <div className="bg-white border border-[var(--color-barclays-border)] flex flex-col h-full">
      <div className="px-5 py-4 flex justify-between items-center border-b border-[var(--color-barclays-border)]">
        <h2 className="text-base font-semibold text-[var(--color-barclays-text)]">Customer Risk Analysis</h2>
        <input
          type="text"
          placeholder="Search customer..."
          className="px-3 py-1.5 border border-[var(--color-barclays-border)] text-sm focus:outline-none focus:border-[var(--color-barclays-blue)] w-60 rounded-sm"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>
      
      <div className="overflow-x-auto flex-1">
        <table className="min-w-full divide-y divide-[var(--color-barclays-border)] text-sm">
          <thead className="bg-[#f8f9fa] sticky top-0">
            <tr>
              <th scope="col" className="px-5 py-3 text-left font-semibold text-gray-700 cursor-pointer hover:bg-gray-100" onClick={() => requestSort('name')}>
                Customer Name {sortConfig.key === 'name' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
              </th>
              <th scope="col" className="px-5 py-3 text-left font-semibold text-gray-700 cursor-pointer hover:bg-gray-100" onClick={() => requestSort('persona')}>
                Persona {sortConfig.key === 'persona' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
              </th>
              <th scope="col" className="px-5 py-3 text-left font-semibold text-gray-700 cursor-pointer hover:bg-gray-100" onClick={() => requestSort('financialStressScore')}>
                Stress Score {sortConfig.key === 'financialStressScore' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
              </th>
              <th scope="col" className="px-5 py-3 text-left font-semibold text-gray-700 cursor-pointer hover:bg-gray-100" onClick={() => requestSort('cibilScore')}>
                CIBIL Score {sortConfig.key === 'cibilScore' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
              </th>
              <th scope="col" className="px-5 py-3 text-left font-semibold text-gray-700 cursor-pointer hover:bg-gray-100" onClick={() => requestSort('riskLevel')}>
                Risk Level {sortConfig.key === 'riskLevel' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
              </th>
              <th scope="col" className="px-5 py-3 text-left font-semibold text-gray-700">
                Recommended Action
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-[var(--color-barclays-border)]">
            {filteredData.map((customer) => (
              <tr 
                key={customer.id} 
                className={`transition-colors ${customer.riskLevel === 'High' ? 'bg-[#FCE8E6] hover:bg-[#fadxdc]' : 'hover:bg-[var(--color-barclays-light)]'}`}
              >
                <td className="px-5 py-3 whitespace-nowrap text-[var(--color-barclays-text)] font-medium">
                  {customer.name}
                </td>
                <td className="px-5 py-3 whitespace-nowrap text-gray-600">
                  {customer.persona}
                </td>
                <td className="px-5 py-3 whitespace-nowrap text-[var(--color-barclays-text)]">
                  {customer.financialStressScore}/100
                </td>
                <td className="px-5 py-3 whitespace-nowrap text-[var(--color-barclays-text)]">
                  {customer.cibilScore}
                </td>
                <td className="px-5 py-3 whitespace-nowrap">
                  <Badge variant={customer.riskLevel}>{customer.riskLevel}</Badge>
                </td>
                <td className="px-5 py-3 whitespace-nowrap text-gray-600">
                  {customer.recommendedAction}
                </td>
              </tr>
            ))}
            {filteredData.length === 0 && (
              <tr>
                <td colSpan="6" className="px-5 py-6 text-center text-gray-500">
                  No customers found matching your search.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default CustomerRiskTable;
