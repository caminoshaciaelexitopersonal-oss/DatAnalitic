import { useState, useEffect } from 'react';
import { apiClient } from '@/services/api-client';

export const useDashboard = (dashboardId: string) => {
  const [dashboard, setDashboard] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!dashboardId) return;

    const fetchDashboard = async () => {
      try {
        setLoading(true);
        const response = await apiClient.get(`/powerbi/dashboard/${dashboardId}`);
        setDashboard(response.data);
      } catch (err) {
        setError('Failed to fetch dashboard');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
  }, [dashboardId]);

  return { dashboard, loading, error };
};
