'use client';

import React from 'react';

interface FilterPanelProps {
  filters: any;
  onFilterChange: (filterName: string, value: any) => void;
}

const FilterPanel: React.FC<FilterPanelProps> = ({ filters, onFilterChange }) => {
  if (!filters) {
    return null;
  }

  return (
    <div className="bg-white shadow rounded-lg p-4 mb-4">
      <h2 className="text-lg font-semibold mb-2">Filters</h2>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {Object.keys(filters).map((filterName) => (
          <div key={filterName}>
            <label className="block text-sm font-medium text-gray-700">{filterName}</label>
            <select
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              onChange={(e) => onFilterChange(filterName, e.target.value)}
            >
              <option value="">All</option>
              {filters[filterName].map((option: any) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FilterPanel;
