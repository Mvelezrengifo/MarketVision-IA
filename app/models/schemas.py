# MokesoftIA - Pydantic Schemas for API Responses
# Autor: Nex

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class SyncResponse(BaseModel):
    status: str
    message: str
    data: List[Dict[str, Any]]
    last_sync: str
    source_bucket: str
    source_prefix: str

class MetricItem(BaseModel):
    symbol: str
    asset_class: str
    current_price: float
    volatility_24h: float
    trend: str
    risk_score: float
    risk_level: str

class AnomalyItem(BaseModel):
    symbol: str
    type: str
    value: float
    threshold: float
    detected_at: str

class RiskSummary(BaseModel):
    average_risk: float
    max_risk: float
    min_risk: float
    high_risk_assets: int
    total_assets_analyzed: int

class MetricsResponse(BaseModel):
    status: str
    metrics: List[MetricItem]
    anomalies: List[AnomalyItem]
    risk_summary: RiskSummary
    calculated_at: str
    data_points_analyzed: int

class LayerStatus(BaseModel):
    prefix: str
    file_count: int
    last_update: str
    status: str

class AwsMetrics(BaseModel):
    estimated_monthly_cost_usd: float
    lambda_invocations_estimate: int
    s3_storage_mb_estimate: float
    free_tier_status: str

class PortfolioStatusResponse(BaseModel):
    status: str
    pipeline_health: str
    layers: Dict[str, LayerStatus]
    last_update: str
    aws_metrics: AwsMetrics
    generated_at: str