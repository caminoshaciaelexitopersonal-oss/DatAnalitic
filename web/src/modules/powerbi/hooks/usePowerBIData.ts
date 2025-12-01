
import { useState, useEffect } from 'react';
import apiClient from '@/services/api';

export const usePowerBIData = (dashboardId: string, widgetId: string, filters?: any) => {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!dashboardId || !widgetId) return;

    const fetchData = async () => {
      try {
        setLoading(true);
        const filterValues = filters ? JSON.stringify(filters) : undefined;
        const widgetData = await apiClient.powerBiStyle.getWidgetDataUnifiedV1WpaPowerbiPowerbiDataWidgetDashboardIdWidgetIdGet(
          dashboardId,
          widgetId,
          filterValues,
        );
        setData(widgetData.data);
      } catch (err) {
        setError('Failed to fetch widget data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [dashboardId, widgetId, filters]);

  return { data, loading, error };
};
