
import React from 'react';

interface Overview {
  num_rows: number;
  num_cols: number;
  total_cells: number;
  missing_cells: number;
  missing_percentage: number;
  duplicate_rows: number;
}

interface DtlSummaryProps {
  healthScore: number;
  overview: Overview;
}

const DtlSummary: React.FC<DtlSummaryProps> = ({ healthScore, overview }) => {
  const getHealthScoreColor = (score: number) => {
    if (score >= 85) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="bg-gray-700 p-6 rounded-lg space-y-4">
      <h3 className="text-2xl font-bold text-white">Data Quality Summary (DTL)</h3>
      <div className="flex items-center justify-between">
        <div className="text-center">
          <p className="font-semibold text-gray-400">Health Score</p>
          <p className={`text-5xl font-bold ${getHealthScoreColor(healthScore)}`}>
            {healthScore.toFixed(1)}%
          </p>
        </div>
        <div className="grid grid-cols-2 gap-x-8 gap-y-2 text-sm">
          <div>
            <span className="font-semibold text-gray-300">Rows:</span>
            <span className="ml-2">{overview.num_rows.toLocaleString()}</span>
          </div>
          <div>
            <span className="font-semibold text-gray-300">Columns:</span>
            <span className="ml-2">{overview.num_cols}</span>
          </div>
          <div>
            <span className="font-semibold text-gray-300">Missing Cells:</span>
            <span className="ml-2 text-yellow-400">{overview.missing_cells.toLocaleString()} ({overview.missing_percentage}%)</span>
          </div>
          <div>
            <span className="font-semibold text-gray-300">Duplicate Rows:</span>
            <span className="ml-2 text-red-400">{overview.duplicate_rows.toLocaleString()}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DtlSummary;
