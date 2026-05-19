"""
Add this endpoint to backend/chat.py (or a new memory.py router).

Just paste the function below at the bottom of backend/chat.py,
right under the existing @router.post("/chat") handler.
"""

# ============================================================
# Add to backend/chat.py (at the bottom)
# ============================================================

from memory.memory_manager import clear_memory


@router.post("/memory/clear")
async def memory_clear(chat_id: Optional[str] = Form(None)):
    """
    Clear backend memory.

    - With chat_id: deletes memory for that chat only
    - Without chat_id: deletes ALL memory rows (use carefully)
    """
    try:
        count = clear_memory(chat_id=chat_id)
        return {
            "success": True,
            "deleted": count,
            "scope": chat_id or "all",
        }
    except Exception as exc:
        log.exception("Memory clear failed")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(exc)},
        )
