// src/app/jobs/[jobId]/page.tsx
'use client';

import React from 'react';
import { useParams } from 'next/navigation';
import DeliverablesSection from '@/components/DeliverablesSection'; // Import the new component

export default function JobResultPage() {
  const params = useParams();
  const jobId = params.jobId as string;

  return (
    <div className="bg-gray-900 text-slate-200 min-h-screen font-sans">
      <header className="p-4 border-b border-gray-700">
        <h1 className="text-xl font-bold">Resultados del Análisis</h1>
      </header>
      <main className="p-8">
        <div className="bg-gray-800 p-8 rounded-lg shadow-lg">
          <h2 className="text-2xl font-bold mb-4">Job ID: <span className="text-blue-400 font-mono">{jobId}</span></h2>

          {/* Placeholder for other job results */}
          <div className="mb-8">
            <p className="text-gray-400">
              Aquí se mostrarán los resultados del análisis, como informes de calidad de datos, visualizaciones y métricas del modelo.
            </p>
          </div>

          {/* Include the Deliverables Section */}
          {jobId && <DeliverablesSection jobId={jobId} />}
        </div>
      </main>
    </div>
  );
}
