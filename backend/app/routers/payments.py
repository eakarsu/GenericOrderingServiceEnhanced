"""Payment + refund flows (Stripe) and reconciliation reports.

TODO: configure credentials — STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET.
"""
from __future__ import annotations

import os
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel


router = APIRouter(prefix="/api/payments", tags=["payments"])

try:
    import stripe  # type: ignore
    if os.environ.get("STRIPE_SECRET_KEY"):
        stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
        _stripe_ready = True
    else:
        _stripe_ready = False
except Exception:
    stripe = None  # type: ignore
    _stripe_ready = False


class IntentReq(BaseModel):
    amount: int  # cents
    currency: str = "usd"
    order_id: Optional[str] = None
    customer_email: Optional[str] = None


class RefundReq(BaseModel):
    payment_intent_id: str
    amount: Optional[int] = None  # partial refund if set
    reason: Optional[str] = None


def _require_stripe() -> None:
    if not _stripe_ready:
        raise HTTPException(status_code=503, detail="Stripe not configured")


@router.post("/intent")
async def create_intent(req: IntentReq):
    _require_stripe()
    intent = stripe.PaymentIntent.create(
        amount=req.amount,
        currency=req.currency,
        receipt_email=req.customer_email,
        metadata={"order_id": req.order_id or ""},
    )
    return {"id": intent["id"], "client_secret": intent["client_secret"]}


@router.post("/refund")
async def refund(req: RefundReq):
    _require_stripe()
    kwargs: Dict[str, Any] = {"payment_intent": req.payment_intent_id}
    if req.amount is not None:
        kwargs["amount"] = req.amount
    if req.reason:
        kwargs["reason"] = req.reason
    r = stripe.Refund.create(**kwargs)
    return {"id": r["id"], "status": r["status"], "amount": r["amount"]}


@router.post("/webhook")
async def webhook(req: Request):
    """Verify Stripe webhook signatures and log events."""
    secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
    if not secret or not _stripe_ready:
        raise HTTPException(status_code=503, detail="Stripe webhook not configured")
    sig = req.headers.get("stripe-signature", "")
    payload = await req.body()
    try:
        event = stripe.Webhook.construct_event(payload, sig, secret)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"signature verification failed: {e}")
    return {"received": True, "type": event["type"], "id": event["id"]}


@router.get("/reconciliation")
async def reconciliation(limit: int = 50):
    _require_stripe()
    charges = stripe.Charge.list(limit=min(100, limit))
    out = []
    for c in charges.auto_paging_iter():
        out.append({"id": c["id"], "amount": c["amount"], "refunded": c["amount_refunded"], "status": c["status"]})
        if len(out) >= limit:
            break
    return {"charges": out, "count": len(out)}
