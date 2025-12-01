'use client';

import React from 'react';
import { Responsive, WidthProvider } from 'react-grid-layout';
import { ChartRenderer } from '../ChartRenderer/ChartRenderer';
import { usePowerBIData } from '../../hooks/usePowerBIData';

const ResponsiveGridLayout = WidthProvider(Responsive);

const Widget = ({ dashboardId, widget, filters }: { dashboardId: string; widget: any; filters: any }) => {
  const { data, loading, error } = usePowerBIData(dashboardId, widget.id, filters);

  if (loading) {
    return <div>Loading widget...</div>;
  }

  if (error) {
    return <div>Error loading widget.</div>;
  }

  return (
    <ChartRenderer
      type={widget.type}
      data={data}
      xField={widget.xField}
      yField={widget.yField}
      series={widget.series}
      config={widget.config}
    />
  );
};

interface DashboardGridProps {
  dashboard: any;
  filters: any;
}

const DashboardGrid: React.FC<DashboardGridProps> = ({ dashboard, filters }) => {
  if (!dashboard) {
    return <div>Loading Dashboard...</div>;
  }

  const layout = dashboard.layout.widgets.map((widget: any, i: number) => ({
    i: widget.id,
    x: widget.col || (i % 2) * 6,
    y: widget.row || Math.floor(i / 2) * 3,
    w: widget.width || 6,
    h: widget.height || 3,
  }));

  return (
    <ResponsiveGridLayout
      className="layout"
      layouts={{ lg: layout }}
      breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 }}
      cols={{ lg: 12, md: 10, sm: 6, xs: 4, xxs: 2 }}
    >
      {dashboard.layout.widgets.map((widget: any) => (
        <div key={widget.id} className="bg-white shadow rounded-lg p-4">
          <h2 className="text-lg font-semibold mb-2">{widget.title}</h2>
          <Widget dashboardId={dashboard.id} widget={widget} filters={filters} />
        </div>
      ))}
    </ResponsiveGridLayout>
  );
};

export default DashboardGrid;
