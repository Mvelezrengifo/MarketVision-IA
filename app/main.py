from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
from typing import Optional

from app.services.ai_service import ensure_analysis_cached, generate_signal

app = FastAPI(title="MarketVision AI Forecast", version="3.5")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Datos base actualizados con tendencias variadas (alcista, lateral, BAJISTA)
ASSETS_BASE = {
    "BTC": {"price": 85320, "rsi": 58, "sma": 84200, "trend": "alcista", "confidence": 0.82, "class": "crypto"},
    "ETH": {"price": 3210, "rsi": 52, "sma": 3150, "trend": "alcista", "confidence": 0.75, "class": "crypto"},
    "NVDA": {"price": 895, "rsi": 65, "sma": 870, "trend": "alcista", "confidence": 0.85, "class": "equity"},
    "AAPL": {"price": 176, "rsi": 48, "sma": 172, "trend": "lateral", "confidence": 0.55, "class": "equity"},
    "GOLD": {"price": 2352, "rsi": 45, "sma": 2330, "trend": "alcista", "confidence": 0.78, "class": "macro"},
    "MSFT": {"price": 420, "rsi": 62, "sma": 412, "trend": "alcista", "confidence": 0.88, "class": "equity"},
    "DOGE": {"price": 0.15, "rsi": 42, "sma": 0.14, "trend": "lateral", "confidence": 0.65, "class": "crypto"},
    "SOL": {"price": 180, "rsi": 55, "sma": 170, "trend": "lateral", "confidence": 0.72, "class": "crypto"},
    "AMZN": {"price": 185, "rsi": 60, "sma": 178, "trend": "alcista", "confidence": 0.80, "class": "equity"},
    "META": {"price": 510, "rsi": 58, "sma": 495, "trend": "alcista", "confidence": 0.78, "class": "equity"},
    # 🔥 NUEVO ACTIVO CON TENENCIA BAJISTA (para mostrar señal de VENTA)
    "TSLA": {"price": 168, "rsi": 72, "sma": 175, "trend": "bajista", "confidence": 0.65, "class": "equity"},
}


def get_projected_history(symbol: str, points: int = 30):
    base = ASSETS_BASE[symbol]
    current = base["price"]
    if base["trend"] == "alcista":
        factor = 1.03
    elif base["trend"] == "bajista":
        factor = 0.97
    else:
        factor = 1.0
    target = current * factor
    history = []
    for i in range(points):
        t = i / (points - 1)
        price = current + (target - current) * (t ** 1.2)
        history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "price_usd": round(price, 2)
        })
    return history


@app.get("/")
async def root():
    return {"message": "MarketVision AI Forecast API", "status": "online"}


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/assets/list")
async def list_assets():
    return {"assets": list(ASSETS_BASE.keys())}


@app.get("/assets/{symbol}")
async def get_forecast(symbol: str, include_history: bool = True):
    symbol = symbol.upper()
    if symbol not in ASSETS_BASE:
        raise HTTPException(404, "Activo no encontrado")
    base = ASSETS_BASE[symbol]
    history = get_projected_history(symbol, 30) if include_history else []

    # Obtener análisis y la señal calculada por reglas
    analysis, signal = ensure_analysis_cached(
        symbol=symbol,
        asset_class=base["class"],
        current_price=base["price"],
        rsi=base["rsi"],
        sma=base["sma"],
        trend=base["trend"],
        confidence=base["confidence"]
    )

    # También recalcular señal por si acaso (consistencia)
    final_signal = signal
    forecast_price = base["price"] * (
        1.03 if base["trend"] == "alcista" else 0.97 if base["trend"] == "bajista" else 1.0)
    percent_change = ((forecast_price - base["price"]) / base["price"]) * 100

    sentiment_score = 50 + (base["rsi"] - 50) * 0.5
    sentiment = {"score": round(sentiment_score, 1),
                 "trend": "positive" if sentiment_score > 55 else "negative" if sentiment_score < 45 else "neutral"}
    risk_level = "high" if base["rsi"] > 70 or base["trend"] == "bajista" else "medium" if base[
                                                                                               "confidence"] < 0.7 else "low"

    return {
        "symbol": symbol,
        "asset_class": base["class"],
        "asset_name": symbol,
        "price_usd": base["price"],
        "forecast_price_usd": round(forecast_price, 2),
        "percentage_change": round(percent_change, 2),
        "forecast_signal": final_signal,  # BUY, SELL o NEUTRAL
        "signal_confidence": base["confidence"],
        "signal_reasoning": [analysis],
        "technical_indicators": {"sma_20": base["sma"], "rsi_14": base["rsi"]},
        "market_status": "OPEN",
        "market_is_closed": False,
        "risk_level": risk_level,
        "analysis": analysis,
        "trend": base["trend"],
        "price_history": history,
        "sentiment": sentiment,
        "risk": {"level": risk_level, "score": f"{base['confidence'] * 10:.1f}/10"},
        "alerts": []
    }


@app.get("/assets/{symbol}/history")
async def get_history(symbol: str, limit: int = 30):
    if symbol.upper() not in ASSETS_BASE:
        raise HTTPException(404, "No data")
    history = get_projected_history(symbol.upper(), limit)
    return {"symbol": symbol, "prices": history}