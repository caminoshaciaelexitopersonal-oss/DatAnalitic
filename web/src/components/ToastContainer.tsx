'use client';

import React from 'react';

const ToastContainer = ({ toasts }: { toasts: { id: number; message: string; type: string }[] }) => (
  <div className="fixed bottom-4 right-4 space-y-2">
    {toasts.map(toast => (
      <div key={toast.id} className={`p-4 rounded-md shadow-lg text-white ${toast.type === 'error' ? 'bg-red-600' : 'bg-blue-600'}`}>
        {toast.message}
      </div>
    ))}
  </div>
);

export default ToastContainer;
