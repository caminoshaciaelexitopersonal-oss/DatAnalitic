import { useState, useEffect } from 'react';
import { PowerBiStyleService } from '@/services/api-client';
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
        const dashboardData = await PowerBiStyleService.getDashboardUnifiedV1WpaPowerbiPowerbiDashboardDashboardIdGet(dashboardId);
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
