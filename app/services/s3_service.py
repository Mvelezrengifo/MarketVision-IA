import boto3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from app.config import config


class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            region_name=config.S3_REGION,
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
        )
        self.bucket = config.S3_BUCKET
        self.gold_prefix = config.GOLD_PREFIX
        self.silver_prefix = config.SILVER_PREFIX

    # ---------- UTILIDADES ----------
    def get_gold_file(self, key: str) -> Optional[Dict]:
        try:
            resp = self.s3_client.get_object(Bucket=self.bucket, Key=key)
            return json.loads(resp['Body'].read().decode('utf-8'))
        except:
            return None

    def find_asset_in_gold(self, symbol: str, asset_class: str = None) -> Optional[Dict]:
        classes = [asset_class] if asset_class else ["crypto", "equity", "macro"]
        for cls in classes:
            for candidate in [f"{self.gold_prefix}{cls}/{symbol}/gold.json",
                              f"{self.gold_prefix}{cls}/{symbol}/{symbol}_gold.json"]:
                data = self.get_gold_file(candidate)
                if data:
                    return data
        return None

    def get_asset_price_history(self, asset_class: str, symbol: str, limit: int = 50) -> List[Dict]:
        """Retorna historial de precios desde Silver, ordenado por tiempo ascendente."""
        prefix = f"{self.silver_prefix}{asset_class}/{symbol}/"
        prices = []
        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
                if 'Contents' not in page:
                    continue
                objects = sorted(page['Contents'], key=lambda x: x['LastModified'])
                for obj in objects[-limit:]:
                    try:
                        data = json.loads(self.s3_client.get_object(Bucket=self.bucket, Key=obj['Key'])['Body'].read())
                        prices.append({
                            "timestamp": data.get("captured_utc"),
                            "price_usd": float(data.get("price_usd", 0))
                        })
                    except:
                        continue
            return prices[-limit:]
        except Exception as e:
            print(f"Error obteniendo historial {symbol}: {e}")
            return []

    # ---------- ÚLTIMO ESTADO CONOCIDO (para mercados cerrados) ----------
    def get_last_known_state(self, symbol: str, asset_class: str) -> Optional[Dict]:
        """Devuelve el último precio y señal conocidos (Gold o último Silver)."""
        gold = self.find_asset_in_gold(symbol, asset_class)
        if gold:
            # Normalizar campos antiguos si vienen de Lambda v5
            if "forecast" in gold:
                gold["forecast_signal"] = gold["forecast"].get("signal")
                gold["signal_confidence"] = gold["forecast"].get("confidence")
            return {
                "price_usd": gold.get("price_usd"),
                "forecast_signal": gold.get("forecast_signal", "NEUTRAL"),
                "signal_confidence": gold.get("signal_confidence", 0.5),
                "technical_indicators": gold.get("technical_indicators", {}),
                "captured_utc": gold.get("captured_utc"),
                "market_status": gold.get("market_status", "CLOSED"),
                "market_is_closed": True
            }
        # Si no hay Gold, tomar el último Silver
        history = self.get_asset_price_history(asset_class, symbol, limit=1)
        if history:
            return {
                "price_usd": history[-1]["price_usd"],
                "forecast_signal": "NEUTRAL",
                "signal_confidence": 0.3,
                "technical_indicators": {"sma_20": None, "rsi_14": None},
                "captured_utc": history[-1]["timestamp"],
                "market_status": "NO_DATA",
                "market_is_closed": True
            }
        return None

    # ---------- PREDICCIÓN EN TIEMPO REAL (usando historial Silver) ----------
    def calculate_prediction_from_history(self, symbol: str, asset_class: str, limit: int = 50) -> Dict[str, Any]:
        """
        Calcula RSI, SMA y señal de pronóstico usando el historial de Silver.
        Para crypto usa SOLO los últimos 5 puntos (más reactivo).
        Para equity/macro usa hasta `limit` puntos.
        Si no hay suficientes datos, devuelve el último estado conocido.
        """
        # Para crypto: ventana máxima de 5 registros
        if asset_class == "crypto":
            window = min(limit, 5)
        else:
            window = limit

        history = self.get_asset_price_history(asset_class, symbol, window)

        # Si no hay historial o es muy corto, usar último estado conocido
        if len(history) < 2:
            last_state = self.get_last_known_state(symbol, asset_class)
            if last_state:
                last_state["price_history"] = []
                return last_state
            else:
                return {
                    "symbol": symbol,
                    "asset_class": asset_class,
                    "asset_name": symbol,
                    "price_usd": None,
                    "forecast_signal": "NEUTRAL",
                    "signal_confidence": 0.0,
                    "technical_indicators": {"sma_20": None, "rsi_14": None},
                    "price_history": [],
                    "market_status": "INSUFFICIENT_DATA",
                    "market_is_closed": True
                }

        prices = [p["price_usd"] for p in history]
        current_price = prices[-1]
        last_timestamp = history[-1]["timestamp"]

        # SMA (20 periodos) – solo si hay suficientes datos
        sma = None
        if len(prices) >= 20:
            sma = sum(prices[-20:]) / 20

        # RSI (14 periodos)
        rsi = None
        if len(prices) >= 15:
            gains = []
            losses = []
            for i in range(1, len(prices)):
                change = prices[i] - prices[i - 1]
                gains.append(change if change > 0 else 0)
                losses.append(-change if change < 0 else 0)
            avg_gain = sum(gains[-14:]) / 14
            avg_loss = sum(losses[-14:]) / 14
            if avg_loss == 0:
                rsi = 100.0
            else:
                rsi = 100 - (100 / (1 + avg_gain / avg_loss))

        # Generar señal y confianza
        signal = "NEUTRAL"
        confidence = 0.5
        reasoning = []

        if sma is not None:
            if current_price > sma:
                signal = "BUY"
                confidence += 0.2
                reasoning.append("price_above_sma")
            elif current_price < sma:
                signal = "SELL"
                confidence += 0.2
                reasoning.append("price_below_sma")

        if rsi is not None:
            if rsi > 70:
                reasoning.append("rsi_overbought")
                if signal == "BUY":
                    signal = "NEUTRAL"
                    confidence -= 0.1
                else:
                    signal = "SELL"
                    confidence += 0.2
            elif rsi < 30:
                reasoning.append("rsi_oversold")
                if signal == "SELL":
                    signal = "NEUTRAL"
                    confidence -= 0.1
                else:
                    signal = "BUY"
                    confidence += 0.2

        confidence = max(0.0, min(1.0, confidence))
        if confidence < 0.3:
            signal = "NEUTRAL"
            reasoning.append("low_confidence")

        risk_level = "medium"
        if rsi and (rsi > 80 or rsi < 20):
            risk_level = "high"
        elif confidence > 0.7:
            risk_level = "low"

        return {
            "symbol": symbol,
            "asset_class": asset_class,
            "asset_name": symbol,
            "price_usd": current_price,
            "captured_utc": last_timestamp,
            "forecast_signal": signal,
            "signal_confidence": round(confidence, 2),
            "signal_reasoning": reasoning,
            "technical_indicators": {
                "sma_20": round(sma, 2) if sma else None,
                "rsi_14": round(rsi, 2) if rsi else None
            },
            "market_status": "OPEN" if len(history) >= 3 else "LIMITED_DATA",
            "market_is_closed": False,
            "market_warnings": [] if len(history) >= 3 else ["insufficient_history"],
            "risk_level": risk_level,
            "quality_flags": ["realtime_calculation"],
            "price_history": history  # ya contiene los últimos 'window' puntos
        }


s3_service = S3Service()