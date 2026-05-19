"""Custom Views router — 4 endpoints:
- VIZ: order-volume-timeline, status-heatmap
- NON-VIZ: order-confirmation-pdf, ordering-rules (CRUD)
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import io
import threading

from ..database import get_db
from ..models import Order, OrderItem, Item, User, Sector
from ..auth_utils import get_current_user

router = APIRouter(prefix="/api/custom-views", tags=["Custom Views"])

# Canonical pipeline stages
PIPELINE = ["pending", "confirmed", "processing", "shipped", "completed", "cancelled"]

# ---- In-memory ordering rules store (CRUD target) ----
_RULES_LOCK = threading.Lock()
_RULES_STORE: Dict[int, Dict[str, Any]] = {}
_RULES_NEXT_ID = {"v": 1}


def _seed_default_rules():
    if _RULES_STORE:
        return
    defaults = [
        {"name": "Min Order Amount", "field": "total", "operator": ">=", "value": "10", "action": "allow", "enabled": True},
        {"name": "Max Items Per Order", "field": "item_count", "operator": "<=", "value": "50", "action": "warn", "enabled": True},
        {"name": "Block Cancelled Resubmit", "field": "status", "operator": "!=", "value": "cancelled", "action": "block", "enabled": True},
    ]
    for d in defaults:
        rid = _RULES_NEXT_ID["v"]
        _RULES_NEXT_ID["v"] += 1
        d.update({"id": rid, "created_at": datetime.utcnow().isoformat()})
        _RULES_STORE[rid] = d


_seed_default_rules()


# =========================================================
# VIZ #1: Order Volume Timeline (by day, last N days)
# =========================================================
@router.get("/order-volume-timeline")
def order_volume_timeline(
    days: int = Query(14, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Daily order counts + revenue over the last N days."""
    end = datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=0)
    start = (end - timedelta(days=days - 1)).replace(hour=0, minute=0, second=0, microsecond=0)

    q = db.query(Order).filter(Order.created_at >= start, Order.created_at <= end)
    if current_user.role not in ("admin", "manager"):
        q = q.filter(Order.user_id == current_user.id)
    rows = q.all()

    # Initialize all buckets so the timeline is continuous.
    buckets: Dict[str, Dict[str, Any]] = {}
    for i in range(days):
        d = (start + timedelta(days=i)).strftime("%Y-%m-%d")
        buckets[d] = {"date": d, "count": 0, "revenue": 0.0}

    for o in rows:
        key = o.created_at.strftime("%Y-%m-%d")
        if key in buckets:
            buckets[key]["count"] += 1
            buckets[key]["revenue"] += float(o.total or 0.0)

    series = list(buckets.values())
    total_orders = sum(b["count"] for b in series)
    total_revenue = round(sum(b["revenue"] for b in series), 2)
    peak = max(series, key=lambda b: b["count"]) if series else None
    avg = round(total_orders / max(1, days), 2)

    return {
        "days": days,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "series": series,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "avg_orders_per_day": avg,
        "peak_day": peak,
    }


# =========================================================
# VIZ #2: Status Heatmap (status x time-of-day buckets)
# =========================================================
@router.get("/status-heatmap")
def status_heatmap(
    days: int = Query(14, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Heatmap: rows = status, cols = 6 time-of-day buckets, cells = order counts."""
    since = datetime.utcnow() - timedelta(days=days)
    q = db.query(Order).filter(Order.created_at >= since)
    if current_user.role not in ("admin", "manager"):
        q = q.filter(Order.user_id == current_user.id)
    rows = q.all()

    # 6 time-of-day buckets (4h each)
    buckets = [
        ("00-04", 0, 4),
        ("04-08", 4, 8),
        ("08-12", 8, 12),
        ("12-16", 12, 16),
        ("16-20", 16, 20),
        ("20-24", 20, 24),
    ]
    bucket_labels = [b[0] for b in buckets]

    # Use canonical statuses + collect any unknown ones.
    statuses_seen = set()
    for o in rows:
        statuses_seen.add((o.status or "unknown").lower())
    statuses = [s for s in PIPELINE if s in statuses_seen] + sorted(s for s in statuses_seen if s not in PIPELINE)
    if not statuses:
        statuses = PIPELINE[:3]

    cells = {s: {b: 0 for b in bucket_labels} for s in statuses}
    for o in rows:
        s = (o.status or "unknown").lower()
        if s not in cells:
            continue
        h = o.created_at.hour
        for label, lo, hi in buckets:
            if lo <= h < hi:
                cells[s][label] += 1
                break

    max_count = 0
    matrix = []
    for s in statuses:
        row = []
        for label in bucket_labels:
            v = cells[s][label]
            if v > max_count:
                max_count = v
            row.append(v)
        matrix.append({"status": s, "counts": row})

    return {
        "days": days,
        "buckets": bucket_labels,
        "statuses": statuses,
        "matrix": matrix,
        "max_count": max_count,
        "total": sum(sum(r["counts"]) for r in matrix),
    }


# =========================================================
# NON-VIZ #1: Order Confirmation PDF
# =========================================================
@router.get("/order-confirmation-pdf")
def order_confirmation_pdf(
    order_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a downloadable order-confirmation PDF for a given order."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if current_user.role not in ("admin", "manager") and order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this order")

    items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    user = db.query(User).filter(User.id == order.user_id).first()
    sector = db.query(Sector).filter(Sector.id == order.sector_id).first()

    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import LETTER
    except ImportError:
        raise HTTPException(status_code=500, detail="reportlab not installed")

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=LETTER)
    width, height = LETTER
    y = height - 50

    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, y, "ORDER CONFIRMATION")
    y -= 28
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, y, f"Confirmation generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    y -= 24

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, f"Confirmation #: CONF-{order.id:06d}")
    y -= 18
    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Order ID: {order.id}")
    y -= 16
    c.drawString(50, y, f"Status: {order.status.upper()}")
    y -= 16
    c.drawString(50, y, f"Placed: {order.created_at.strftime('%Y-%m-%d %H:%M')}")
    y -= 16
    if user:
        name = user.first_name or user.username
        c.drawString(50, y, f"Customer: {name} <{user.email}>")
        y -= 16
    if sector:
        c.drawString(50, y, f"Sector: {sector.name}")
        y -= 16
    if order.shipping_address:
        c.drawString(50, y, f"Ship to: {order.shipping_address[:80]}")
        y -= 16
    if order.payment_method:
        c.drawString(50, y, f"Payment: {order.payment_method}")
        y -= 16

    y -= 10
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Item")
    c.drawString(330, y, "Qty")
    c.drawString(390, y, "Unit Price")
    c.drawString(480, y, "Subtotal")
    y -= 6
    c.line(50, y, 560, y)
    y -= 16
    c.setFont("Helvetica", 10)

    subtotal = 0.0
    for oi in items:
        item = db.query(Item).filter(Item.id == oi.item_id).first()
        name = (item.name if item else f"Item #{oi.item_id}")[:40]
        line = oi.quantity * oi.unit_price
        subtotal += line
        c.drawString(50, y, name)
        c.drawString(330, y, str(oi.quantity))
        c.drawString(390, y, f"${oi.unit_price:.2f}")
        c.drawString(480, y, f"${line:.2f}")
        y -= 14
        if y < 140:
            c.showPage()
            y = height - 50

    if subtotal == 0.0:
        subtotal = float(order.total or 0.0)
    tax = round(subtotal * 0.0875, 2)
    total = round(subtotal + tax, 2)

    y -= 10
    c.line(50, y, 560, y)
    y -= 18
    c.setFont("Helvetica", 11)
    c.drawString(390, y, "Subtotal:")
    c.drawString(480, y, f"${subtotal:.2f}")
    y -= 16
    c.drawString(390, y, "Tax (8.75%):")
    c.drawString(480, y, f"${tax:.2f}")
    y -= 16
    c.setFont("Helvetica-Bold", 12)
    c.drawString(390, y, "TOTAL:")
    c.drawString(480, y, f"${total:.2f}")
    y -= 30

    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Confirmation Code: CONF-{order.id:06d}-{order.created_at.strftime('%y%m%d')}")
    y -= 14
    c.drawString(50, y, "This document confirms receipt of your order. Thank you!")

    c.showPage()
    c.save()
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="confirmation_order_{order.id}.pdf"'},
    )


# =========================================================
# NON-VIZ #2: Ordering Rules Editor (CRUD)
# =========================================================
class RuleBase(BaseModel):
    name: str
    field: str
    operator: str
    value: str
    action: str = "allow"  # allow | warn | block
    enabled: bool = True


class RuleUpdate(BaseModel):
    name: Optional[str] = None
    field: Optional[str] = None
    operator: Optional[str] = None
    value: Optional[str] = None
    action: Optional[str] = None
    enabled: Optional[bool] = None


ALLOWED_OPERATORS = {">", ">=", "<", "<=", "==", "!=", "in", "contains"}
ALLOWED_ACTIONS = {"allow", "warn", "block"}


def _validate_rule_payload(name=None, operator=None, action=None):
    if operator is not None and operator not in ALLOWED_OPERATORS:
        raise HTTPException(status_code=400, detail=f"Invalid operator. Allowed: {sorted(ALLOWED_OPERATORS)}")
    if action is not None and action not in ALLOWED_ACTIONS:
        raise HTTPException(status_code=400, detail=f"Invalid action. Allowed: {sorted(ALLOWED_ACTIONS)}")
    if name is not None and (not isinstance(name, str) or not name.strip()):
        raise HTTPException(status_code=400, detail="Name is required")


@router.get("/ordering-rules")
def list_rules(current_user: User = Depends(get_current_user)):
    with _RULES_LOCK:
        return {"rules": list(_RULES_STORE.values()), "count": len(_RULES_STORE)}


@router.post("/ordering-rules")
def create_rule(payload: RuleBase, current_user: User = Depends(get_current_user)):
    if current_user.role not in ("admin", "manager"):
        raise HTTPException(status_code=403, detail="Manager or admin role required")
    _validate_rule_payload(payload.name, payload.operator, payload.action)
    with _RULES_LOCK:
        rid = _RULES_NEXT_ID["v"]
        _RULES_NEXT_ID["v"] += 1
        rule = payload.dict()
        rule.update({"id": rid, "created_at": datetime.utcnow().isoformat()})
        _RULES_STORE[rid] = rule
        return rule


@router.put("/ordering-rules/{rule_id}")
def update_rule(rule_id: int, payload: RuleUpdate, current_user: User = Depends(get_current_user)):
    if current_user.role not in ("admin", "manager"):
        raise HTTPException(status_code=403, detail="Manager or admin role required")
    _validate_rule_payload(payload.name, payload.operator, payload.action)
    with _RULES_LOCK:
        if rule_id not in _RULES_STORE:
            raise HTTPException(status_code=404, detail="Rule not found")
        rule = _RULES_STORE[rule_id]
        for k, v in payload.dict(exclude_unset=True).items():
            rule[k] = v
        rule["updated_at"] = datetime.utcnow().isoformat()
        _RULES_STORE[rule_id] = rule
        return rule


@router.delete("/ordering-rules/{rule_id}")
def delete_rule(rule_id: int, current_user: User = Depends(get_current_user)):
    if current_user.role not in ("admin", "manager"):
        raise HTTPException(status_code=403, detail="Manager or admin role required")
    with _RULES_LOCK:
        if rule_id not in _RULES_STORE:
            raise HTTPException(status_code=404, detail="Rule not found")
        removed = _RULES_STORE.pop(rule_id)
        return {"deleted": True, "rule": removed}
