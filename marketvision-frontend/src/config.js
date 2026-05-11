// ===== CONFIGURACIÓN GLOBAL =====
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  ENDPOINTS: {
    ASSET: '/assets',
    ASSET_HISTORY: '/assets/{symbol}/history',
    HEALTH: '/health',
    SYNC: '/sync',
    GROK_REVIEWS: '/grok/reviews' // 🔮 Futuro
  },
  TIMEOUT: 10000,
  AUTO_REFRESH_MS: 10000
};

export const UI_CONFIG = {
  ROBOT_IMAGE: '/robot.svg.png', // ✅ Ruta correcta
  SYMBOLS: ['BTC', 'ETH', 'NVDA', 'AAPL', 'GOLD'],
  SIGNAL_COLORS: {
    BUY: '#10b981',
    SELL: '#ef4444',
    NEUTRAL: '#6b7280',
    MARKET_CLOSED: '#f59e0b'
  }
};