from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
import csv
import io

from ..database import get_db
from ..models import Item, Order, OrderItem, User, Sector
from ..auth_utils import get_current_user, require_manager_or_admin

router = APIRouter(prefix="/api/export", tags=["Export"])


@router.get("/items/csv")
def export_items_csv(
    sector_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """CSV export for items."""
    query = db.query(Item)
    if sector_id:
        query = query.filter(Item.sector_id == sector_id)
    if search:
        query = query.filter(Item.name.ilike(f"%{search}%"))

    items = query.all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Name", "Description", "Price", "Available", "Sector", "Category", "Tags", "Created"])

    for item in items:
        sector = db.query(Sector).filter(Sector.id == item.sector_id).first()
        writer.writerow([
            item.id, item.name, item.description, f"${item.price:.2f}",
            "Yes" if item.is_available else "No",
            sector.name if sector else "", "",
            item.tags, item.created_at.strftime("%Y-%m-%d %H:%M")
        ])

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=items_export.csv"}
    )


@router.get("/orders/csv")
def export_orders_csv(
    status: Optional[str] = Query(None),
    sector_id: Optional[int] = Query(None),
    current_user: User = Depends(require_manager_or_admin),
    db: Session = Depends(get_db)
):
    """CSV export for orders."""
    query = db.query(Order)
    if status:
        query = query.filter(Order.status == status)
    if sector_id:
        query = query.filter(Order.sector_id == sector_id)

    orders = query.order_by(Order.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "User", "Sector", "Status", "Total", "Items", "Notes", "Address", "Payment", "Created"])

    for order in orders:
        user = db.query(User).filter(User.id == order.user_id).first()
        sector = db.query(Sector).filter(Sector.id == order.sector_id).first()
        item_count = db.query(OrderItem).filter(OrderItem.order_id == order.id).count()
        writer.writerow([
            order.id,
            f"{user.first_name} {user.last_name}" if user else "",
            sector.name if sector else "",
            order.status, f"${order.total:.2f}", item_count,
            order.notes, order.shipping_address, order.payment_method,
            order.created_at.strftime("%Y-%m-%d %H:%M")
        ])

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=orders_export.csv"}
    )


@router.get("/users/csv")
def export_users_csv(current_user: User = Depends(require_manager_or_admin), db: Session = Depends(get_db)):
    """CSV export for users."""
    users = db.query(User).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Username", "Email", "Name", "Phone", "Role", "Active", "Verified", "Created"])

    for u in users:
        writer.writerow([
            u.id, u.username, u.email,
            f"{u.first_name} {u.last_name}", u.phone,
            u.role, "Yes" if u.is_active else "No",
            "Yes" if u.is_verified else "No",
            u.created_at.strftime("%Y-%m-%d %H:%M")
        ])

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=users_export.csv"}
    )


@router.get("/items/pdf")
def export_items_pdf(
    sector_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """PDF export for items (generates simple HTML-based PDF)."""
    query = db.query(Item)
    if sector_id:
        query = query.filter(Item.sector_id == sector_id)
    items = query.all()

    html = """<html><head><style>
    body { font-family: Arial; margin: 20px; }
    h1 { color: #1e40af; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    th { background: #1e40af; color: white; padding: 10px; text-align: left; }
    td { padding: 8px; border-bottom: 1px solid #ddd; }
    tr:nth-child(even) { background: #f8fafc; }
    .footer { margin-top: 20px; color: #666; font-size: 12px; }
    </style></head><body>
    <h1>Items Report</h1>
    <table><tr><th>ID</th><th>Name</th><th>Price</th><th>Available</th><th>Tags</th></tr>"""

    for item in items:
        html += f"<tr><td>{item.id}</td><td>{item.name}</td><td>${item.price:.2f}</td>"
        html += f"<td>{'Yes' if item.is_available else 'No'}</td><td>{item.tags}</td></tr>"

    html += f"</table><p class='footer'>Total items: {len(items)} | Generated for: {current_user.username}</p></body></html>"

    return StreamingResponse(
        io.BytesIO(html.encode()),
        media_type="text/html",
        headers={"Content-Disposition": "attachment; filename=items_report.html"}
    )


@router.get("/orders/pdf")
def export_orders_pdf(
    status: Optional[str] = Query(None),
    current_user: User = Depends(require_manager_or_admin),
    db: Session = Depends(get_db)
):
    """PDF export for orders (generates simple HTML-based PDF)."""
    query = db.query(Order)
    if status:
        query = query.filter(Order.status == status)
    orders = query.order_by(Order.created_at.desc()).all()

    html = """<html><head><style>
    body { font-family: Arial; margin: 20px; }
    h1 { color: #1e40af; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    th { background: #1e40af; color: white; padding: 10px; text-align: left; }
    td { padding: 8px; border-bottom: 1px solid #ddd; }
    tr:nth-child(even) { background: #f8fafc; }
    </style></head><body>
    <h1>Orders Report</h1>
    <table><tr><th>ID</th><th>User</th><th>Sector</th><th>Status</th><th>Total</th><th>Date</th></tr>"""

    for o in orders:
        user = db.query(User).filter(User.id == o.user_id).first()
        sector = db.query(Sector).filter(Sector.id == o.sector_id).first()
        html += f"<tr><td>{o.id}</td><td>{user.first_name if user else ''} {user.last_name if user else ''}</td>"
        html += f"<td>{sector.name if sector else ''}</td><td>{o.status}</td><td>${o.total:.2f}</td>"
        html += f"<td>{o.created_at.strftime('%Y-%m-%d')}</td></tr>"

    html += f"</table><p>Total orders: {len(orders)}</p></body></html>"

    return StreamingResponse(
        io.BytesIO(html.encode()),
        media_type="text/html",
        headers={"Content-Disposition": "attachment; filename=orders_report.html"}
    )
