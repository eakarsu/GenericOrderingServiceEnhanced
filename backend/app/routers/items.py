from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
import math

from ..database import get_db
from ..models import Item, Sector, Category, User
from ..schemas import ItemCreate, ItemUpdate, BulkDeleteRequest, BulkUpdateRequest
from ..auth_utils import get_current_user, require_manager_or_admin

router = APIRouter(prefix="/api/items", tags=["Items"])


@router.get("/")
def list_items(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    sort_by: str = Query("name"),
    sort_order: str = Query("asc"),
    sector_id: Optional[int] = Query(None),
    category_id: Optional[int] = Query(None),
    is_available: Optional[bool] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    tags: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List items with pagination, search, filter, sort."""
    query = db.query(Item)

    # Search
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Item.name.ilike(search_term)) |
            (Item.description.ilike(search_term)) |
            (Item.tags.ilike(search_term))
        )

    # Filters
    if sector_id:
        query = query.filter(Item.sector_id == sector_id)
    if category_id:
        query = query.filter(Item.category_id == category_id)
    if is_available is not None:
        query = query.filter(Item.is_available == is_available)
    if min_price is not None:
        query = query.filter(Item.price >= min_price)
    if max_price is not None:
        query = query.filter(Item.price <= max_price)
    if tags:
        query = query.filter(Item.tags.ilike(f"%{tags}%"))

    # Sort
    sort_column = getattr(Item, sort_by, Item.name)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    total = query.count()
    total_pages = math.ceil(total / per_page) if total > 0 else 1
    items = query.offset((page - 1) * per_page).limit(per_page).all()

    result_items = []
    for item in items:
        sector = db.query(Sector).filter(Sector.id == item.sector_id).first()
        category = db.query(Category).filter(Category.id == item.category_id).first() if item.category_id else None
        result_items.append({
            "id": item.id, "name": item.name, "description": item.description,
            "price": item.price, "is_available": item.is_available,
            "tags": item.tags, "sector_id": item.sector_id,
            "category_id": item.category_id,
            "sector_name": sector.name if sector else "",
            "category_name": category.name if category else "",
            "created_at": item.created_at.isoformat(),
            "updated_at": item.updated_at.isoformat() if item.updated_at else None
        })

    return {
        "items": result_items,
        "total": total, "page": page, "per_page": per_page,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }


@router.get("/{item_id}")
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get item detail."""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    sector = db.query(Sector).filter(Sector.id == item.sector_id).first()
    category = db.query(Category).filter(Category.id == item.category_id).first() if item.category_id else None

    return {
        "id": item.id, "name": item.name, "description": item.description,
        "price": item.price, "is_available": item.is_available,
        "tags": item.tags, "sector_id": item.sector_id,
        "category_id": item.category_id,
        "sector_name": sector.name if sector else "",
        "category_name": category.name if category else "",
        "metadata": item.metadata_json or {},
        "created_at": item.created_at.isoformat(),
        "updated_at": item.updated_at.isoformat() if item.updated_at else None
    }


@router.post("/sector/{sector_id}")
def create_item(sector_id: int, data: ItemCreate, current_user: User = Depends(require_manager_or_admin), db: Session = Depends(get_db)):
    """Create item in a sector."""
    sector = db.query(Sector).filter(Sector.id == sector_id).first()
    if not sector:
        raise HTTPException(status_code=404, detail="Sector not found")

    item = Item(
        sector_id=sector_id, name=data.name, description=data.description,
        price=data.price, category_id=data.category_id,
        is_available=data.is_available, tags=data.tags
    )
    db.add(item)
    sector.item_count = db.query(Item).filter(Item.sector_id == sector_id).count() + 1
    db.commit()
    db.refresh(item)
    return {"id": item.id, "name": item.name, "message": "Item created"}


@router.put("/{item_id}")
def update_item(item_id: int, data: ItemUpdate, current_user: User = Depends(require_manager_or_admin), db: Session = Depends(get_db)):
    """Update item."""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if data.name is not None:
        item.name = data.name
    if data.description is not None:
        item.description = data.description
    if data.price is not None:
        item.price = data.price
    if data.category_id is not None:
        item.category_id = data.category_id
    if data.is_available is not None:
        item.is_available = data.is_available
    if data.tags is not None:
        item.tags = data.tags
    db.commit()
    db.refresh(item)
    return {"message": "Item updated", "id": item.id}


@router.delete("/{item_id}")
def delete_item(item_id: int, current_user: User = Depends(require_manager_or_admin), db: Session = Depends(get_db)):
    """Delete item."""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    sector_id = item.sector_id
    db.delete(item)
    sector = db.query(Sector).filter(Sector.id == sector_id).first()
    if sector:
        sector.item_count = db.query(Item).filter(Item.sector_id == sector_id).count() - 1
    db.commit()
    return {"message": "Item deleted"}


@router.post("/bulk-delete")
def bulk_delete_items(data: BulkDeleteRequest, current_user: User = Depends(require_manager_or_admin), db: Session = Depends(get_db)):
    """Bulk delete items."""
    deleted = db.query(Item).filter(Item.id.in_(data.ids)).delete(synchronize_session=False)
    db.commit()
    return {"message": f"{deleted} items deleted"}


@router.post("/bulk-update")
def bulk_update_items(data: BulkUpdateRequest, current_user: User = Depends(require_manager_or_admin), db: Session = Depends(get_db)):
    """Bulk update items."""
    allowed_fields = {"is_available", "price", "tags"}
    updates = {k: v for k, v in data.updates.items() if k in allowed_fields}
    if not updates:
        raise HTTPException(status_code=400, detail="No valid fields to update")
    updated = db.query(Item).filter(Item.id.in_(data.ids)).update(updates, synchronize_session=False)
    db.commit()
    return {"message": f"{updated} items updated"}
