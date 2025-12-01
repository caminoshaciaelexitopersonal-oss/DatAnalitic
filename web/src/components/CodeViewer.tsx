
'use client';

import React, { useState } from 'react';
import { ApiClient } from '@/services/api-client';

interface CodeViewerProps {
  jobId: string;
}

type CodeFormat = 'python' | 'json' | 'text';

const CodeViewer: React.FC<CodeViewerProps> = ({ jobId }) => {
  const [format, setFormat] = useState<CodeFormat>('python');
  const [code, setCode] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const apiClient = new ApiClient();

  const fetchCode = async () => {
    setIsLoading(true);
    setError(null);
    try {
      // const response = await apiClient.wpaAutomatedAnalysis.getReportUnifiedV1WpaAutoAnalysisJobIdReportFormatGet(jobId, format);
      // setCode(response as any);
      setCode("NOTE: Code viewing is not implemented in the base commit.");
    } catch (e) {
      setError('Failed to fetch code.');
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-gray-800 p-4 rounded-lg mt-4">
      <h3 className="text-lg font-semibold mb-2">Code Inspector</h3>
      <div className="flex space-x-2 mb-2">
        <select onChange={(e) => setFormat(e.target.value as CodeFormat)} value={format} className="bg-gray-700 p-2 rounded">
          <option value="python">Python</option>
          <option value="json">JSON</option>
          <option value="text">Text</option>
        </select>
        <button onClick={fetchCode} disabled={isLoading} className="bg-indigo-500 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded">
          {isLoading ? 'Loading...' : 'Load Code'}
        </button>
      </div>
      {error && <p className="text-red-500">{error}</p>}
      {code && (
        <pre className="bg-gray-900 p-4 rounded-md overflow-x-auto">
          <code>{code}</code>
        </pre>
      )}
    </div>
  );
};

export default CodeViewer;
