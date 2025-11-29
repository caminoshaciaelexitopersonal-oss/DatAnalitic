'use client';

import React, { useState, useEffect } from 'react';
import { McpMainControlPlaneService, ApiError } from '@/services/api-client';
import ReportDownloader from '@/components/ReportDownloader';
import CodeViewer from '@/components/CodeViewer';

// Define a type for the status object for better type safety
type JobStatus = {
  status: 'queued' | 'running' | 'completed' | 'failed';
  stage?: string;
  error?: string;
  [key: string]: any;
};

export default function JobStatusPage({ params }: { params: { job_id: string } }) {
  const { job_id: jobId } = params;
  const [status, setStatus] = useState<JobStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) return;

    let interval: NodeJS.Timeout;

    const fetchStatus = async () => {
      try {
        // Use the correct unified service
        const result = await McpMainControlPlaneService.getJobStatusUnified(jobId);
        setStatus(result as JobStatus);
        if (result.status === 'completed' || result.status === 'failed') {
          if (interval) clearInterval(interval);
        }
      } catch (e) {
        if (e instanceof ApiError) {
          setError(`API Error: ${e.body.detail || e.message}`);
        } else {
          setError((e as Error).message);
        }
        if (interval) clearInterval(interval);
      }
    };

    fetchStatus();
    interval = setInterval(fetchStatus, 5000);

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [jobId]);

  const isJobComplete = status?.status === 'completed';

  return (
    <div className="bg-gray-900 text-slate-200 min-h-screen font-sans flex flex-col">
      <header className="p-4 border-b border-gray-700">
        <h1 className="text-xl font-bold">Estado del Trabajo de Análisis</h1>
      </header>
      <main className="flex-1 overflow-y-auto p-8">
        <p className="mb-4">Job ID: <span className="font-mono text-green-400">{jobId}</span></p>

        {error && (
          <div className="p-4 rounded-md bg-red-800 text-white">
            <p><strong>Error:</strong> {error}</p>
          </div>
        )}

        {status && (
            <div className="p-4 rounded-md bg-gray-800 my-4">
                <p><strong>Estado:</strong> <span className={`font-bold ${
                    status.status === 'completed' ? 'text-green-400' :
                    status.status === 'failed' ? 'text-red-400' : 'text-yellow-400'
                }`}>{status.status}</span></p>
                {status.stage && <p><strong>Etapa:</strong> {status.stage}</p>}
                {status.error && <p className="text-red-400"><strong>Detalle del Error:</strong> {status.error}</p>}
            </div>
        )}

        {isJobComplete && (
          <div className="mt-8">
            <h2 className="text-xl mb-4 font-semibold">Resultados del Análisis</h2>
            <div className="flex flex-col gap-4">
                <ReportDownloader jobId={jobId} />
                <CodeViewer jobId={jobId} />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
