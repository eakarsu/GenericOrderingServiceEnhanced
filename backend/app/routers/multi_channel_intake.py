"""Multi-channel order intake (voice, WhatsApp, web) with a unified ledger.

TODO: configure credentials for Twilio (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
and WhatsApp Business (WHATSAPP_VERIFY_TOKEN).
"""
from __future__ import annotations

import os
import time
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel


router = APIRouter(prefix="/api/multi-channel", tags=["multi-channel"])

# Unified ledger entry — replace with DB model when migration is OK.
_LEDGER: List[Dict[str, Any]] = []


class IntakeEvent(BaseModel):
    channel: str  # "voice" | "whatsapp" | "web" | "sms"
    customer_ref: str
    text: Optional[str] = None
    payload: Dict[str, Any] = {}


@router.post("/intake")
async def intake(evt: IntakeEvent):
    entry = {
        "id": f"ic_{int(time.time()*1000)}",
        "channel": evt.channel,
        "customer_ref": evt.customer_ref,
        "text": evt.text,
        "payload": evt.payload,
        "received_at": time.time(),
        "status": "received",
    }
    _LEDGER.append(entry)
    return entry


@router.get("/ledger")
async def ledger(channel: Optional[str] = None, limit: int = 50):
    rows = _LEDGER
    if channel:
        rows = [r for r in rows if r["channel"] == channel]
    return {"count": len(rows), "items": rows[-limit:]}


@router.post("/twilio/sms")
async def twilio_inbound(req: Request):
    """Twilio webhook for inbound SMS. Returns TwiML to acknowledge."""
    form = await req.form()
    body = form.get("Body", "")
    from_ = form.get("From", "")
    _LEDGER.append({
        "id": f"sms_{int(time.time()*1000)}",
        "channel": "sms",
        "customer_ref": from_,
        "text": body,
        "received_at": time.time(),
        "status": "received",
    })
    twiml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response><Message>Order received! We'll confirm shortly.</Message></Response>"
    return {"content": twiml}


@router.get("/whatsapp/verify")
async def whatsapp_verify(req: Request):
    """Meta verify-token handshake."""
    challenge = req.query_params.get("hub.challenge")
    verify_token = req.query_params.get("hub.verify_token")
    expected = os.environ.get("WHATSAPP_VERIFY_TOKEN")
    if expected and verify_token == expected and challenge:
        return int(challenge)
    raise HTTPException(status_code=403, detail="verify failed")


@router.post("/whatsapp/webhook")
async def whatsapp_webhook(payload: Dict[str, Any]):
    """Receive WhatsApp Business Cloud API events."""
    entries = payload.get("entry", [])
    captured = 0
    for ent in entries:
        for change in ent.get("changes", []):
            for msg in change.get("value", {}).get("messages", []):
                _LEDGER.append({
                    "id": f"wa_{msg.get('id', int(time.time()*1000))}",
                    "channel": "whatsapp",
                    "customer_ref": msg.get("from", ""),
                    "text": msg.get("text", {}).get("body", ""),
                    "received_at": time.time(),
                    "status": "received",
                })
                captured += 1
    return {"received": captured}
