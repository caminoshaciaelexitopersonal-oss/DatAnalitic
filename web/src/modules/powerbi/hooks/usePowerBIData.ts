import { useState, useEffect } from 'react';
import { apiClient } from '@/services/api-client';

export const usePowerBIData = (dashboardId: string, widgetId: string, filters?: any) => {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!dashboardId || !widgetId) return;

    const fetchData = async () => {
      try {
        setLoading(true);
        const params = filters ? { filter_values: JSON.stringify(filters) } : {};
        const response = await apiClient.get(`/powerbi/data/widget/${dashboardId}/${widgetId}`, { params });
        setData(response.data.data);
      } catch (err) {
        setError('Failed to fetch widget data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [dashboardId, widgetId, filters]);

  return { data, loading, error };
};
