"""Real-time order tracking (SSE) for kitchen + customer."""
from __future__ import annotations

import asyncio
import json
import time
from collections import defaultdict
from typing import Any, AsyncGenerator, Dict, List

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel


router = APIRouter(prefix="/api/realtime", tags=["realtime"])

# room_id -> list[asyncio.Queue]
_subscribers: Dict[str, List[asyncio.Queue]] = defaultdict(list)


class Event(BaseModel):
    room: str
    type: str
    payload: Dict[str, Any] = {}


async def _broadcast(room: str, event: Dict[str, Any]) -> None:
    for q in list(_subscribers.get(room, [])):
        try:
            q.put_nowait(event)
        except Exception:
            pass


@router.post("/publish")
async def publish(evt: Event):
    """Push an event to all subscribers in a room (kitchen:KDS-1, order:<id>, etc.)."""
    payload = {"type": evt.type, "at": time.time(), **evt.payload}
    await _broadcast(evt.room, payload)
    return {"ok": True, "subscribers": len(_subscribers.get(evt.room, []))}


@router.get("/subscribe/{room}")
async def subscribe(room: str, request: Request):
    """SSE stream of events for a room."""
    queue: asyncio.Queue = asyncio.Queue()
    _subscribers[room].append(queue)

    async def gen() -> AsyncGenerator[bytes, None]:
        yield b": connected\n\n"
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    evt = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield f"data: {json.dumps(evt)}\n\n".encode()
                except asyncio.TimeoutError:
                    yield b": ping\n\n"
        finally:
            try:
                _subscribers[room].remove(queue)
            except ValueError:
                pass

    return StreamingResponse(gen(), media_type="text/event-stream")


@router.get("/rooms")
async def rooms():
    return {"rooms": [{"room": r, "subscribers": len(qs)} for r, qs in _subscribers.items()]}
