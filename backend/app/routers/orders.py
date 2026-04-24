from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
import math

from ..database import get_db
from ..models import Order, OrderItem, Item, Sector, User
from ..schemas import OrderCreate, OrderUpdate, BulkDeleteRequest, BulkUpdateRequest
from ..auth_utils import get_current_user, require_manager_or_admin

router = APIRouter(prefix="/api/orders", tags=["Orders"])


@router.get("/")
def list_orders(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    status: Optional[str] = Query(None),
    sector_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    min_total: Optional[float] = Query(None),
    max_total: Optional[float] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List orders with pagination, search, filter, sort."""
    query = db.query(Order)

    # Non-admin users can only see their own orders
    if current_user.role not in ["admin", "manager"]:
        query = query.filter(Order.user_id == current_user.id)
    elif user_id:
        query = query.filter(Order.user_id == user_id)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Order.notes.ilike(search_term)) |
            (Order.shipping_address.ilike(search_term)) |
            (Order.status.ilike(search_term))
        )

    if status:
        query = query.filter(Order.status == status)
    if sector_id:
        query = query.filter(Order.sector_id == sector_id)
    if min_total is not None:
        query = query.filter(Order.total >= min_total)
    if max_total is not None:
        query = query.filter(Order.total <= max_total)

    sort_column = getattr(Order, sort_by, Order.created_at)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    total = query.count()
    total_pages = math.ceil(total / per_page) if total > 0 else 1
    orders = query.offset((page - 1) * per_page).limit(per_page).all()

    result = []
    for o in orders:
        user = db.query(User).filter(User.id == o.user_id).first()
        sector = db.query(Sector).filter(Sector.id == o.sector_id).first()
        items = db.query(OrderItem).filter(OrderItem.order_id == o.id).all()
        result.append({
            "id": o.id, "user_id": o.user_id, "sector_id": o.sector_id,
            "status": o.status, "total": o.total, "notes": o.notes,
            "shipping_address": o.shipping_address, "payment_method": o.payment_method,
            "user_name": f"{user.first_name} {user.last_name}" if user else "",
            "sector_name": sector.name if sector else "",
            "item_count": len(items),
            "created_at": o.created_at.isoformat(),
            "updated_at": o.updated_at.isoformat() if o.updated_at else None
        })

    return {
        "items": result,
        "total": total, "page": page, "per_page": per_page,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }


@router.get("/{order_id}")
def get_order(order_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get order detail with items."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if current_user.role not in ["admin", "manager"] and order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    user = db.query(User).filter(User.id == order.user_id).first()
    sector = db.query(Sector).filter(Sector.id == order.sector_id).first()
    order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()

    items_detail = []
    for oi in order_items:
        item = db.query(Item).filter(Item.id == oi.item_id).first()
        items_detail.append({
            "id": oi.id, "item_id": oi.item_id,
            "item_name": item.name if item else "Deleted Item",
            "quantity": oi.quantity, "unit_price": oi.unit_price,
            "subtotal": oi.quantity * oi.unit_price,
            "customizations": oi.customizations or {}
        })

    return {
        "id": order.id, "user_id": order.user_id, "sector_id": order.sector_id,
        "status": order.status, "total": order.total, "notes": order.notes,
        "shipping_address": order.shipping_address, "payment_method": order.payment_method,
        "user_name": f"{user.first_name} {user.last_name}" if user else "",
        "sector_name": sector.name if sector else "",
        "items": items_detail,
        "created_at": order.created_at.isoformat(),
        "updated_at": order.updated_at.isoformat() if order.updated_at else None
    }


@router.post("/")
def create_order(data: OrderCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new order."""
    sector = db.query(Sector).filter(Sector.id == data.sector_id).first()
    if not sector:
        raise HTTPException(status_code=404, detail="Sector not found")

    order = Order(
        user_id=current_user.id, sector_id=data.sector_id,
        notes=data.notes, shipping_address=data.shipping_address,
        payment_method=data.payment_method
    )
    db.add(order)
    db.flush()

    total = 0.0
    for item_data in data.items:
        item = db.query(Item).filter(Item.id == item_data.item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail=f"Item {item_data.item_id} not found")
        oi = OrderItem(
            order_id=order.id, item_id=item.id,
            quantity=item_data.quantity, unit_price=item.price,
            customizations=item_data.customizations
        )
        total += item.price * item_data.quantity
        db.add(oi)

    order.total = round(total, 2)
    db.commit()
    db.refresh(order)
    return {"id": order.id, "total": order.total, "message": "Order created"}


@router.put("/{order_id}")
def update_order(order_id: int, data: OrderUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update order."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if current_user.role not in ["admin", "manager"] and order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    if data.status is not None:
        order.status = data.status
    if data.notes is not None:
        order.notes = data.notes
    if data.shipping_address is not None:
        order.shipping_address = data.shipping_address
    db.commit()
    return {"message": "Order updated"}


@router.delete("/{order_id}")
def delete_order(order_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete order."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if current_user.role not in ["admin", "manager"] and order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    db.query(OrderItem).filter(OrderItem.order_id == order.id).delete()
    db.delete(order)
    db.commit()
    return {"message": "Order deleted"}


@router.post("/bulk-delete")
def bulk_delete_orders(data: BulkDeleteRequest, current_user: User = Depends(require_manager_or_admin), db: Session = Depends(get_db)):
    """Bulk delete orders."""
    for oid in data.ids:
        db.query(OrderItem).filter(OrderItem.order_id == oid).delete(synchronize_session=False)
    deleted = db.query(Order).filter(Order.id.in_(data.ids)).delete(synchronize_session=False)
    db.commit()
    return {"message": f"{deleted} orders deleted"}


@router.post("/bulk-update")
def bulk_update_orders(data: BulkUpdateRequest, current_user: User = Depends(require_manager_or_admin), db: Session = Depends(get_db)):
    """Bulk update orders."""
    allowed_fields = {"status"}
    updates = {k: v for k, v in data.updates.items() if k in allowed_fields}
    if not updates:
        raise HTTPException(status_code=400, detail="No valid fields to update")
    updated = db.query(Order).filter(Order.id.in_(data.ids)).update(updates, synchronize_session=False)
    db.commit()
    return {"message": f"{updated} orders updated"}
