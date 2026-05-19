"""
Web search tool — uses DuckDuckGo by default (no API key required).

If you want better quality results later, you can set one of these
environment variables and the tool will automatically prefer them:

  TAVILY_API_KEY    — https://tavily.com (1000 free searches/month)
  SERPER_API_KEY    — https://serper.dev (2500 free searches/month)

Install requirements:
    pip install ddgs requests
"""

import os
import json
import logging
from datetime import datetime

import requests

log = logging.getLogger(__name__)

# Auto-pick best provider available
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# How many results to fetch per search
MAX_RESULTS = 5
# How many characters of each snippet to keep
SNIPPET_CHARS = 400


def _search_tavily(query: str) -> str:
    """Tavily — best quality, free tier available."""
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "max_results": MAX_RESULTS,
        "search_depth": "basic",
        "include_answer": True,
    }
    r = requests.post(url, json=payload, timeout=15)
    r.raise_for_status()
    data = r.json()

    parts = []
    if data.get("answer"):
        parts.append(f"📌 ANSWER: {data['answer']}\n")

    for i, item in enumerate(data.get("results", [])[:MAX_RESULTS], 1):
        parts.append(
            f"[{i}] {item.get('title', 'Untitled')}\n"
            f"URL: {item.get('url', '')}\n"
            f"{item.get('content', '')[:SNIPPET_CHARS]}\n"
        )
    return "\n".join(parts) or "No results found."


def _search_serper(query: str) -> str:
    """Serper — Google results via API."""
    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
    r = requests.post(url, headers=headers, json={"q": query, "num": MAX_RESULTS}, timeout=15)
    r.raise_for_status()
    data = r.json()

    parts = []
    if data.get("answerBox", {}).get("answer"):
        parts.append(f"📌 ANSWER: {data['answerBox']['answer']}\n")

    for i, item in enumerate(data.get("organic", [])[:MAX_RESULTS], 1):
        parts.append(
            f"[{i}] {item.get('title', 'Untitled')}\n"
            f"URL: {item.get('link', '')}\n"
            f"{item.get('snippet', '')[:SNIPPET_CHARS]}\n"
        )
    return "\n".join(parts) or "No results found."


def _search_duckduckgo(query: str) -> str:
    """DuckDuckGo — free, no API key. Default fallback."""
    try:
        from ddgs import DDGS
    except ImportError:
        return ("❌ Search unavailable: install with `pip install ddgs`")

    parts = []
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=MAX_RESULTS, region="wt-wt"))

        if not results:
            return "No web results found for this query."

        for i, item in enumerate(results, 1):
            parts.append(
                f"[{i}] {item.get('title', 'Untitled')}\n"
                f"URL: {item.get('href', '')}\n"
                f"{item.get('body', '')[:SNIPPET_CHARS]}\n"
            )
        return "\n".join(parts)
    except Exception as exc:
        log.warning("DuckDuckGo search failed: %s", exc)
        return f"❌ Search failed: {exc}"


def search_web(query: str) -> str:
    """
    Main entry point used by all agents.

    Returns a human-readable summary of search results, prefixed with the
    current date so the LLM grounds its answer in TODAY's reality rather
    than its training-data knowledge cutoff.
    """
    if not query or not query.strip():
        return "❌ Empty search query."

    today = datetime.now().strftime("%B %d, %Y")
    log.info("🔎 Web search: %s", query[:100])

    try:
        if TAVILY_API_KEY:
            results = _search_tavily(query)
            provider = "Tavily"
        elif SERPER_API_KEY:
            results = _search_serper(query)
            provider = "Serper"
        else:
            results = _search_duckduckgo(query)
            provider = "DuckDuckGo"

        return (
            f"📅 Today's date: {today}\n"
            f"🔎 Search provider: {provider}\n"
            f"❓ Query: {query}\n\n"
            f"--- WEB RESULTS ---\n{results}\n"
            f"--- END OF RESULTS ---\n\n"
            f"IMPORTANT: Use ONLY the information above for your answer. "
            f"If the results don't contain the answer, say so honestly — "
            f"do NOT invent facts from your training data."
        )
    except Exception as exc:
        log.exception("search_web failed")
        return f"❌ Web search error: {exc}"
