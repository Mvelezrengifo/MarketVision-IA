import React from 'react';
import SignalBadge from './SignalBadge';

const AssetCard = ({ symbol, data, history, onRefresh }) => {
  if (!data) {
    return (
      <div className="bg-gray-900 rounded-2xl p-8 border border-gray-800 text-center">
        <p className="text-gray-400">Sin datos disponibles</p>
      </div>
    );
  }

  const {
    forecast_signal,
    signal_confidence,
    price_usd,
    technical_indicators,
    market_status,
    asset_class
  } = data;

  return (
    <div className="bg-gray-900 rounded-2xl p-8 border border-gray-800 shadow-2xl w-full max-w-lg">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-3xl font-bold text-white">{symbol}</h2>
          <p className="text-gray-400 text-sm capitalize">{asset_class}</p>
        </div>
        <button
          onClick={onRefresh}
          className="p-3 rounded-lg bg-gray-800 hover:bg-gray-700 transition"
        >
          🔄
        </button>
      </div>

      {/* Price */}
      <div className="mb-6">
        <p className="text-4xl font-bold text-white mb-2">
          ${price_usd?.toLocaleString() || 'N/A'}
        </p>
        <SignalBadge signal={forecast_signal} confidence={signal_confidence} />
      </div>

      {/* Indicators Grid */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-gray-800 rounded-xl p-4">
          <p className="text-gray-400 text-xs mb-1">RSI (14)</p>
          <p className="text-2xl font-bold text-white">
            {technical_indicators?.rsi_14 ?? 'N/A'}
          </p>
        </div>
        <div className="bg-gray-800 rounded-xl p-4">
          <p className="text-gray-400 text-xs mb-1">SMA (20)</p>
          <p className="text-2xl font-bold text-white">
            ${technical_indicators?.sma_20?.toLocaleString() ?? 'N/A'}
          </p>
        </div>
      </div>

      {/* Market Status */}
      <div className="pt-4 border-t border-gray-800">
        <p className="text-gray-400 text-sm">
          Estado del Mercado: <span className="text-white font-medium">{market_status || 'Desconocido'}</span>
        </p>
      </div>
    </div>
  );
};

export default AssetCard;