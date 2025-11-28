'use client';

import React from 'react';

interface ReportDownloaderProps {
  jobId: string;
}

const ReportDownloader: React.FC<ReportDownloaderProps> = ({ jobId }) => {
  const downloadUrl = (format: 'docx' | 'excel' | 'pdf') => {
    // This constructs a relative URL. The Next.js rewrite proxy will handle forwarding it.
    return `/unified/v1/wpa/auto-analysis/${jobId}/report/${format}`;
  };

  return (
    <div className="bg-gray-800 p-4 rounded-lg mt-4">
      <h3 className="text-lg font-semibold mb-2">Descargar Informes</h3>
      <div className="flex space-x-2">
        <a href={downloadUrl('docx')} download className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
          Descargar DOCX
        </a>
        <a href={downloadUrl('excel')} download className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded">
          Descargar Excel
        </a>
        <a href={downloadUrl('pdf')} download className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded">
          Descargar PDF
        </a>
      </div>
    </div>
  );
};

export default ReportDownloader;
