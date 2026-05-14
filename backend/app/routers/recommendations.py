"""Recommendation engine using cross-sector keyword/co-occurrence signals."""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Item, Order


router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


class ForUserReq(BaseModel):
    user_id: int
    sector_id: int | None = None
    limit: int = 5


def _co_occurrence(db: Session) -> Dict[int, Counter]:
    pairs: Dict[int, Counter] = defaultdict(Counter)
    orders = db.query(Order).all()
    for o in orders:
        items_ids = []
        if hasattr(o, "items") and isinstance(o.items, list):
            items_ids = [getattr(it, "id", None) for it in o.items if getattr(it, "id", None)]
        elif hasattr(o, "item_id") and getattr(o, "item_id", None):
            items_ids = [o.item_id]
        for a in items_ids:
            for b in items_ids:
                if a != b:
                    pairs[a][b] += 1
    return pairs


@router.post("/for-user")
def for_user(req: ForUserReq, db: Session = Depends(get_db)):
    user_orders = db.query(Order).filter(getattr(Order, "user_id", None) == req.user_id).all() \
        if hasattr(Order, "user_id") else []
    user_item_ids: List[int] = []
    for o in user_orders:
        if hasattr(o, "items") and isinstance(o.items, list):
            user_item_ids.extend([getattr(it, "id", None) for it in o.items if getattr(it, "id", None)])
        elif getattr(o, "item_id", None):
            user_item_ids.append(o.item_id)

    co = _co_occurrence(db)
    scores: Counter = Counter()
    for iid in user_item_ids:
        scores.update(co.get(iid, {}))
    for iid in user_item_ids:
        scores.pop(iid, None)

    top_ids = [iid for iid, _ in scores.most_common(req.limit)]
    items = db.query(Item).filter(Item.id.in_(top_ids)).all() if top_ids else []
    items_by_id = {it.id: it for it in items}
    ranked = []
    for iid, sc in scores.most_common(req.limit):
        it = items_by_id.get(iid)
        if it:
            ranked.append({"item_id": iid, "name": it.name, "score": sc})
    return {"user_id": req.user_id, "recommendations": ranked, "based_on_orders": len(user_orders)}


@router.get("/popular")
def popular(limit: int = 10, db: Session = Depends(get_db)):
    item_counts: Counter = Counter()
    for o in db.query(Order).limit(2000).all():
        if hasattr(o, "items") and isinstance(o.items, list):
            for it in o.items:
                if getattr(it, "id", None):
                    item_counts[it.id] += 1
        elif getattr(o, "item_id", None):
            item_counts[o.item_id] += 1
    top = item_counts.most_common(limit)
    items = db.query(Item).filter(Item.id.in_([i for i, _ in top])).all() if top else []
    items_by_id = {it.id: it for it in items}
    return {"popular": [{"item_id": i, "name": items_by_id.get(i).name if items_by_id.get(i) else None, "count": c} for i, c in top]}
