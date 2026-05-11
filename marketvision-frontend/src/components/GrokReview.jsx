import React, { useState, useEffect } from 'react';
import { getGrokReviews } from '../services/api';

const GrokReview = ({ symbol }) => {
  const [review, setReview] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // 🔮 FUTURO: Descomentar cuando el endpoint esté listo
    // const fetchReview = async () => {
    //   setLoading(true);
    //   const data = await getGrokReviews(symbol);
    //   setReview(data);
    //   setLoading(false);
    // };
    // fetchReview();
  }, [symbol]);

  return (
    <div className="bg-gradient-to-r from-purple-900 to-blue-900 rounded-xl p-4 mt-4">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-2xl">🤖</span>
        <h3 className="text-white font-bold">Análisis Grok AI</h3>
      </div>

      {loading ? (
        <p className="text-gray-400 text-sm">Analizando con Grok...</p>
      ) : review ? (
        <div>
          <p className="text-white text-sm">{review.summary}</p>
          <div className="mt-2 flex gap-2">
            {review.tags?.map((tag, i) => (
              <span key={i} className="px-2 py-1 bg-purple-800 rounded text-xs text-white">
                {tag}
              </span>
            ))}
          </div>
        </div>
      ) : (
        <p className="text-gray-400 text-sm italic">
          Próximamente: Análisis automático con Grok AI
        </p>
      )}
    </div>
  );
};

export default GrokReview;