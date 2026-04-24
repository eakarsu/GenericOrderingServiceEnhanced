from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
import math

from ..database import get_db
from ..models import Sector, Category, Item, User
from ..schemas import CategoryCreate, CategoryResponse
from ..auth_utils import get_current_user, require_admin

router = APIRouter(prefix="/api/sectors", tags=["Sectors"])


@router.get("/")
def list_sectors(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    sort_by: str = Query("name"),
    sort_order: str = Query("asc"),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """List all sectors with pagination, search, filter, sort."""
    query = db.query(Sector)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Sector.name.ilike(search_term)) |
            (Sector.description.ilike(search_term))
        )

    if is_active is not None:
        query = query.filter(Sector.is_active == is_active)

    sort_column = getattr(Sector, sort_by, Sector.name)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    total = query.count()
    total_pages = math.ceil(total / per_page) if total > 0 else 1
    sectors = query.offset((page - 1) * per_page).limit(per_page).all()

    return {
        "items": [
            {
                "id": s.id, "name": s.name, "slug": s.slug,
                "description": s.description, "icon": s.icon,
                "color": s.color, "is_active": s.is_active,
                "item_count": s.item_count, "created_at": s.created_at.isoformat()
            } for s in sectors
        ],
        "total": total, "page": page, "per_page": per_page,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }


@router.get("/{sector_id}")
def get_sector(sector_id: int, db: Session = Depends(get_db)):
    """Get sector detail with categories."""
    sector = db.query(Sector).filter(Sector.id == sector_id).first()
    if not sector:
        raise HTTPException(status_code=404, detail="Sector not found")

    categories = db.query(Category).filter(Category.sector_id == sector_id).order_by(Category.sort_order).all()

    return {
        "id": sector.id, "name": sector.name, "slug": sector.slug,
        "description": sector.description, "icon": sector.icon,
        "color": sector.color, "is_active": sector.is_active,
        "item_count": sector.item_count, "created_at": sector.created_at.isoformat(),
        "categories": [
            {"id": c.id, "name": c.name, "description": c.description, "sort_order": c.sort_order}
            for c in categories
        ]
    }


@router.get("/slug/{slug}")
def get_sector_by_slug(slug: str, db: Session = Depends(get_db)):
    """Get sector by slug."""
    sector = db.query(Sector).filter(Sector.slug == slug).first()
    if not sector:
        raise HTTPException(status_code=404, detail="Sector not found")

    categories = db.query(Category).filter(Category.sector_id == sector.id).order_by(Category.sort_order).all()

    return {
        "id": sector.id, "name": sector.name, "slug": sector.slug,
        "description": sector.description, "icon": sector.icon,
        "color": sector.color, "is_active": sector.is_active,
        "item_count": sector.item_count, "created_at": sector.created_at.isoformat(),
        "categories": [
            {"id": c.id, "name": c.name, "description": c.description, "sort_order": c.sort_order}
            for c in categories
        ]
    }


@router.post("/{sector_id}/categories")
def create_category(sector_id: int, data: CategoryCreate, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    """Create category in a sector."""
    sector = db.query(Sector).filter(Sector.id == sector_id).first()
    if not sector:
        raise HTTPException(status_code=404, detail="Sector not found")

    cat = Category(sector_id=sector_id, name=data.name, description=data.description, sort_order=data.sort_order)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return {"id": cat.id, "name": cat.name, "message": "Category created"}


@router.get("/{sector_id}/categories")
def list_categories(sector_id: int, db: Session = Depends(get_db)):
    """List categories for a sector."""
    categories = db.query(Category).filter(Category.sector_id == sector_id).order_by(Category.sort_order).all()
    return [
        {"id": c.id, "name": c.name, "description": c.description, "sort_order": c.sort_order, "is_active": c.is_active}
        for c in categories
    ]
