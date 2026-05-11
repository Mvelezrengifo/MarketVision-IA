import React, { useState, useEffect, useCallback } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ReferenceLine } from 'recharts';
import { getAsset } from './services/api';

const SIGNAL_CONFIG = {
  BUY: { color: '#10b981', text: 'COMPRA', bg: 'rgba(16, 185, 129, 0.15)' },
  SELL: { color: '#ef4444', text: 'VENTA', bg: 'rgba(239, 68, 68, 0.15)' },
  NEUTRAL: { color: '#f59e0b', text: 'NEUTRAL', bg: 'rgba(245, 158, 11, 0.15)' }
};

const styles = `
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: system-ui, sans-serif; background: #050505; color: #e5e7eb; }
  .dashboard { min-height: 100vh; padding: 16px 20px; display: flex; flex-direction: column; gap: 12px; }
  .header { text-align: center; margin-bottom: 4px; }
  .header h1 { font-size: 28px; font-weight: 800; letter-spacing: 3px; background: linear-gradient(90deg, #3b82f6, #10b981); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
  .header p { font-size: 12px; color: #6b7280; margin-top: 2px; }
  .main-grid { display: grid; grid-template-columns: 1fr 280px; gap: 16px; }
  @media (max-width: 900px) { .main-grid { grid-template-columns: 1fr; } }
  .card { background: rgba(20, 20, 30, 0.9); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 16px; }
  .select { width: 100%; padding: 8px 10px; background: #111; border: 1px solid #333; border-radius: 8px; color: white; font-size: 14px; margin-bottom: 12px; }
  .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 12px 0; }
  .stat { background: #0f0f15; padding: 8px 6px; border-radius: 10px; text-align: center; }
  .stat-label { font-size: 10px; color: #9ca3af; text-transform: uppercase; }
  .stat-value { font-size: 16px; font-weight: 700; margin-top: 2px; }
  .chart-box { height: 200px; margin: 12px 0; }
  .analysis-box { background: #0a0a0f; border-radius: 12px; padding: 12px; margin-top: 8px; border-left: 3px solid var(--signal-color); position: relative; }
  .analysis-title { font-size: 11px; text-transform: uppercase; color: #9ca3af; letter-spacing: 1.5px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center; }
  .analysis-text { font-size: 14px; line-height: 1.4; color: #e5e7eb; }
  .why-button { background: none; border: 1px solid #3b82f6; border-radius: 20px; padding: 4px 12px; font-size: 11px; color: #3b82f6; cursor: pointer; transition: 0.2s; }
  .why-button:hover { background: #3b82f620; }
  .explanation-popup { position: absolute; background: #1a1a2a; border: 1px solid #3b82f6; border-radius: 12px; padding: 12px; width: 280px; right: 0; top: 100%; margin-top: 8px; z-index: 10; backdrop-filter: blur(8px); box-shadow: 0 4px 20px rgba(0,0,0,0.5); font-size: 12px; color: #cbd5e1; }
  .popup-close { float: right; cursor: pointer; color: #9ca3af; margin-left: 8px; }
  .popup-close:hover { color: white; }
  .robot-container { text-align: center; display: flex; flex-direction: column; align-items: center; gap: 8px; }
  .robot-img { width: 100%; max-width: 200px; transition: filter 0.3s; }
  .refresh-btn { background: #3b82f6; border: none; padding: 8px 16px; border-radius: 40px; color: white; font-weight: bold; cursor: pointer; width: 100%; font-size: 14px; margin-top: 8px; }
  .refresh-btn:hover { background: #2563eb; }
  .status-bar { position: fixed; bottom: 12px; right: 12px; background: #111; padding: 4px 10px; border-radius: 20px; font-size: 10px; display: flex; gap: 6px; align-items: center; }
  .status-dot { width: 8px; height: 8px; border-radius: 50%; background: #10b981; }
  .price-row { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px; }
  .signal-badge { padding: 2px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; background: var(--bg); color: var(--color); }
  .alert-item { font-size: 11px; padding: 4px 0; border-bottom: 1px solid #222; }
  .loading-explanation { font-size: 11px; color: #3b82f6; text-align: center; padding: 8px; }
`;

function App() {
  const [availableAssets, setAvailableAssets] = useState([]);
  const [selectedSymbol, setSelectedSymbol] = useState('');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [showExplanation, setShowExplanation] = useState(false);
  const [explanationText, setExplanationText] = useState('');
  const [loadingExplanation, setLoadingExplanation] = useState(false);

  // Cargar lista de activos desde el backend
  useEffect(() => {
    fetch('http://localhost:8000/assets/list')
      .then(res => res.json())
      .then(data => {
        const assets = data.assets || [];
        setAvailableAssets(assets);
        if (assets.length > 0 && !selectedSymbol) setSelectedSymbol(assets[0]);
      })
      .catch(err => console.error("Error cargando activos:", err));
  }, []);

  const fetchForecast = useCallback(async () => {
    if (!selectedSymbol) return;
    setLoading(true);
    setError(null);
    try {
      const result = await getAsset(selectedSymbol, true, 30);
      setData(result);
      setLastUpdate(new Date().toLocaleTimeString());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [selectedSymbol]);

  useEffect(() => {
    if (selectedSymbol) fetchForecast();
  }, [selectedSymbol, fetchForecast]);

  const fetchExplanation = async () => {
    if (!selectedSymbol) return;
    setLoadingExplanation(true);
    setExplanationText('');
    try {
      const response = await fetch(`http://localhost:8000/explain/${selectedSymbol}`);
      const result = await response.json();
      setExplanationText(result.explanation || "No se pudo obtener explicación.");
    } catch (err) {
      setExplanationText("Error al conectar con el motor de IA.");
    } finally {
      setLoadingExplanation(false);
    }
  };

  const handleWhyClick = () => {
    if (!showExplanation) {
      fetchExplanation();
    }
    setShowExplanation(!showExplanation);
  };

  const signal = data?.forecast_signal || 'NEUTRAL';
  const sigConfig = SIGNAL_CONFIG[signal] || SIGNAL_CONFIG.NEUTRAL;
  const isPositive = data?.percentage_change > 0;

  let chartPoints = [];
  if (data?.price_history) {
    chartPoints = data.price_history.map((p, idx) => ({
      index: idx,
      price: p.price_usd,
      sma: data.technical_indicators?.sma_20
    }));
    if (data.forecast_price_usd) {
      chartPoints.push({
        index: chartPoints.length,
        price: data.forecast_price_usd,
        sma: data.technical_indicators?.sma_20,
        isForecast: true
      });
    }
  }

  return (
    <>
      <style>{styles}</style>
      <div className="dashboard">
        <div className="header">
          <h1>MARKETVISION</h1>
          <p>Pronóstico financiero con IA</p>
        </div>

        <div className="main-grid">
          <div className="card">
            <select className="select" value={selectedSymbol} onChange={(e) => setSelectedSymbol(e.target.value)}>
              {availableAssets.map(sym => <option key={sym} value={sym}>{sym}</option>)}
            </select>

            {loading && <div style={{ textAlign: 'center', padding: 20 }}>Cargando pronóstico...</div>}
            {error && <div style={{ color: '#ef4444', textAlign: 'center' }}>Error: {error}</div>}
            {data && !loading && (
              <>
                <div className="price-row">
                  <div>
                    <span style={{ fontSize: 24, fontWeight: 'bold' }}>${data.price_usd?.toLocaleString()}</span>
                    <span style={{ marginLeft: 8, fontSize: 14, color: isPositive ? '#10b981' : '#ef4444' }}>
                      {isPositive ? '▲' : '▼'} {Math.abs(data.percentage_change || 0).toFixed(2)}%
                    </span>
                  </div>
                  <div className="signal-badge" style={{ '--color': sigConfig.color, '--bg': sigConfig.bg, color: sigConfig.color, background: sigConfig.bg }}>
                    {sigConfig.text}
                  </div>
                </div>

                <div className="stats-grid">
                  <div className="stat"><div className="stat-label">RSI (14)</div><div className="stat-value">{data.technical_indicators?.rsi_14 ?? '--'}</div></div>
                  <div className="stat"><div className="stat-label">SMA (20)</div><div className="stat-value">${data.technical_indicators?.sma_20?.toLocaleString() ?? '--'}</div></div>
                  <div className="stat"><div className="stat-label">Confianza</div><div className="stat-value">{(data.signal_confidence * 100).toFixed(0)}%</div></div>
                  <div className="stat"><div className="stat-label">Tendencia</div><div className="stat-value" style={{ color: data.trend === 'alcista' ? '#10b981' : '#f59e0b' }}>{data.trend === 'alcista' ? 'Alcista' : 'Lateral'}</div></div>
                </div>

                <div className="stats-grid" style={{ marginTop: 0 }}>
                  <div className="stat"><div className="stat-label">Sentimiento</div><div className="stat-value" style={{ color: data.sentiment?.trend === 'positive' ? '#10b981' : '#f59e0b' }}>{data.sentiment?.score || 50}%</div></div>
                  <div className="stat"><div className="stat-label">Riesgo</div><div className="stat-value" style={{ color: data.risk?.level === 'high' ? '#ef4444' : '#f59e0b' }}>{data.risk?.level?.toUpperCase() || 'MEDIUM'}</div></div>
                </div>

                <div className="chart-box">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartPoints}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#222" />
                      <XAxis dataKey="index" hide />
                      <YAxis domain={['auto', 'auto']} tickFormatter={(v) => `$${v.toLocaleString()}`} width={50} />
                      <Tooltip contentStyle={{ background: '#111', border: 'none' }} formatter={(value) => [`$${value.toLocaleString()}`, 'Precio']} />
                      <Line type="monotone" dataKey="price" stroke="#3b82f6" strokeWidth={2} dot={false} />
                      <ReferenceLine y={data.technical_indicators?.sma_20} stroke="#fbbf24" strokeDasharray="5 5" label="SMA20" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>

                <div className="analysis-box" style={{ '--signal-color': sigConfig.color }}>
                  <div className="analysis-title">
                    <span>ANÁLISIS DE IA</span>
                    <button className="why-button" onClick={handleWhyClick}>
                      {showExplanation ? '✖ Cerrar' : '❓ ¿Por qué?'}
                    </button>
                  </div>
                  <div className="analysis-text">{data.analysis || data.signal_reasoning?.[0] || "Pronóstico basado en tendencias de mercado y noticias recientes."}</div>
                  {showExplanation && (
                    <div className="explanation-popup">
                      <span className="popup-close" onClick={() => setShowExplanation(false)}>✖</span>
                      <strong style={{ display: 'block', marginBottom: 8 }}>🤖 Explicación de Gemini AI:</strong>
                      {loadingExplanation ? (
                        <div className="loading-explanation">Generando análisis...</div>
                      ) : (
                        <div style={{ fontSize: 12, lineHeight: 1.5 }}>{explanationText || "No se pudo obtener explicación."}</div>
                      )}
                    </div>
                  )}
                </div>

                {data.alerts && data.alerts.length > 0 && (
                  <div className="analysis-box" style={{ borderLeftColor: '#f59e0b', marginTop: 8 }}>
                    <div className="analysis-title">ALERTAS ACTIVAS</div>
                    {data.alerts.map((alert, idx) => (
                      <div key={idx} className="alert-item" style={{ color: alert.priority === 'critical' ? '#ef4444' : '#fbbf24' }}>
                        ⚠️ {alert.message}
                      </div>
                    ))}
                  </div>
                )}

                <button className="refresh-btn" onClick={fetchForecast}>↻ Actualizar pronóstico</button>
                <div style={{ fontSize: 10, color: '#4b5563', textAlign: 'center', marginTop: 8 }}>Última actualización: {lastUpdate}</div>
              </>
            )}
          </div>

          <div className="card robot-container">
            <img src="/robot.svg.png" alt="AI Robot" className="robot-img" style={{ filter: `drop-shadow(0 0 20px ${sigConfig.color})` }} />
            <div style={{ fontWeight: 'bold', color: sigConfig.color, marginTop: 4 }}>Señal: {sigConfig.text}</div>
            <button className="refresh-btn" onClick={fetchForecast}>↻ Nuevo análisis</button>
          </div>
        </div>

        <div className="status-bar"><div className="status-dot"></div><span>IA activa</span></div>
      </div>
    </>
  );
}

export default App;