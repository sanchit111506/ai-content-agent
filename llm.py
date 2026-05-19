"""
Centralized LLM factory for Universal AI.

Two-model setup
───────────────
- light_llm    → phi3:mini      (Auto mode, light tasks, normal chat)
- moderate_llm → qwen2.5:7b     (Moderate + DeepSearch, all agent tasks)

Why only two models?
────────────────────
On CPU hardware, the 14B model is too slow to be practical.
qwen2.5:7b delivers excellent quality at 3-5x the speed.
phi3:mini handles quick conversational tasks in 2-5 seconds.

For backward compatibility we also export ``deepsearch_llm`` as an
alias for ``moderate_llm`` so existing agent imports keep working.
"""

import os
from crewai import LLM

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
KEEP_ALIVE = "30m"

# ──────────────────────────────────────────────────────────
# LIGHT TIER — phi3:mini  (~2.3 GB, very fast)
# Used for: Auto mode, normal chat, simple Q&A
# ──────────────────────────────────────────────────────────
light_llm = LLM(
    model="ollama/phi3:mini",
    base_url=OLLAMA_BASE_URL,
    temperature=0.3,
    max_tokens=400,
)

# ──────────────────────────────────────────────────────────
# MODERATE / DEEPSEARCH TIER — qwen2.5:7b  (~4.7 GB)
# Used for: all 10 agents (coding, math, rag, research, etc.)
# Also handles DeepSearch mode in the orchestrator.
# ──────────────────────────────────────────────────────────
moderate_llm = LLM(
    model="ollama/qwen2.5:7b",
    base_url=OLLAMA_BASE_URL,
    temperature=0.3,
    max_tokens=1500,
)

# Alias kept for backward compatibility with old agent imports.
# Both names point to the SAME instance.
deepsearch_llm = moderate_llm


# ──────────────────────────────────────────────────────────
# PRELOAD HELPER
# ──────────────────────────────────────────────────────────
MODELS_TO_PRELOAD = ["phi3:mini", "qwen2.5:7b"]


async def preload_models() -> None:
    """Warm both models in RAM so first request isn't a cold start."""
    import ollama
    client = ollama.AsyncClient(host=OLLAMA_BASE_URL)
    for name in MODELS_TO_PRELOAD:
        try:
            await client.generate(
                model=name,
                prompt="hi",
                keep_alive=KEEP_ALIVE,
                options={"num_predict": 1},
            )
            print(f"✅ Preloaded {name}")
        except Exception as exc:
            print(f"⚠️  Could not preload {name}: {exc}")
