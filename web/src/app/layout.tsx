'use client';

import { Inter } from "next/font/google";
import "./globals.css";
import { OpenAPI } from "@/services/api-client";
import ToastContainer from "@/components/ToastContainer";
import React, { useState } from "react";

// --- API Client Configuration ---
// This is the central point to configure the API client base URL.
// It reads from an environment variable to allow different configurations per environment.
OpenAPI.BASE = process.env.NEXT_PUBLIC_API_URL || "/unified/v1";

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
