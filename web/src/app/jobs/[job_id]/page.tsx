
'use client';

import React, { useState, useEffect } from 'react';
import apiClient from '@/services/api';
import { ApiError, Job } from '@/services/api-client';
import ToastContainer from '@/components/ToastContainer';
import DtlSummary from '@/components/DtlSummary';
import DtlColumnDetails from '@/components/DtlColumnDetails';

// Local type definition for QualityReport to fix build error
interface QualityReport {
  overview: any;
  column_details: any;
  health_score: number;
}

export default function JobPage({ params }: { params: { job_id: string } }) {
  const { job_id } = params;
  const [status, setStatus] = useState<any>(null);
  const [results, setResults] = useState<any | null>(null);
  const [qualityReport, setQualityReport] = useState<QualityReport | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [toasts, setToasts] = useState<{ id: number; message: string; type: 'success' | 'error' | 'info' }[]>([]);

  const addToast = (message: string, type: 'success' | 'error' | 'info') => {
    setToasts(prev => [...prev, { id: Date.now(), message, type }]);
    setTimeout(() => setToasts(prev => prev.slice(1)), 5000);
  };

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const currentStatus = await apiClient.mcpMainControlPlane.getJobStatusUnified(job_id);
        setStatus(currentStatus);

        if (currentStatus.status === 'completed' || currentStatus.status === 'failed') {
          fetchResults();
          return;
        }
        setTimeout(fetchStatus, 3000);
      } catch (err) {
        handleApiError(err, 'Error fetching job status');
      }
    };

    const fetchResults = async () => {
      try {
        // Fetch both results and quality report in parallel
        const [finalResults, qualityData] = await Promise.all([
          apiClient.mcpMainControlPlane.getJobResults(job_id),
          // Manually fetch the quality report as the generated client is not updated yet
          fetch(`/unified/v1/wpa/auto-analysis/${job_id}/quality-report`).then(res => {
            if (!res.ok) throw new Error('Quality report request failed');
            return res.json();
          })
        ]);

        setResults(finalResults);
        setQualityReport(qualityData); // Set the quality report state
        addToast('Analysis has finished.', 'success');

      } catch (err) {
        handleApiError(err, 'Error fetching job results');
      } finally {
        setIsLoading(false);
      }
    };

    const handleApiError = (err: any, defaultMessage: string) => {
      let errorMessage = defaultMessage;
      if (err instanceof ApiError) {
        errorMessage = err.body?.detail || err.message;
      } else if (err instanceof Error) {
        errorMessage = err.message;
      }
      setError(errorMessage);
      addToast(errorMessage, 'error');
      setIsLoading(false);
    };

    fetchStatus();
  }, [job_id]);

  // ... (render methods are unchanged)
  const renderStatus = () => {
    if (isLoading && !status) {
      return <p className="text-lg text-yellow-400">Loading analysis status...</p>;
    }
    if (status) {
      return (
        <div className="bg-gray-700 p-4 rounded-lg mb-6">
          <p className="text-lg font-semibold">Status: <span className="text-cyan-400">{status.status}</span></p>
          <p className="text-md">Stage: <span className="text-cyan-500">{status.stage}</span></p>
        </div>
      );
    }
    return null;
  };

  const renderResults = () => {
    if (isLoading) {
      return <p className="text-lg text-yellow-400 mt-4">Waiting for final results...</p>;
    }
    if (error && !results) {
      return <p className="text-lg text-red-500 mt-4">Error: {error}</p>;
    }
    if (results) {
      return (
        <>
          {qualityReport && (
            <>
              <DtlSummary
                healthScore={qualityReport.health_score}
                overview={qualityReport.overview}
              />
              <DtlColumnDetails
                columnDetails={qualityReport.column_details}
              />
            </>
          )}
          <div className="mt-6 bg-gray-700 p-6 rounded-lg space-y-4">
            <h3 className="text-2xl font-bold text-green-400">General Analysis Results</h3>
            <div>
              <p className="font-semibold">Job ID:</p>
              <p className="font-mono text-sm">{results.job_id}</p>
            </div>
            <div className="border-t border-gray-600 pt-4">
              <h4 className="text-xl font-bold mb-2">Target Variable Detection</h4>
              <p><strong>Selected Target:</strong> {results.target_detection.selected_target || 'N/A'}</p>
              <p><strong>Confidence:</strong> {results.target_detection.confidence.toFixed(2)}</p>
              <p><strong>Explanation:</strong> {results.target_detection.explanation}</p>
            </div>
          </div>
        </>
      );
    }
    return null;
  };

  return (
    <div className="bg-gray-900 text-slate-200 min-h-screen font-sans flex flex-col">
      <header className="p-4 border-b border-gray-700">
        <h1 className="text-xl font-bold">Analysis Results for Job: <span className="font-mono text-blue-400">{job_id}</span></h1>
      </header>
      <main className="flex-1 p-8">
        <div className="w-full max-w-4xl mx-auto">
          <div className="bg-gray-800 p-8 rounded-lg shadow-lg">
            {renderStatus()}
            {renderResults()}
          </div>
        </div>
      </main>
      <ToastContainer toasts={toasts} />
    </div>
  );
}
