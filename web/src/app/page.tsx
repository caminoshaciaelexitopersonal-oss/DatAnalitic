'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios'; // Import axios
import ToastContainer from '@/components/ToastContainer';
import { Job } from '@/services/api-client'; // We can still use the types

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [toasts, setToasts] = useState<{ id: number; message: string; type: 'success' | 'error' | 'info' }[]>([]);
  const router = useRouter();

  const addToast = (message: string, type: 'success' | 'error' | 'info') => {
    setToasts(prev => [...prev, { id: Date.now(), message, type }]);
    setTimeout(() => {
      setToasts(prev => {
        const newToasts = [...prev];
        newToasts.shift();
        return newToasts;
      });
    }, 5000);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!file) {
      setError('Por favor, selecciona un archivo para analizar.');
      return;
    }

    setIsLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      // Use axios for the multipart/form-data request
      const response = await axios.post<Job>('/unified/v1/mcp/job/start', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      addToast('Análisis iniciado con éxito. Redirigiendo...', 'success');

      const job = response.data;
      if (job.job_id) {
        router.push(`/jobs/${job.job_id}`);
      } else {
        throw new Error("La respuesta de la API no incluyó un ID de trabajo.");
      }

    } catch (err: any) {
      let errorMessage = 'Ocurrió un error desconocido.';
      if (axios.isAxiosError(err) && err.response) {
        // Capture detailed error from axios response
        const apiError = err.response.data;
        errorMessage = `Error en el servidor: ${apiError.detail || err.message}`;
      } else if (err instanceof Error) {
        errorMessage = err.message;
      }
      setError(errorMessage);
      addToast(errorMessage, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-gray-900 text-slate-200 h-screen font-sans flex flex-col">
      <header className="p-4 border-b border-gray-700 flex justify-between items-center">
        <h1 className="text-xl font-bold">Sistema de Analítica de Datos Inteligente (SADI)</h1>
      </header>
      <main className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-lg">
          <div className="bg-gray-800 p-8 rounded-lg shadow-lg text-center">
            <h2 className="text-2xl font-bold mb-4">Iniciar Nuevo Análisis</h2>
            <p className="mb-6 text-gray-400">
              Sube tu archivo de datos (CSV, Excel, JSON) para comenzar el proceso de DTL y análisis automatizado.
            </p>
            <form onSubmit={handleSubmit}>
              <div className="mb-4">
                <input
                  type="file"
                  onChange={handleFileChange}
                  className="w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-500 file:text-white hover:file:bg-blue-600"
                  accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel, .json"
                />
              </div>

              {error && <p className="text-red-500 text-sm mb-4">{error}</p>}

              <button
                type="submit"
                disabled={isLoading || !file}
                className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-lg disabled:bg-gray-500 disabled:cursor-not-allowed transition-colors duration-300"
              >
                {isLoading ? 'Analizando...' : 'Iniciar Análisis'}
              </button>
            </form>
          </div>
        </div>
      </main>
      <ToastContainer toasts={toasts} />
    </div>
  );
}
