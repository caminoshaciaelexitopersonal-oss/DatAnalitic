'use client';

import React, { useState, useEffect } from 'react';
import { Responsive, WidthProvider } from 'react-grid-layout';
import { ChartRenderer } from '../ChartRenderer/ChartRenderer';
import { usePowerBIData } from '../../hooks/usePowerBIData';
import WidgetEditor from '../WidgetEditor/WidgetEditor';
import { api } from '../../../../services/api';

const ResponsiveGridLayout = WidthProvider(Responsive);

const Widget = ({ widget, onDelete }: { widget: any; onDelete: (id: number) => void }) => {
  const { data, loading, error } = usePowerBIData(widget.id); // Updated hook usage
  const [menuOpen, setMenuOpen] = useState(false);

  // Export logic remains the same, but uses the new endpoint structure
  const handleExport = (format: string) => {
    const url = `/unified/v1/wpa/powerbi/widget/${widget.id}/export?format=${format}`;
    window.open(url, '_blank');
    setMenuOpen(false);
  };

  if (loading) return <div className="flex items-center justify-center h-full"><div>Loading...</div></div>;
  if (error) return <div className="flex items-center justify-center h-full"><div>Error!</div></div>;

  return (
    <div className="h-full w-full relative">
       <div className="absolute top-0 right-1 z-10">
        <button onClick={() => setMenuOpen(!menuOpen)} className="p-1 rounded-full hover:bg-gray-200">&#x22EE;</button>
        {menuOpen && (
          <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-20">
            <div className="py-1">
              <a onClick={() => {/* TODO: Edit widget */}} className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 cursor-pointer">Edit</a>
              <a onClick={() => onDelete(widget.id)} className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 cursor-pointer">Delete</a>
              <div className="border-t my-1"></div>
              <a onClick={() => handleExport('png')} className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 cursor-pointer">Export as PNG</a>
              <a onClick={() => handleExport('pdf')} className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 cursor-pointer">Export as PDF</a>
              <a onClick={() => handleExport('csv')} className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 cursor-pointer">Export data as CSV</a>
            </div>
          </div>
        )}
      </div>
      <ChartRenderer
        type={widget.type}
        data={data?.data} // Data is now nested under 'data' key
        xField={widget.xField}
        yField={widget.yField}
        series={widget.series}
        config={widget.config}
      />
    </div>
  );
};

const DashboardGrid = ({ dashboardId }: { dashboardId: number }) => {
  const [dashboard, setDashboard] = useState(null);
  const [isEditorOpen, setEditorOpen] = useState(false);

  useEffect(() => {
    if (dashboardId) {
      api.wpa.powerbi.getDashboard(dashboardId).then(setDashboard);
    }
  }, [dashboardId]);

  const handleSaveWidget = async (widgetData: any) => {
    await api.wpa.powerbi.addWidgetToDashboard(dashboardId, widgetData);
    // Refresh dashboard
    const updatedDashboard = await api.wpa.powerbi.getDashboard(dashboardId);
    setDashboard(updatedDashboard);
    setEditorOpen(false);
  };

  const handleDeleteWidget = async (widgetId: number) => {
    await api.wpa.powerbi.deleteWidget(widgetId);
    // Refresh dashboard
    const updatedDashboard = await api.wpa.powerbi.getDashboard(dashboardId);
    setDashboard(updatedDashboard);
  };

  if (!dashboard) return <div>Loading Dashboard...</div>;

  const layout = dashboard.layout.widgets.map((w: any) => ({ i: String(w.id), ...w.layout }));

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">{dashboard.name}</h1>
        <button onClick={() => setEditorOpen(true)} className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
          Add Widget
        </button>
      </div>

      {isEditorOpen && (
        <WidgetEditor
          onSave={handleSaveWidget}
          onCancel={() => setEditorOpen(false)}
        />
      )}

      <ResponsiveGridLayout
        layouts={{ lg: layout }}
        breakpoints={{ lg: 1200 }}
        cols={{ lg: 12 }}
        rowHeight={100}
      >
        {dashboard.layout.widgets.map((widget: any) => (
          <div key={String(widget.id)} className="bg-white shadow rounded-lg p-2 pt-8 relative">
            <h2 className="text-lg font-semibold mb-2 absolute top-2 left-4">{widget.title}</h2>
            <Widget widget={widget} onDelete={handleDeleteWidget} />
          </div>
        ))}
      </ResponsiveGridLayout>
    </div>
  );
};

export default DashboardGrid;
