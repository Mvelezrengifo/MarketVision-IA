# MokesoftIA - Metrics Service (Nova's Logic)
# Autor: Nex (implementando lógica de Nova)

import statistics
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from app.config import settings


def calculate_metrics(
        symbol: Optional[str] = None,
        asset_class: Optional[str] = None
) -> Dict[str, Any]:
    """
    Calcula indicadores de riesgo y anomalías financieras.
    Lógica supervisada por Nova.

    Args:
        symbol: Filtrar por símbolo (ej: BTC, AAPL)
        asset_class: Filtrar por clase (crypto, tech, macro)

    Returns:
        Métricas, anomalías y resumen de riesgo
    """
    # NOTA: En producción, esto leería de S3 Gold Layer o Athena
    # Para demo, usamos datos simulados basados en la estructura real

    metrics = []
    anomalies = []

    # Datos de ejemplo (reemplazar con llamada real a S3/Athena)
    sample_data = [
        {"symbol": "BTC", "asset_class": "crypto", "price": 67432.50, "volatility": 0.035},
        {"symbol": "ETH", "asset_class": "crypto", "price": 3456.78, "volatility": 0.042},
        {"symbol": "AAPL", "asset_class": "tech", "price": 178.45, "volatility": 0.018},
        {"symbol": "MSFT", "asset_class": "tech", "price": 412.30, "volatility": 0.015},
        {"symbol": "NVDA", "asset_class": "tech", "price": 875.60, "volatility": 0.055},
    ]

    for asset in sample_data:
        # Filtros
        if symbol and asset["symbol"] != symbol:
            continue
        if asset_class and asset["asset_class"] != asset_class:
            continue

        # Calcular tendencia (simulado)
        trend = calculate_trend(asset["volatility"])

        # Calcular riesgo
        risk_score = calculate_risk_score(asset["volatility"], asset["price"])

        # Detectar anomalías
        is_anomaly = detect_anomaly(asset["volatility"])

        metrics.append({
            "symbol": asset["symbol"],
            "asset_class": asset["asset_class"],
            "current_price": asset["price"],
            "volatility_24h": round(asset["volatility"] * 100, 2),
            "trend": trend,
            "risk_score": round(risk_score, 3),
            "risk_level": get_risk_level(risk_score)
        })

        if is_anomaly:
            anomalies.append({
                "symbol": asset["symbol"],
                "type": "high_volatility",
                "value": asset["volatility"],
                "threshold": settings.ANOMALY_THRESHOLD_STD,
                "detected_at": datetime.now(timezone.utc).isoformat()
            })

    # Resumen de riesgo
    risk_scores = [m["risk_score"] for m in metrics]
    risk_summary = {
        "average_risk": round(statistics.mean(risk_scores), 3) if risk_scores else 0,
        "max_risk": round(max(risk_scores), 3) if risk_scores else 0,
        "min_risk": round(min(risk_scores), 3) if risk_scores else 0,
        "high_risk_assets": sum(1 for m in metrics if m["risk_level"] == "high"),
        "total_assets_analyzed": len(metrics)
    }

    return {
        "metrics": metrics,
        "anomalies": anomalies,
        "risk_summary": risk_summary,
        "data_points": len(metrics)
    }


def calculate_trend(volatility: float) -> str:
    """Determina tendencia basada en volatilidad"""
    if volatility > 0.05:
        return "volatile"
    elif volatility > 0.02:
        return "stable"
    else:
        return "calm"


def calculate_risk_score(volatility: float, price: float) -> float:
    """Calcula score de riesgo (0-1)"""
    # Fórmula simplificada: volatilidad pesada + factor de precio
    base_risk = volatility * 10
    price_factor = min(price / 10000, 1.0)  # Normalizar precio
    return min(base_risk + (price_factor * 0.1), 1.0)


def get_risk_level(score: float) -> str:
    """Clasifica nivel de riesgo"""
    if score >= settings.RISK_HIGH_THRESHOLD:
        return "high"
    elif score >= settings.RISK_LOW_THRESHOLD:
        return "medium"
    else:
        return "low"


def detect_anomaly(volatility: float) -> bool:
    """Detecta si la volatilidad es anómala"""
    return volatility > (settings.ANOMALY_THRESHOLD_STD * 0.02)  # 2 std dev