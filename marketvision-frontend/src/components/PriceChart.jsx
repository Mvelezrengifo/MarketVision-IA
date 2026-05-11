import React from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const PriceChart = ({ data, symbol, compact = false }) => {
  const chartData = data.map((point, index) => ({
    ...point,
    index
  }));

  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={chartData}>
        <XAxis dataKey="index" hide />
        <YAxis
          domain={['auto', 'auto']}
          tick={{ fill: '#9ca3af', fontSize: compact ? 10 : 12 }}
          tickFormatter={(value) => `$${value.toLocaleString()}`}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: '#1f2937',
            border: '1px solid #374151',
            borderRadius: '8px'
          }}
          labelStyle={{ color: '#9ca3af' }}
          formatter={(value) => [`$${value.toLocaleString()}`, 'Precio']}
        />
        <Line
          type="monotone"
          dataKey="price_usd"
          stroke="#3b82f6"
          strokeWidth={compact ? 2 : 3}
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default PriceChart;