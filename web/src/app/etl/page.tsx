'use client';

import React from 'react';

export default function EtlControlPage() {
  return (
    <div className="bg-gray-900 text-slate-200 h-screen font-sans flex flex-col">
      <header className="p-4 border-b border-gray-700">
        <h1 className="text-xl font-bold">Control de Operaciones ETL</h1>
      </header>
      <main className="flex-1 overflow-y-auto p-8">
        <h2 className="text-2xl mb-4">Interfaz de Control ETL</h2>
        <p>
          Esta página servirá como una interfaz de usuario administrable para ejecutar
          y validar operaciones de ETL seguras.
        </p>
        <div className="mt-8 p-4 rounded-md bg-gray-800">
          <p className="font-mono">
            Placeholder para controles de UI (ej. validadores de scripts SQL, selectores de fuente de datos, etc.).
          </p>
        </div>
      </main>
    </div>
  );
}
