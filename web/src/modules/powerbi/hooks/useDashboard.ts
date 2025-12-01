
import { useState, useEffect } from 'react';
import apiClient from '@/services/api';
import { DashboardConfig } from '@/services/api-client';

export const useDashboard = (dashboardId: string) => {
  const [dashboard, setDashboard] = useState<DashboardConfig | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!dashboardId) return;

    const fetchDashboard = async () => {
      try {
        setLoading(true);
        const dashboardData = await apiClient.powerBiStyle.getDashboardUnifiedV1WpaPowerbiPowerbiDashboardDashboardIdGet(dashboardId);
        setDashboard(dashboardData);
      } catch (err) {
        setError('Failed to fetch dashboard');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
  }, [dashboardId]);

  return { dashboard, loading, error };
};
