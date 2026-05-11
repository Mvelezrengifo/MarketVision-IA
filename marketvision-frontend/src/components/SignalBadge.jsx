import React from 'react';
import { ROBOT_COLORS } from '../config';

const SignalBadge = ({ signal, confidence = 0 }) => {
  const colors = ROBOT_COLORS[signal] || ROBOT_COLORS.DEFAULT;

  const signalInfo = {
    BUY: { label: 'COMPRA', icon: '🟢' },
    SELL: { label: 'VENTA', icon: '🔴' },
    NEUTRAL: { label: 'NEUTRAL', icon: '⚪' },
    MARKET_CLOSED: { label: 'MERCADO CERRADO', icon: '🚫' },
    LOADING: { label: 'CARGANDO', icon: '⏳' },
    ERROR: { label: 'ERROR', icon: '⚠️' }
  };

  const info = signalInfo[signal] || { label: signal, icon: '⚪' };

  return (
    <div className="flex items-center gap-3">
      <span
        className="px-4 py-2 rounded-full text-xs font-bold uppercase tracking-wider"
        style={{ backgroundColor: colors.primary, color: '#fff' }}
      >
        {info.icon} {info.label}
      </span>
      {confidence > 0 && (
        <span className="text-xs text-gray-400">
          Confianza: {(confidence * 100).toFixed(0)}%
        </span>
      )}
    </div>
  );
};

export default SignalBadge;