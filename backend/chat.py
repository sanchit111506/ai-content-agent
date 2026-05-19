"""
FastAPI chat router with chat_id support for per-chat memory.
"""

import os
import json
import shutil
import logging
from typing import List, Optional

from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse

from agents.orchestrator import generate_content

log = logging.getLogger(__name__)
router = APIRouter()

UPLOAD_FOLDER = "uploads"
VALID_MODES = {"Auto", "Moderate", "DeepSearch"}
MAX_UPLOAD_SIZE_MB = 25

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def _normalize_mode(mode: str) -> str:
    mode = (mode or "").strip()
    return mode if mode in VALID_MODES else "Auto"


def _save_uploads(files: List[UploadFile]) -> List[str]:
    saved: list[str] = []
    for file in files or []:
        if not file or not file.filename:
            continue
        try:
            dest = os.path.join(UPLOAD_FOLDER, file.filename)
            with open(dest, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            size_mb = os.path.getsize(dest) / (1024 * 1024)
            if size_mb > MAX_UPLOAD_SIZE_MB:
                os.remove(dest)
                log.warning("Rejected %s — %.1f MB exceeds %d MB limit",
                            file.filename, size_mb, MAX_UPLOAD_SIZE_MB)
                continue
            saved.append(dest)
        except Exception as exc:
            log.warning("Upload failed for %s: %s", file.filename, exc)
    return saved


def _cleanup_uploads(paths: List[str]) -> None:
    for p in paths:
        try:
            if os.path.exists(p):
                os.remove(p)
        except Exception as exc:
            log.debug("Cleanup failed for %s: %s", p, exc)


def _parse_history(raw: Optional[str]) -> list[dict]:
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return [
                {"role": m.get("role", "user"), "content": m.get("content", "")}
                for m in parsed
                if isinstance(m, dict) and m.get("content")
            ]
    except Exception as exc:
        log.warning("Could not parse chat_history: %s", exc)
    return []


@router.post("/chat")
async def chat(
    message: str = Form(""),
    mode: str = Form("Auto"),
    chat_history: Optional[str] = Form(None),
    chat_id: Optional[str] = Form(None),
    files: List[UploadFile] = File([]),
):
    mode = _normalize_mode(mode)
    uploaded_paths = _save_uploads(files)
    history = _parse_history(chat_history)

    log.info("=" * 50)
    log.info("📩 MESSAGE: %s", message[:120] + ("…" if len(message) > 120 else ""))
    log.info("🔥 MODE   : %s", mode)
    log.info("🆔 CHAT   : %s", chat_id or "default")
    log.info("📎 FILES  : %s", uploaded_paths or "none")
    log.info("🗨️  HISTORY: %d messages", len(history))
    log.info("=" * 50)

    try:
        result = await generate_content(
            prompt=message,
            mode=mode,
            uploaded_files=uploaded_paths,
            chat_history=history,
            chat_id=chat_id,
        )
        return {
            "success": True,
            "response": str(result),
            "mode": mode,
            "files_uploaded": [os.path.basename(p) for p in uploaded_paths],
        }

    except Exception as exc:
        log.exception("Chat orchestration failed")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "response": f"⚠️ Backend Error: {exc}",
                "mode": mode,
            },
        )

    finally:
        _cleanup_uploads(uploaded_paths)
