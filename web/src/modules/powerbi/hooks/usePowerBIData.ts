import { useState, useEffect } from 'react';
import { api } from '../../../services/api';

export const usePowerBIData = (widgetId: number) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<any>(null);

  useEffect(() => {
    if (!widgetId) return;

    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await api.wpa.powerbi.getWidgetData(widgetId);
        setData(response);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [widgetId]);

  return { data, loading, error };
};
