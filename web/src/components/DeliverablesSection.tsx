// src/components/DeliverablesSection.tsx
import React from 'react';

interface DeliverablesSectionProps {
  jobId: string;
}

const DeliverablesSection: React.FC<DeliverablesSectionProps> = ({ jobId }) => {
  // Base URL for the download endpoints
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || '';

  const handleDownload = (type: 'package' | 'code' | 'notebook') => {
    const url = `${API_BASE_URL}/unified/v1/mpa/delivery/job/${jobId}/${type}`;
    // Open the URL in a new tab to trigger the download
    window.open(url, '_blank');
  };

  return (
    <div className="mt-8 p-4 border border-gray-200 rounded-lg shadow-sm">
      <h2 className="text-xl font-semibold mb-4 text-gray-800">Entregables</h2>
      <p className="text-sm text-gray-600 mb-4">
        Descargue el paquete de código completo, los scripts individuales o el notebook de verificación.
      </p>

      {/* File Tree Visualization (Placeholder) */}
      <div className="bg-gray-50 p-3 rounded-md mb-4">
        <p className="text-gray-700 font-mono text-sm">
          - /src/ <br />
          &nbsp;&nbsp;- preprocessing.py <br />
          &nbsp;&nbsp;- model_training.py <br />
          - /reports/ (próximamente) <br />
          - manifest.json <br />
          - README.md <br />
          - verificacion_analisis.ipynb (próximamente)
        </p>
      </div>

      {/* Download Buttons */}
      <div className="flex space-x-4">
        <button
          onClick={() => handleDownload('package')}
          className="bg-blue-600 text-white font-bold py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
        >
          Descargar Paquete (.zip)
        </button>
        {/*
        <button
          onClick={() => handleDownload('code')}
          className="bg-gray-600 text-white font-bold py-2 px-4 rounded-md hover:bg-gray-700 transition-colors"
        >
          Descargar Código
        </button>
        <button
          onClick={() => handleDownload('notebook')}
          className="bg-green-600 text-white font-bold py-2 px-4 rounded-md hover:bg-green-700 transition-colors"
        >
          Descargar Notebook
        </button>
        */}
      </div>
    </div>
  );
};

export default DeliverablesSection;
