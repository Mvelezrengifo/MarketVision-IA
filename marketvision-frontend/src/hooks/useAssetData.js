import { useState, useEffect } from 'react';
import { getAsset, getAssetHistory } from '../services/api';

export const useAssetData = (symbol, assetClass, includeHistory = true) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!symbol) return;
    const fetchData = async () => {
      setLoading(true);
      try {
        const assetData = await getAsset(symbol, includeHistory, 50);
        let history = null;
        if (includeHistory) {
          history = await getAssetHistory(symbol, 50);
        }
        setData({ ...assetData, priceHistory: history?.prices || [] });
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [symbol, includeHistory]);

  return { data, loading, error };
};