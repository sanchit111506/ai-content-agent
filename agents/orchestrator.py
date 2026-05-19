"""
Universal AI Orchestrator — fast path + per-chat memory.
"""

import os
import re
import logging
from datetime import datetime
from functools import lru_cache
from importlib import import_module

import pandas as pd
from pypdf import PdfReader
from docx import Document
import ollama

from memory.memory_manager import save_interaction, get_formatted_memory
from tools.search_tool import search_web

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

MODEL_MAPPING = {
    "Auto":       "phi3:mini",
    "Moderate":   "qwen2.5:7b",
    "DeepSearch": "qwen2.5:7b",
}

USE_CREWAI = os.getenv("USE_CREWAI", "0") == "1"
_FILE_CHAR_LIMIT = 24_000


def _today() -> str:
    return datetime.now().strftime("%A, %B %d, %Y")


_SPECIALIST_PROMPTS: dict[str, str] = {
    "coding": (
        "You are a Senior Software Engineering Specialist. Generate "
        "production-quality code with brief, clear explanations. Cover "
        "Python, FastAPI, Docker, Kubernetes, backend engineering, DevOps. "
        "Always use markdown code blocks. Be concise."
    ),
    "math": (
        "You are a Mathematics and Science Specialist. Solve problems "
        "step-by-step. Use formulas. Keep explanations educational but concise."
    ),
    "research": (
        "You are a Web Research Specialist. Use the provided web search "
        "results as your PRIMARY source. Cite source URLs inline. "
        "Never invent statistics or quotes."
    ),
    "writer": (
        "You are a Universal AI Content Writer. Generate professional, "
        "highly readable content. Use markdown. Avoid repetition."
    ),
    "seo": (
        "You are an SEO & Content Optimization Specialist. Optimize for "
        "keywords, search intent, readability. Use proper headings. "
        "No keyword stuffing."
    ),
    "trend": (
        "You are a Trend Intelligence Specialist. Analyze emerging tech "
        "trends and market shifts. Focus on recent developments."
    ),
    "document": (
        "You are a Document Intelligence Specialist. Analyze uploaded "
        "documents precisely. Extract key facts. Summarize concisely."
    ),
    "rag": (
        "You are a RAG Knowledge Specialist. Answer ONLY from the provided "
        "document context. If the answer isn't in the context, say so plainly."
    ),
    "conversion": (
        "You are a File Conversion Specialist. Provide clear step-by-step "
        "conversion guidance. Mention tools (pandoc, LibreOffice, python-docx)."
    ),
    "image": (
        "You are an Image Processing Specialist. Guide through resizing, "
        "compression, format conversion with CLI examples (Pillow, ImageMagick)."
    ),
}


def _system_prompt(mode: str, specialist: str = "") -> str:
    base = (
        f"Today's date is {_today()}.\n\n"
        f"RULES FOR YOUR RESPONSE:\n"
        f"1. The user's LATEST request is the ONLY thing you must answer. "
        f"It appears in the section marked 'USER REQUEST'.\n"
        f"2. If 'CONVERSATION HISTORY' is provided, use it ONLY to resolve "
        f"references like 'this', 'that', 'the above'. Do NOT answer "
        f"questions from the history again.\n"
        f"3. If the user asks for improvements/changes to 'the above' or "
        f"'the previous' answer, locate the most recent ASSISTANT message "
        f"in history and refine THAT specific content.\n"
        f"4. Never refer to a training-data cutoff. If you lack current "
        f"info, say so plainly.\n\n"
    )
    mode_style = {
        "Auto": "Style: concise and natural.",
        "Moderate": "Style: structured markdown.",
        "DeepSearch": "Style: detailed, structured analysis with headings, bullets, code/CLI examples.",
    }
    parts = [base, mode_style.get(mode, mode_style["Auto"])]
    if specialist:
        parts.append(specialist)
    return " ".join(parts)


INTENT_TIER: dict[str, str] = {
    "coding":     "DeepSearch",
    "document":   "DeepSearch",
    "math":       "DeepSearch",
    "rag":        "DeepSearch",
    "research":   "DeepSearch",
    "writer":     "Moderate",
    "seo":        "Moderate",
    "trend":      "Moderate",
    "conversion": "Moderate",
    "image":      "Moderate",
}

_AGENT_REGISTRY: dict[str, tuple[str, str]] = {
    "coding":     ("agents.coding_agent",          "coding_agent"),
    "document":   ("agents.document_agent",         "document_agent"),
    "conversion": ("agents.file_conversion_agent",  "file_conversion_agent"),
    "image":      ("agents.image_processing_agent", "image_processing_agent"),
    "math":       ("agents.math_agent",             "math_agent"),
    "rag":        ("agents.rag_agent",              "rag_agent"),
    "research":   ("agents.research_agent",         "research_agent"),
    "seo":        ("agents.seo_agent",              "seo_agent"),
    "trend":      ("agents.trend_agent",            "trend_agent"),
    "writer":     ("agents.writer_agent",           "writer_agent"),
}

_INTENT_PATTERNS: dict[str, tuple[list[str], int]] = {
    "coding":     (["python", "react", "fastapi", "docker", "kubernetes",
                    r"\bcode\b", "script", "debug", "devops", "function",
                    "class", "api endpoint", "unit test", "javascript",
                    "typescript", "sql"], 1),
    "document":   ([r"summarize\b.{0,30}\bpdf\b", r"analyze\b.{0,30}\breport\b",
                    "document extraction", "parse document",
                    r"extract\b.{0,20}\bdocument\b"], 1),
    "conversion": ([r"convert\b.{0,20}\bpdf\b", "pdf to word", "excel to pdf",
                    "word to pdf", "pdf to excel", "pdf to docx",
                    "docx to pdf", r"convert\b.{0,20}\bfile\b",
                    "file conversion", r"convert\b.{0,30}\bdocument\b"], 1),
    "image":      (["resize image", "compress image", "image quality",
                    "thumbnail", r"edit\b.{0,15}\bimage\b",
                    r"crop\b.{0,15}\bimage\b"], 1),
    "math":       ([r"solve\b.{0,20}\bequation\b", "calculus", r"\balgebra\b",
                    r"\bcalculate\b.{0,30}", r"physics problem",
                    r"\bstatistics\b", r"\bintegral\b", r"\bderivative\b",
                    r"\bmatrix\b"], 1),
    "rag":        (["search my files", "knowledge base",
                    r"from\b.{0,20}\buploaded documents\b",
                    "semantic search", r"from\b.{0,20}\bmy documents\b"], 1),
    "research":   ([r"search the web", r"latest news\b.{0,30}",
                    r"find facts on", "research internet",
                    r"what.s happening with", r"current status of"], 1),
    "seo":        (["seo keyword", "rank math", "google ranking",
                    "search intent", "optimize blog", "meta description",
                    "backlink", "serp"], 1),
    "trend":      (["trending technology", "emerging trend", "viral topic",
                    "future tech", "industry trend"], 1),
    "writer":     ([r"write\b.{0,15}\bblog\b", "write documentation",
                    r"draft\b.{0,15}\barticle\b", r"write\b.{0,15}\bessay\b",
                    r"write\b.{0,15}\bpost\b", r"write\b.{0,20}\bcopy\b"], 1),
}

_NEEDS_WEB_PATTERNS = [
    r"\bwho is\b", r"\bwhat is\b", r"\bwhere is\b", r"\bwhen is\b",
    r"\blatest\b", r"\bcurrent\b", r"\btoday\b", r"\bnow\b",
    r"\b202[4-9]\b", r"\b203\d\b",
    r"\bnews\b", r"\bprice\b", r"\bstock\b", r"\bmarket\b",
    r"\brichest\b", r"\bpresident\b", r"\bceo\b",
    r"\bweather\b", r"\bsensex\b", r"\bnifty\b",
    r"\brecent\b", r"\bversion\b",
    r"\bwar\b", r"\belection\b", r"\bsituation\b",
]

_FOLLOWUP_PATTERNS = [
    r"\bthis\b", r"\bthat\b", r"\bthose\b", r"\bthese\b",
    r"\bit\b", r"\bthe (above|topic|situation|issue|thing|problem|matter|code|answer|response|solution)\b",
    r"\babove\b", r"\bprevious\b", r"\bearlier\b", r"\blast\b",
    r"\bmore (about|on|info|detail)\b", r"\btell me more\b",
    r"\bcontinue\b", r"\bgo on\b", r"\belaborate\b",
    r"\bimprove(ment)?\b", r"\bbetter\b", r"\boptimize\b",
    r"\bany (other|more)\b", r"\bcan you (also|please)\b",
    r"\bfix\b", r"\bchange\b", r"\bmodify\b",
]


def _needs_web_search(prompt: str) -> bool:
    p = prompt.lower()
    return any(re.search(pat, p) for pat in _NEEDS_WEB_PATTERNS)


def _is_followup(prompt: str) -> bool:
    p = prompt.lower()
    return any(re.search(pat, p) for pat in _FOLLOWUP_PATTERNS)


@lru_cache(maxsize=None)
def _load_agent(intent: str):
    module_path, obj_name = _AGENT_REGISTRY[intent]
    module = import_module(module_path)
    return getattr(module, obj_name)


def extract_file_content(file_paths: list) -> str:
    extracted_text: list[str] = []
    for file_path in file_paths:
        try:
            ext = os.path.splitext(file_path)[1].lower()
            if ext == ".pdf":
                reader = PdfReader(file_path)
                text = "".join(page.extract_text() or "" for page in reader.pages)
            elif ext == ".docx":
                doc = Document(file_path)
                text = "\n".join(p.text for p in doc.paragraphs)
            elif ext == ".txt":
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
            elif ext == ".csv":
                df = pd.read_csv(file_path)
                text = f"CSV Preview (first 100 rows):\n{df.head(100).to_string()}"
            elif ext == ".xlsx":
                df = pd.read_excel(file_path)
                text = f"Excel Preview (first 100 rows):\n{df.head(100).to_string()}"
            else:
                text = f"[Unsupported file skipped: {file_path}]"
            extracted_text.append(text)
        except Exception as exc:
            extracted_text.append(f"[Error reading {file_path}: {exc}]")
            log.warning("File extraction failed for %s: %s", file_path, exc)

    combined = "\n\n".join(extracted_text)
    if len(combined) > _FILE_CHAR_LIMIT:
        log.warning("File content truncated from %d to %d chars.",
                    len(combined), _FILE_CHAR_LIMIT)
        combined = combined[:_FILE_CHAR_LIMIT] + "\n\n[… content truncated …]"
    return combined


def _detect_intent(prompt: str) -> str:
    scores: dict[str, int] = {}
    for intent, (patterns, _min) in _INTENT_PATTERNS.items():
        hit = sum(1 for pat in patterns if re.search(pat, prompt, re.IGNORECASE))
        scores[intent] = hit
    best_intent = max(scores, key=scores.get)
    required_min = _INTENT_PATTERNS[best_intent][1]
    return best_intent if scores[best_intent] >= required_min else "general"


def _detect_intent_with_context(prompt: str, history: list[dict]) -> str:
    direct = _detect_intent(prompt)
    if direct != "general":
        return direct
    if _is_followup(prompt) and history:
        for msg in reversed(history):
            if msg.get("role") == "user":
                prior_intent = _detect_intent(msg.get("content", ""))
                if prior_intent != "general":
                    log.info("📌 Inherited intent '%s' from previous turn", prior_intent)
                    return prior_intent
    return "general"


def _resolve_model_for_intent(intent: str, mode: str) -> str:
    tier = INTENT_TIER.get(intent)
    if tier and tier in MODEL_MAPPING:
        return MODEL_MAPPING[tier]
    return MODEL_MAPPING.get(mode, MODEL_MAPPING["Auto"])


def _get_options(mode: str) -> dict:
    configs = {
        "Auto":       {"temperature": 0.2, "top_p": 0.8, "num_predict": 500,
                       "num_ctx": 2048, "repeat_penalty": 1.2},
        "Moderate":   {"temperature": 0.3, "top_p": 0.9, "num_predict": 1000,
                       "num_ctx": 4096, "repeat_penalty": 1.15},
        "DeepSearch": {"temperature": 0.2, "top_p": 0.9, "num_predict": 1500,
                       "num_ctx": 4096, "repeat_penalty": 1.15},
    }
    return configs.get(mode, configs["Auto"])


def _format_chat_history(history: list[dict]) -> str:
    if not history:
        return ""
    lines = []
    for msg in history[-6:]:
        role = (msg.get("role") or "user").upper()
        content = (msg.get("content") or "").strip()
        if not content:
            continue
        if len(content) > 1200:
            content = content[:1200] + " …[truncated]"
        lines.append(f"{role}: {content}")
    return "\n\n".join(lines)


def _build_prompt(prompt: str, files_content: str, web_results: str,
                  chat_history: str, fallback_memory: str) -> str:
    sections: list[str] = []
    if chat_history:
        sections.append(
            f"--- CONVERSATION HISTORY (most recent at the bottom) ---\n"
            f"{chat_history}\n--- END HISTORY ---"
        )
    elif fallback_memory:
        sections.append(
            f"--- PRIOR MEMORY ---\n{fallback_memory}\n--- END MEMORY ---"
        )
    if web_results:
        sections.append(
            f"--- LIVE WEB SEARCH RESULTS ---\n{web_results}\n--- END WEB ---"
        )
    if files_content:
        sections.append(
            f"--- UPLOADED FILE CONTENT ---\n{files_content}\n--- END FILE ---"
        )
    sections.append(f"=== USER REQUEST ===\n{prompt}\n=== END REQUEST ===")
    return "\n\n".join(sections)


async def _run_ollama(model: str, prompt: str, system: str, mode: str) -> str:
    client = ollama.AsyncClient()
    response = await client.generate(
        model=model,
        prompt=prompt,
        system=system,
        options=_get_options(mode),
        keep_alive="30m",
    )
    if isinstance(response, dict):
        return response.get("response", "")
    return getattr(response, "response", str(response))


# =========================================================
# MAIN ORCHESTRATOR
# =========================================================
async def generate_content(
    prompt: str,
    mode: str = "Auto",
    uploaded_files: list | None = None,
    chat_history: list[dict] | None = None,
    chat_id: str | None = None,
) -> str:
    uploaded_files = uploaded_files or []
    chat_history = chat_history or []
    mode = mode.strip() if mode.strip() in MODEL_MAPPING else "Auto"

    intent = _detect_intent_with_context(prompt, chat_history)
    intent_tier = INTENT_TIER.get(intent, mode)
    intent_model = _resolve_model_for_intent(intent, mode)
    specialist_prompt = _SPECIALIST_PROMPTS.get(intent, "")

    log.info("=" * 60)
    log.info("📩 MESSAGE    : %s", prompt[:120])
    log.info("🆔 CHAT_ID    : %s", chat_id or "default")
    log.info("🔥 MODE       : %s  |  🧠 MODEL: %s", mode, MODEL_MAPPING[mode])
    log.info("🎯 INTENT     : %s", intent.upper())
    log.info("⚙️  TIER       : %s  |  🧠 MODEL: %s", intent_tier, intent_model)
    log.info("🗨️  HISTORY    : %d msgs   📎 FILES: %s",
             len(chat_history), uploaded_files or "none")
    log.info("=" * 60)

    extracted_files = extract_file_content(uploaded_files) if uploaded_files else ""
    history_text = _format_chat_history(chat_history)
    followup = _is_followup(prompt)

    if USE_CREWAI and intent != "general" and intent in _AGENT_REGISTRY:
        log.info("🚀 [DEBUG] Using CrewAI agent: %s_agent", intent)
        try:
            from crewai import Task, Crew
            selected_agent = _load_agent(intent)
            task = Task(
                description=f"Today: {_today()}\n\nUser: {prompt}",
                expected_output="A complete, accurate response.",
                agent=selected_agent,
            )
            crew = Crew(agents=[selected_agent], tasks=[task], verbose=False)
            result = await crew.kickoff_async()
            final_output = getattr(result, "raw", None) or str(result)
        except Exception as exc:
            log.error("CrewAI flow failed: %s", exc)
            final_output = f"Agent Execution Error: {exc}"

    else:
        web_results = ""
        if not followup and (_needs_web_search(prompt) or intent == "research"):
            log.info("🔎 Running web search…")
            try:
                web_results = search_web(prompt)
                log.info("✅ Web search OK (%d chars)", len(web_results))
            except Exception as exc:
                log.warning("Web search failed: %s", exc)
        elif followup:
            log.info("↩️ Follow-up detected — skipping web search, using history only")

        log.info("⚡ FAST PATH  [intent=%s | model=%s | web=%s | history=%s | followup=%s]",
                 intent, intent_model, bool(web_results),
                 bool(history_text), followup)

        # Per-chat memory fallback (only when frontend didn't send history)
        fallback_memory = ""
        if not history_text:
            try:
                fallback_memory = get_formatted_memory(chat_id=chat_id)
            except Exception as exc:
                log.warning("Memory fetch failed: %s", exc)

        full_prompt = _build_prompt(
            prompt=prompt,
            files_content=extracted_files,
            web_results=web_results,
            chat_history=history_text,
            fallback_memory=fallback_memory,
        )

        system_message = _system_prompt(intent_tier, specialist_prompt)

        try:
            final_output = await _run_ollama(
                model=intent_model,
                prompt=full_prompt,
                system=system_message,
                mode=intent_tier,
            )
        except Exception as exc:
            log.exception("Ollama generation failed")
            return f"Error generating response: {exc}"

    # Save with chat_id so future requests to this chat see only its history
    try:
        save_interaction(
            user_prompt=prompt,
            ai_response=final_output,
            chat_id=chat_id,
            mode=mode,
            intent=intent,
        )
    except Exception as exc:
        log.warning("Memory save failed: %s", exc)

    if mode == "DeepSearch" or intent != "general":
        try:
            os.makedirs("generated_content", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prefix = intent if intent != "general" else "deepsearch"
            filename = f"generated_content/{prefix}_{timestamp}.md"
            with open(filename, "w", encoding="utf-8") as fh:
                fh.write(final_output)
            log.info("💾 SAVED: %s", filename)
        except Exception as exc:
            log.warning("File save failed: %s", exc)

    return final_output
