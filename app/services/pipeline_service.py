# MokesoftIA - Pipeline Status Service
# Autor: Nex

import boto3
from datetime import datetime, timezone
from typing import Dict, Any
from app.config import settings

s3_client = boto3.client('s3', region_name=settings.S3_REGION)


def count_s3_objects(prefix: str) -> int:
    """Cuenta objetos en un prefix de S3"""
    try:
        paginator = s3_client.get_paginator('list_objects_v2')
        count = 0

        for page in paginator.paginate(Bucket=settings.S3_BUCKET, Prefix=prefix):
            if 'Contents' in page:
                count += len(page['Contents'])

        return count
    except:
        return 0


def get_last_modified(prefix: str) -> str:
    """Obtiene timestamp del último archivo modificado"""
    try:
        response = s3_client.list_objects_v2(
            Bucket=settings.S3_BUCKET,
            Prefix=prefix,
            MaxKeys=1
        )

        if 'Contents' in response and response['Contents']:
            return response['Contents'][0]['LastModified'].isoformat()

        return "N/A"
    except:
        return "N/A"


def get_pipeline_status() -> Dict[str, Any]:
    """
    Retorna el estado completo del pipeline de datos.
    """
    # Contar archivos por capa
    bronze_count = count_s3_objects(settings.BRONZE_PREFIX)
    silver_count = count_s3_objects(settings.SILVER_PREFIX)
    gold_count = count_s3_objects(settings.GOLD_PREFIX)

    # Última actualización por capa
    bronze_last = get_last_modified(settings.BRONZE_PREFIX)
    silver_last = get_last_modified(settings.SILVER_PREFIX)
    gold_last = get_last_modified(settings.GOLD_PREFIX)

    # Determinar salud del pipeline
    health = "healthy"
    if gold_count == 0:
        health = "warning"
    if bronze_count > 0 and silver_count == 0 and gold_count == 0:
        health = "critical"

    # Métricas AWS (estimadas para Free Tier)
    aws_metrics = {
        "estimated_monthly_cost_usd": round((bronze_count + silver_count + gold_count) * 0.000005, 2),
        "lambda_invocations_estimate": bronze_count * 2,  # Ingestor + Silver
        "s3_storage_mb_estimate": round((bronze_count + silver_count + gold_count) * 0.05, 2),
        "free_tier_status": "within_limits" if aws_metrics["estimated_monthly_cost_usd"] < 5 else "approaching_limit"
    }

    return {
        "health": health,
        "layers": {
            "bronze": {
                "prefix": settings.BRONZE_PREFIX,
                "file_count": bronze_count,
                "last_update": bronze_last,
                "status": "active" if bronze_count > 0 else "empty"
            },
            "silver": {
                "prefix": settings.SILVER_PREFIX,
                "file_count": silver_count,
                "last_update": silver_last,
                "status": "active" if silver_count > 0 else "empty"
            },
            "gold": {
                "prefix": settings.GOLD_PREFIX,
                "file_count": gold_count,
                "last_update": gold_last,
                "status": "active" if gold_count > 0 else "empty"
            }
        },
        "last_update": max([bronze_last, silver_last, gold_last]),
        "aws_metrics": aws_metrics
    }