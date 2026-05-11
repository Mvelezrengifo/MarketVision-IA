import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Grok (ya no se usa, pero se mantiene por compatibilidad)
    GROK_API_KEY = os.getenv("XAI_API_KEY", "")  # si tenías XAI_API_KEY

    # Gemini (nueva)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

    # AWS
    S3_BUCKET = os.getenv("S3_BUCKET", "marketvision-raw-data-velez-315922616034-us-east-1-an")
    S3_REGION = os.getenv("AWS_REGION", "us-east-1")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

    # Data Lake prefixes
    BRONZE_PREFIX = os.getenv("BRONZE_PREFIX", "ingested-raw/")
    SILVER_PREFIX = os.getenv("SILVER_PREFIX", "processed-silver/")
    GOLD_PREFIX = os.getenv("DESTINATION_PREFIX", "processed-gold/")

    # General
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    API_VERSION = "1.0.0"

# 🔥 Instancia global para importar fácilmente
config = Config()