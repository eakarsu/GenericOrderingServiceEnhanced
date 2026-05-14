"""AI router — exposes the standalone Universal Service Bot scripts as
HTTP endpoints under /api/ai/*.

This module is intentionally a *thin wrapper*. It does NOT rewrite or
refactor the LLM logic that lives in the repo-root scripts
(``updated_universal_service_bot.py``, ``orderProcessorEnhanced.py``,
``menuIndexerIntentCalcEnhanced.py``, ``comprehensiveAnalytics.py``,
``crossSectorIntelligence.py``). Those scripts share global state and
heavy deps (chromadb, langchain) and are TOO-RISKY to refactor in a
bootstrap pass — see ``_AUDIT_NOTE.md`` for context.

Behaviour:
  * If ``OPENROUTER_API_KEY`` is not set, every endpoint returns
    HTTP 503 ``{"error": "AI not configured"}``.
  * If the heavy LLM/vector deps (langchain, chromadb, fuzzywuzzy, ...)
    are not installed, the import of the underlying script will fail at
    *first call*. We surface that as HTTP 503 with the missing-dep name
    so an operator sees what to install.
  * The expensive ``UniversalServiceBot`` instance is lazily constructed
    on first use and cached on the module.
"""

from __future__ import annotations

import os
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


router = APIRouter(prefix="/api/ai", tags=["AI"])


# --------------------------------------------------------------------------- #
# Lazy bot wrapper
# --------------------------------------------------------------------------- #

# Repo root = three levels above this file (.../backend/app/routers/ai.py)
_REPO_ROOT = Path(__file__).resolve().parents[3]

_bot_instance: Any = None
_bot_init_error: Optional[str] = None


def _ensure_repo_on_path() -> None:
    """Make the repo root importable so we can ``import updated_universal_service_bot``."""
    repo_str = str(_REPO_ROOT)
    if repo_str not in sys.path:
        sys.path.insert(0, repo_str)


def _api_key_present() -> bool:
    return bool(os.getenv("OPENROUTER_API_KEY"))


def _get_bot() -> Any:
    """Return a cached ``UniversalServiceBot`` instance.

    Raises an HTTPException(503) if construction fails.
    """
    global _bot_instance, _bot_init_error

    if _bot_instance is not None:
        return _bot_instance

    if _bot_init_error is not None:
        raise HTTPException(status_code=503, detail={"error": "AI not configured", "reason": _bot_init_error})

    _ensure_repo_on_path()
    try:
        # Imported lazily to avoid pulling chromadb/langchain at module import.
        from updated_universal_service_bot import UniversalServiceBot  # type: ignore

        sectors_dir = str(_REPO_ROOT / "sectors")
        db_path = str(_REPO_ROOT / "universal_chroma_database")
        _bot_instance = UniversalServiceBot(sectors_directory=sectors_dir, db_path=db_path)
        return _bot_instance
    except ModuleNotFoundError as exc:
        _bot_init_error = f"missing dependency: {exc.name}"
        raise HTTPException(status_code=503, detail={"error": "AI not configured", "reason": _bot_init_error})
    except Exception as exc:  # noqa: BLE001 — surface anything to the client
        _bot_init_error = f"{type(exc).__name__}: {exc}"
        traceback.print_exc()
        raise HTTPException(status_code=503, detail={"error": "AI not configured", "reason": _bot_init_error})


def _require_api_key() -> None:
    if not _api_key_present():
        raise HTTPException(status_code=503, detail={"error": "AI not configured"})


# --------------------------------------------------------------------------- #
# Schemas
# --------------------------------------------------------------------------- #


class ChatRequest(BaseModel):
    message: str
    sector: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    sector: Optional[str] = None


class ConversationRequest(BaseModel):
    messages: List[str]


class ConversationResponse(BaseModel):
    responses: List[str]


class SectorDetectRequest(BaseModel):
    message: str


class SectorDetectResponse(BaseModel):
    sector: str


class OrderRequest(BaseModel):
    query: str
    sector: Optional[str] = None


# --------------------------------------------------------------------------- #
# Endpoints
# --------------------------------------------------------------------------- #


@router.get("/health")
def ai_health() -> Dict[str, Any]:
    """Lightweight health check — does not boot the bot."""
    return {
        "status": "ok",
        "configured": _api_key_present(),
        "bot_loaded": _bot_instance is not None,
        "init_error": _bot_init_error,
    }


@router.get("/sectors")
def list_sectors() -> Dict[str, Any]:
    """List sector directories present on disk.

    Cheap: just reads the filesystem, no bot init required.
    """
    sectors_dir = _REPO_ROOT / "sectors"
    if not sectors_dir.exists():
        return {"sectors": []}
    sectors = sorted(p.name for p in sectors_dir.iterdir() if p.is_dir())
    return {"sectors": sectors}


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    """Single-turn chat. Wraps ``UniversalServiceBot.chatAway2``.

    ``chatAway2`` is the stateless variant — safer for HTTP than
    ``chatAway`` which mutates per-bot ``self.state``.
    """
    _require_api_key()
    bot = _get_bot()
    try:
        text = bot.chatAway2(req.message, detected_sector=req.sector)
    except Exception as exc:  # noqa: BLE001
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"chat failed: {exc}")
    return ChatResponse(response=text, sector=req.sector)


@router.post("/conversation", response_model=ConversationResponse)
def conversation(req: ConversationRequest) -> ConversationResponse:
    """Replay a multi-message conversation. Wraps ``process_conversation``."""
    _require_api_key()
    if not req.messages:
        raise HTTPException(status_code=400, detail="messages must be a non-empty list")
    bot = _get_bot()
    try:
        responses = bot.process_conversation(req.messages)
    except Exception as exc:  # noqa: BLE001
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"conversation failed: {exc}")
    return ConversationResponse(responses=list(responses))


@router.post("/detect-sector", response_model=SectorDetectResponse)
def detect_sector(req: SectorDetectRequest) -> SectorDetectResponse:
    """Detect which sector a message belongs to. Wraps the intent detector."""
    _require_api_key()
    bot = _get_bot()
    try:
        sector = bot.detect_sector_with_ai(req.message, "")
    except Exception as exc:  # noqa: BLE001
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"detect-sector failed: {exc}")
    return SectorDetectResponse(sector=sector)


@router.post("/order")
def process_order(req: OrderRequest) -> Dict[str, Any]:
    """Process an order against a specific sector's catalogue.

    Wraps ``SectorSpecificProcessor.process_order`` via the bot's
    ``get_sector_processor``. If sector is omitted, the bot's intent
    detector chooses one.
    """
    _require_api_key()
    bot = _get_bot()
    try:
        sector = req.sector or bot.detect_sector_with_ai(req.query, "")
        processor = bot.get_sector_processor(sector)
        result = processor.process_order(req.query)
    except ValueError as exc:
        # Unknown sector — surface as 400.
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:  # noqa: BLE001
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"order failed: {exc}")
    return {"sector": sector, "result": result}
