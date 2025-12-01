
import React from 'react';

interface ColumnDetail {
  dtype: string;
  missing_values: number;
  missing_percentage: number;
  unique_values: number;
  mean?: number;
  std_dev?: number;
  min?: number;
  max?: number;
}

interface DtlColumnDetailsProps {
  columnDetails: Record<string, ColumnDetail>;
}

const DtlColumnDetails: React.FC<DtlColumnDetailsProps> = ({ columnDetails }) => {
  if (!columnDetails) {
    return null;
  }

  const columns = Object.keys(columnDetails);
  const isNumeric = (col: string) => columnDetails[col].mean !== undefined;

  return (
    <div className="mt-6 bg-gray-700 p-6 rounded-lg">
      <h3 className="text-2xl font-bold text-white mb-4">Column Analysis</h3>
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm text-left">
          <thead className="bg-gray-800 text-xs text-gray-300 uppercase tracking-wider">
            <tr>
              <th className="p-3">Column</th>
              <th className="p-3">Data Type</th>
              <th className="p-3 text-center">Unique Values</th>
              <th className="p-3 text-center">Missing Values (%)</th>
              <th className="p-3 text-right">Mean / Min / Max</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-600">
            {columns.map((colName) => (
              <tr key={colName} className="hover:bg-gray-600">
                <td className="p-3 font-semibold">{colName}</td>
                <td className="p-3 font-mono">{columnDetails[colName].dtype}</td>
                <td className="p-3 text-center">{columnDetails[colName].unique_values}</td>
                <td className="p-3 text-center">
                  {columnDetails[colName].missing_values} ({columnDetails[colName].missing_percentage}%)
                </td>
                <td className="p-3 text-right font-mono">
                  {isNumeric(colName)
                    ? `${columnDetails[colName].mean?.toFixed(2)} / ${columnDetails[colName].min?.toFixed(2)} / ${columnDetails[colName].max?.toFixed(2)}`
                    : 'N/A'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default DtlColumnDetails;
