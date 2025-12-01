'use client';

import React, { useState } from 'react';

const WidgetEditor = ({ onSave, onCancel, widget = {} }) => {
  const [title, setTitle] = useState(widget.title || '');
  const [type, setType] = useState(widget.type || 'bar');
  const [dataSource, setDataSource] = useState(widget.config?.path || '');
  const [xField, setXField] = useState(widget.config?.xField || '');
  const [yField, setYField] = useState(widget.config?.yField || '');
  const [series, setSeries] = useState(widget.config?.series?.join(', ') || '');

  const handleSave = () => {
    // Basic validation
    if (!title || !type || !dataSource) {
      alert("Please fill in all required fields.");
      return;
    }

    onSave({
      title,
      type,
      config: {
        path: dataSource,
        source: 'local', // Assuming local for now
        xField,
        yField,
        series: series.split(',').map(s => s.trim()).filter(Boolean),
      },
      layout: widget.layout || { w: 6, h: 4, x: 0, y: Infinity } // Place new widgets at the bottom
    });
  };

  const chartTypes = ["bar", "line", "area", "pie", "scatter", "histogram", "boxplot", "heatmap", "feature_importance", "roc_curve", "confusion_matrix"];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-center">
      <div className="bg-white p-6 rounded-lg shadow-xl w-1/2 max-h-screen overflow-y-auto">
        <h2 className="text-2xl mb-4">{widget.id ? 'Edit Widget' : 'Create New Widget'}</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2">Widget Title*</label>
            <input value={title} onChange={(e) => setTitle(e.target.value)} className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700" />
          </div>

          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2">Chart Type*</label>
            <select value={type} onChange={(e) => setType(e.target.value)} className="shadow border rounded w-full py-2 px-3 text-gray-700">
              {chartTypes.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
        </div>

        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2">Data Source (e.g., path to CSV)*</label>
          <input value={dataSource} onChange={(e) => setDataSource(e.target.value)} className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700" />
        </div>

        <hr className="my-4"/>
        <h3 className="text-xl mb-2">Chart Configuration</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2">X-Axis Field</label>
                <input value={xField} onChange={(e) => setXField(e.target.value)} placeholder="e.g., date" className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700" />
            </div>
            <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2">Y-Axis Field</label>
                <input value={yField} onChange={(e) => setYField(e.target.value)} placeholder="e.g., value (for pie/scatter)" className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700" />
            </div>
        </div>
        <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2">Series (comma-separated)</label>
            <input value={series} onChange={(e) => setSeries(e.target.value)} placeholder="e.g., sales, revenue, cost" className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700" />
        </div>

        <div className="flex justify-end mt-6">
          <button onClick={onCancel} className="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded mr-2">
            Cancel
          </button>
          <button onClick={handleSave} className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
            Save
          </button>
        </div>
      </div>
    </div>
  );
};

export default WidgetEditor;
