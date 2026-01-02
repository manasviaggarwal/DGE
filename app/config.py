"""
Central configuration file for the AI-powered Social Security Application System.

Purpose:
- Centralize environment variables
- Define model, database, and agent settings
- Enable clean separation between logic and configuration
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# -------------------------------------------------
# Base Paths
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

if ENV_FILE.exists():
    load_dotenv(ENV_FILE)

# -------------------------------------------------
# Application Settings
# -------------------------------------------------
APP_NAME = "AI Social Support Eligibility System"
APP_ENV = os.getenv("APP_ENV", "development")
DEBUG = APP_ENV != "production"

# -------------------------------------------------
# Local LLM (Ollama) Configuration
# -------------------------------------------------
OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434"
)

OLLAMA_MODEL_NAME = os.getenv(
    "OLLAMA_MODEL_NAME",
    "llama3.1:8b"
)

LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", 0.2))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", 2048))

# -------------------------------------------------
# Agentic AI Configuration
# -------------------------------------------------
AGENT_REASONING_METHOD = os.getenv(
    "AGENT_REASONING_METHOD",
    "ReAct"  # ReAct / PaS / Reflexion
)

AGENT_ORCHESTRATION_ENGINE = os.getenv(
    "AGENT_ORCHESTRATION_ENGINE",
    "LangGraph"
)

# -------------------------------------------------
# Databases
# -------------------------------------------------

# PostgreSQL (Structured application data)
POSTGRES_URI = os.getenv(
    "POSTGRES_URI",
    "postgresql://postgres:postgres@localhost:5432/social_support"
)

# MongoDB (Documents, OCR output, JSON)
MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb://localhost:27017"
)

MONGODB_DB_NAME = os.getenv(
    "MONGODB_DB_NAME",
    "social_support_documents"
)

# Vector Database (Embeddings)
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_COLLECTION = os.getenv(
    "QDRANT_COLLECTION",
    "applicant_embeddings"
)

# Graph Database (Relationships)
NEO4J_URI = os.getenv(
    "NEO4J_URI",
    "bolt://localhost:7687"
)
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# -------------------------------------------------
# ML Model Configuration
# -------------------------------------------------
MODEL_DIR = BASE_DIR / "app" / "models"

ELIGIBILITY_MODEL_PATH = MODEL_DIR / "eligibility_classifier.pkl"
FEATURE_SCALER_PATH = MODEL_DIR / "feature_scaler.pkl"

APPROVAL_THRESHOLD = float(os.getenv("APPROVAL_THRESHOLD", 0.70))
SOFT_DECLINE_THRESHOLD = float(os.getenv("SOFT_DECLINE_THRESHOLD", 0.40))

# -------------------------------------------------
# Observability (Langfuse)
# -------------------------------------------------
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY", "")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", "")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "http://localhost:3000")

ENABLE_LANGFUSE = bool(
    LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY
)

# -------------------------------------------------
# Security & Compliance
# -------------------------------------------------
PII_FIELDS = [
    "emirates_id",
    "passport_number",
    "phone_number",
    "email",
    "home_address",
    "bank_account_number"
]

DATA_RETENTION_DAYS = int(
    os.getenv("DATA_RETENTION_DAYS", 365)
)

# -------------------------------------------------
# Feature Flags
# -------------------------------------------------
ENABLE_OCR = True
ENABLE_CREDIT_REPORT_CHECK = True
ENABLE_JOB_MATCHING = True
ENABLE_TRAINING_RECOMMENDATIONS = True
