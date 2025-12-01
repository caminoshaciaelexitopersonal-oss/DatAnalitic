'use client';

import { Inter } from "next/font/google";
import "./globals.css";
import { OpenAPI } from "@/services/api-client";
import ToastContainer from "@/components/ToastContainer";
import React, { useState } from "react";

// --- API Client Configuration ---
// Bypass the Next.js proxy and connect directly to the backend for robust communication.
OpenAPI.BASE = "http://localhost:8000/unified/v1";

const inter = Inter({ subsets: ["latin"] });

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  // Minimal state management for ToastContainer to satisfy TypeScript
  const [toasts, setToasts] = useState<{ id: number; message: string; type: string }[]>([]);

  return (
    <html lang="en">
      <body className={inter.className}>
        {children}
        <ToastContainer toasts={toasts} />
      </body>
    </html>
  );
}
