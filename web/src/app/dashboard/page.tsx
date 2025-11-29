'use client';

import React, { useState } from 'react';
import { useDashboard } from '../../modules/powerbi/hooks/useDashboard';
import DashboardGrid from '../../modules/powerbi/components/Layout/DashboardGrid';
import FilterPanel from '../../modules/powerbi/components/Filters/FilterPanel';

const DashboardPage = () => {
  // Hardcoded for now, will be dynamic later
  const dashboardId = 'main_dashboard';
  const { dashboard, loading, error } = useDashboard(dashboardId);
  const [filters, setFilters] = useState<any>({});

  const handleFilterChange = (filterName: string, value: any) => {
    setFilters((prevFilters: any) => ({
      ...prevFilters,
      [filterName]: value,
    }));
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">{dashboard?.title}</h1>
      <FilterPanel filters={dashboard?.global_filters} onFilterChange={handleFilterChange} />
      <DashboardGrid dashboard={dashboard} filters={filters} />
    </div>
  );
};

export default DashboardPage;
