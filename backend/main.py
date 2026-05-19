"""
FastAPI entry point for Universal AI backend.

CRITICAL: env vars MUST be set BEFORE importing anything that uses
LiteLLM (which includes llm.py, crewai, and anything from agents/).
"""

# ────────────────────────────────────────────────
# ENV VARS — must be set FIRST
# ────────────────────────────────────────────────
import os

# LiteLLM retry / timeout controls
os.environ["LITELLM_REQUEST_TIMEOUT"] = "180"   # 3 min per LLM call
os.environ["LITELLM_NUM_RETRIES"] = "0"          # no auto-retries
os.environ["LITELLM_DROP_PARAMS"] = "true"

# Telemetry off
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"

# ────────────────────────────────────────────────
# IMPORTS
# ────────────────────────────────────────────────
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from llm import preload_models
from backend.chat import router as chat_router

# ────────────────────────────────────────────────
# LOGGING
# ────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
log = logging.getLogger("universal-ai")


# ────────────────────────────────────────────────
# LIFESPAN — preload both models on startup
# ────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("🚀 Universal AI starting…")
    log.info("⏳ Preloading Ollama models (one-time cost)…")
    try:
        await preload_models()
        log.info("✨ Both models warmed up — first request will be fast.")
    except Exception as exc:
        log.warning("Preload encountered an issue: %s", exc)

    yield

    log.info("🛑 Universal AI shutting down.")


# ────────────────────────────────────────────────
# APP
# ────────────────────────────────────────────────
app = FastAPI(
    title="Universal AI",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "universal-ai"}


@app.get("/")
async def root():
    return {"message": "Universal AI backend is running."}
