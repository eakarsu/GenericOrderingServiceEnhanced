"""Expose analytics modules as FastAPI endpoints with caching."""
from __future__ import annotations

import time
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Order, Item, Sector


router = APIRouter(prefix="/api/analytics", tags=["analytics"])

# Simple in-memory TTL cache to spare hot endpoints repeated DB scans.
_CACHE: Dict[str, Dict[str, Any]] = {}
_TTL_SEC = 60


def _cache_get(key: str) -> Optional[Any]:
    rec = _CACHE.get(key)
    if not rec:
        return None
    if time.time() - rec["t"] > _TTL_SEC:
        _CACHE.pop(key, None)
        return None
    return rec["v"]


def _cache_set(key: str, value: Any) -> None:
    _CACHE[key] = {"t": time.time(), "v": value}


@router.get("/overview")
def overview(db: Session = Depends(get_db)):
    """Top-line metrics across the platform."""
    cached = _cache_get("overview")
    if cached:
        return cached
    out = {
        "orders": db.query(Order).count(),
        "items": db.query(Item).count(),
        "sectors": db.query(Sector).count(),
        "generated_at": time.time(),
    }
    _cache_set("overview", out)
    return out


@router.get("/orders-by-sector")
def orders_by_sector(db: Session = Depends(get_db)):
    cached = _cache_get("orders-by-sector")
    if cached:
        return cached
    rows = (
        db.query(Sector.name, Sector.id)
        .all()
    )
    out = []
    for name, sid in rows:
        count = db.query(Order).filter(getattr(Order, "sector_id", None) == sid).count() if hasattr(Order, "sector_id") else 0
        out.append({"sector": name, "orders": count})
    _cache_set("orders-by-sector", out)
    return out


@router.post("/cache/clear")
def clear_cache():
    _CACHE.clear()
    return {"ok": True, "cleared_at": time.time()}


@router.get("/cross-sector")
def cross_sector():
    """Best-effort summary from the cross-sector intelligence module if importable."""
    try:
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).resolve().parents[3]))
        import crossSectorIntelligence  # type: ignore
        summary = getattr(crossSectorIntelligence, "summary", None)
        if callable(summary):
            return summary()
        return {"available": True, "note": "module imported but no `summary()` exported"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"cross-sector module unavailable: {e}")
