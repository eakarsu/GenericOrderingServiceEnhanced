"""Tenant onboarding wizard with seed data per sector."""
from __future__ import annotations

import time
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Item, Sector


router = APIRouter(prefix="/api/tenant-onboarding", tags=["tenant-onboarding"])


_SECTOR_SEEDS: Dict[str, List[Dict[str, Any]]] = {
    "restaurant": [
        {"name": "Cheeseburger", "price": 9.5, "description": "Classic burger"},
        {"name": "Caesar Salad", "price": 8.0, "description": "Romaine, parmesan, dressing"},
        {"name": "Soda", "price": 2.5, "description": "12oz can"},
    ],
    "retail": [
        {"name": "T-Shirt", "price": 19.99, "description": "Cotton tee"},
        {"name": "Mug", "price": 12.0, "description": "Ceramic mug"},
    ],
    "services": [
        {"name": "Consultation 30min", "price": 75.0, "description": "Discovery call"},
        {"name": "Implementation hour", "price": 150.0, "description": "Hands-on work"},
    ],
}


class OnboardReq(BaseModel):
    tenant_name: str
    sector: str
    contact_email: str
    seed_data: bool = True


class CompleteReq(BaseModel):
    tenant_id: str
    step: str


@router.get("/sectors")
def list_sectors():
    return {"sectors": list(_SECTOR_SEEDS.keys())}


@router.post("/begin")
def begin(req: OnboardReq, db: Session = Depends(get_db)):
    tenant_id = f"t_{int(time.time()*1000)}"
    sector_obj = db.query(Sector).filter(Sector.name == req.sector).first()
    if not sector_obj:
        try:
            sector_obj = Sector(name=req.sector)
            db.add(sector_obj)
            db.commit()
            db.refresh(sector_obj)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"sector create failed: {e}")

    seeded = 0
    if req.seed_data:
        seeds = _SECTOR_SEEDS.get(req.sector, [])
        for s in seeds:
            try:
                db.add(Item(name=s["name"], price=s["price"], description=s["description"], sector_id=sector_obj.id))
                seeded += 1
            except Exception:
                pass
        try:
            db.commit()
        except Exception:
            db.rollback()

    return {
        "tenant_id": tenant_id,
        "name": req.tenant_name,
        "sector": req.sector,
        "seeded": seeded,
        "next_steps": ["customize-menu", "add-team", "configure-payments", "go-live"],
    }


@router.post("/complete-step")
def complete_step(req: CompleteReq):
    return {"tenant_id": req.tenant_id, "step": req.step, "completed_at": time.time()}
