import React from 'react';
import { ROBOT_COLORS } from '../config';

const RobotDisplay = ({
  signal = 'NEUTRAL',
  size = 'large',
  isLoading = false,
  isError = false
}) => {
  let displaySignal = signal;

  if (isLoading) {
    displaySignal = 'LOADING';
  } else if (isError) {
    displaySignal = 'ERROR';
  }

  const colors = {
    ...ROBOT_COLORS,
    LOADING: {
      primary: '#6b7280',
      glow: '#9ca3af',
      bg: '#1f2937'
    },
    ERROR: {
      primary: '#ef4444',
      glow: '#f87171',
      bg: '#371515'
    }
  }[displaySignal] || ROBOT_COLORS.DEFAULT;

  const sizeClasses = {
    small: 'w-32 h-32',
    medium: 'w-48 h-48',
    large: 'w-64 h-64',
    xlarge: 'w-80 h-80'
  };

  return (
    <div className={`relative ${sizeClasses[size]} transition-all duration-500`}>
      {/* Glow Effect */}
      <div
        className="absolute inset-0 rounded-full blur-3xl opacity-50 animate-pulse"
        style={{ backgroundColor: colors.glow }}
      />

      {/* Robot Container */}
      <div
        className="relative w-full h-full rounded-full flex items-center justify-center transition-all duration-500"
        style={{
          backgroundColor: colors.bg,
          border: `4px solid ${colors.primary}`,
          boxShadow: `0 0 40px ${colors.glow}`
        }}
      >
        {/* Robot Image con Fallback */}
        <img
          src="/Copilot_20260504_095330.png"
          alt="🤖"
          className="w-3/4 h-3/4 object-contain"
          loading="eager"
          fetchpriority="high"
          onError={(e) => {
            // Si la imagen falla, mostrar emoji
            e.target.style.display = 'none';
            e.target.parentElement.innerHTML = '🤖';
            e.target.parentElement.style.fontSize = size === 'xlarge' ? '120px' : '80px';
          }}
        />
      </div>

      {/* Signal Label */}
      <div className="absolute -bottom-14 left-1/2 transform -translate-x-1/2 whitespace-nowrap">
        <span
          className="px-6 py-2 rounded-full text-sm font-bold uppercase tracking-wider"
          style={{
            backgroundColor: colors.primary,
            color: '#fff',
            boxShadow: `0 0 20px ${colors.glow}`
          }}
        >
          {isLoading ? '⏳ Cargando...' : isError ? '⚠️ Error' : signal.replace('_', ' ')}
        </span>
      </div>
    </div>
  );
};

export default RobotDisplay;