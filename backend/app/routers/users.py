from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..models import User, UserSettings
from ..schemas import UserUpdate, UserSettingsUpdate, UserResponse, RoleUpdate, BulkDeleteRequest, BulkUpdateRequest
from ..auth_utils import get_current_user, require_admin, require_manager_or_admin
import math

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/")
def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    role: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(require_manager_or_admin),
    db: Session = Depends(get_db)
):
    """List users with pagination, search, filter, sort."""
    query = db.query(User)

    # Search
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (User.username.ilike(search_term)) |
            (User.email.ilike(search_term)) |
            (User.first_name.ilike(search_term)) |
            (User.last_name.ilike(search_term))
        )

    # Filter
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    # Sort
    sort_column = getattr(User, sort_by, User.created_at)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    total = query.count()
    total_pages = math.ceil(total / per_page) if total > 0 else 1
    users = query.offset((page - 1) * per_page).limit(per_page).all()

    return {
        "items": [
            {
                "id": u.id, "username": u.username, "email": u.email,
                "first_name": u.first_name, "last_name": u.last_name,
                "phone": u.phone, "role": u.role, "is_active": u.is_active,
                "is_verified": u.is_verified, "created_at": u.created_at.isoformat()
            } for u in users
        ],
        "total": total, "page": page, "per_page": per_page,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }


@router.get("/{user_id}")
def get_user(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user detail."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Users can see their own profile, managers/admins can see anyone
    if current_user.id != user_id and current_user.role not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Access denied")
    return {
        "id": user.id, "username": user.username, "email": user.email,
        "first_name": user.first_name, "last_name": user.last_name,
        "phone": user.phone, "role": user.role, "is_active": user.is_active,
        "is_verified": user.is_verified, "avatar_url": user.avatar_url,
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat() if user.updated_at else None
    }


@router.put("/profile")
def update_profile(data: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update user profile/settings."""
    if data.first_name is not None:
        current_user.first_name = data.first_name
    if data.last_name is not None:
        current_user.last_name = data.last_name
    if data.phone is not None:
        current_user.phone = data.phone
    if data.avatar_url is not None:
        current_user.avatar_url = data.avatar_url
    db.commit()
    db.refresh(current_user)
    return {"message": "Profile updated", "user": {
        "id": current_user.id, "username": current_user.username,
        "first_name": current_user.first_name, "last_name": current_user.last_name,
        "phone": current_user.phone, "avatar_url": current_user.avatar_url
    }}


@router.put("/settings")
def update_settings(data: UserSettingsUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update user settings page."""
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)

    if data.theme is not None:
        settings.theme = data.theme
    if data.notifications_enabled is not None:
        settings.notifications_enabled = data.notifications_enabled
    if data.language is not None:
        settings.language = data.language
    if data.timezone is not None:
        settings.timezone = data.timezone
    if data.items_per_page is not None:
        settings.items_per_page = data.items_per_page
    db.commit()
    return {"message": "Settings updated"}


@router.get("/settings/me")
def get_settings(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user settings."""
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not settings:
        return {"theme": "light", "notifications_enabled": True, "language": "en", "timezone": "UTC", "items_per_page": 10}
    return {
        "theme": settings.theme, "notifications_enabled": settings.notifications_enabled,
        "language": settings.language, "timezone": settings.timezone, "items_per_page": settings.items_per_page
    }


@router.put("/{user_id}/role")
def update_user_role(user_id: int, data: RoleUpdate, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    """RBAC - Update user role (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = data.role
    db.commit()
    return {"message": f"User role updated to {data.role}"}


@router.delete("/{user_id}")
def delete_user(user_id: int, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    """Delete user (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}


@router.post("/bulk-delete")
def bulk_delete_users(data: BulkDeleteRequest, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    """Bulk delete users."""
    if current_user.id in data.ids:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    deleted = db.query(User).filter(User.id.in_(data.ids)).delete(synchronize_session=False)
    db.commit()
    return {"message": f"{deleted} users deleted"}


@router.post("/bulk-update")
def bulk_update_users(data: BulkUpdateRequest, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    """Bulk update users."""
    allowed_fields = {"role", "is_active"}
    updates = {k: v for k, v in data.updates.items() if k in allowed_fields}
    if not updates:
        raise HTTPException(status_code=400, detail="No valid fields to update")
    updated = db.query(User).filter(User.id.in_(data.ids)).update(updates, synchronize_session=False)
    db.commit()
    return {"message": f"{updated} users updated"}
