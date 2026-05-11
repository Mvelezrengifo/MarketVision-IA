import axios from 'axios';

const API_BASE = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
});

export const getAsset = async (symbol, includeHistory = true, limit = 20) => {
  const response = await api.get(`/assets/${symbol}`, {
    params: { include_history: includeHistory, limit }
  });
  return response.data;
};

export const getAssetHistory = async (symbol, limit = 20) => {
  const response = await api.get(`/assets/${symbol}/history`, { params: { limit } });
  return response.data;
};

export default api;