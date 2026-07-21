from pydantic import BaseModel, EmailStr, field_validator, model_validator
from typing import Optional, List, Any
from datetime import datetime
import re
from .config import (
    PASSWORD_MIN_LENGTH, PASSWORD_REQUIRE_UPPERCASE,
    PASSWORD_REQUIRE_LOWERCASE, PASSWORD_REQUIRE_DIGIT, PASSWORD_REQUIRE_SPECIAL
)


# --- Auth Schemas ---
class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    first_name: str = ""
    last_name: str = ""
    phone: str = ""

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v):
        errors = []
        if len(v) < PASSWORD_MIN_LENGTH:
            errors.append(f"at least {PASSWORD_MIN_LENGTH} characters")
        if PASSWORD_REQUIRE_UPPERCASE and not re.search(r"[A-Z]", v):
            errors.append("one uppercase letter")
        if PASSWORD_REQUIRE_LOWERCASE and not re.search(r"[a-z]", v):
            errors.append("one lowercase letter")
        if PASSWORD_REQUIRE_DIGIT and not re.search(r"\d", v):
            errors.append("one digit")
        if PASSWORD_REQUIRE_SPECIAL and not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            errors.append("one special character")
        if errors:
            raise ValueError(f"Password must contain: {', '.join(errors)}")
        return v

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError("Invalid email format")
        return v.lower()

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError("Username can only contain letters, numbers, and underscores")
        return v


class UserLogin(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: str

    @model_validator(mode="after")
    def require_identity(self):
        if not (self.username or self.email):
            raise ValueError("Username or email is required")
        return self


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class PasswordResetRequest(BaseModel):
    email: str


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v):
        errors = []
        if len(v) < PASSWORD_MIN_LENGTH:
            errors.append(f"at least {PASSWORD_MIN_LENGTH} characters")
        if PASSWORD_REQUIRE_UPPERCASE and not re.search(r"[A-Z]", v):
            errors.append("one uppercase letter")
        if PASSWORD_REQUIRE_LOWERCASE and not re.search(r"[a-z]", v):
            errors.append("one lowercase letter")
        if PASSWORD_REQUIRE_DIGIT and not re.search(r"\d", v):
            errors.append("one digit")
        if PASSWORD_REQUIRE_SPECIAL and not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            errors.append("one special character")
        if errors:
            raise ValueError(f"Password must contain: {', '.join(errors)}")
        return v


class ChangePassword(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v):
        errors = []
        if len(v) < PASSWORD_MIN_LENGTH:
            errors.append(f"at least {PASSWORD_MIN_LENGTH} characters")
        if PASSWORD_REQUIRE_UPPERCASE and not re.search(r"[A-Z]", v):
            errors.append("one uppercase letter")
        if PASSWORD_REQUIRE_LOWERCASE and not re.search(r"[a-z]", v):
            errors.append("one lowercase letter")
        if PASSWORD_REQUIRE_DIGIT and not re.search(r"\d", v):
            errors.append("one digit")
        if PASSWORD_REQUIRE_SPECIAL and not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            errors.append("one special character")
        if errors:
            raise ValueError(f"Password must contain: {', '.join(errors)}")
        return v


# --- User Schemas ---
class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None


class UserSettingsUpdate(BaseModel):
    theme: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    items_per_page: Optional[int] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    phone: str
    role: str
    is_active: bool
    is_verified: bool
    avatar_url: str
    created_at: datetime

    class Config:
        from_attributes = True


# --- Sector Schemas ---
class SectorResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: str
    icon: str
    color: str
    is_active: bool
    item_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# --- Category Schemas ---
class CategoryCreate(BaseModel):
    name: str
    description: str = ""
    sort_order: int = 0


class CategoryResponse(BaseModel):
    id: int
    sector_id: int
    name: str
    description: str
    sort_order: int
    is_active: bool

    class Config:
        from_attributes = True


# --- Item Schemas ---
class ItemCreate(BaseModel):
    name: str
    description: str = ""
    price: float = 0.0
    category_id: Optional[int] = None
    is_available: bool = True
    tags: str = ""


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[int] = None
    is_available: Optional[bool] = None
    tags: Optional[str] = None


class ItemResponse(BaseModel):
    id: int
    sector_id: int
    category_id: Optional[int]
    name: str
    description: str
    price: float
    is_available: bool
    tags: str
    created_at: datetime
    updated_at: Optional[datetime]
    category_name: Optional[str] = None
    sector_name: Optional[str] = None

    class Config:
        from_attributes = True


# --- Order Schemas ---
class OrderItemCreate(BaseModel):
    item_id: int
    quantity: int = 1
    customizations: dict = {}


class OrderCreate(BaseModel):
    sector_id: int
    items: List[OrderItemCreate]
    notes: str = ""
    shipping_address: str = ""
    payment_method: str = "credit_card"


class OrderUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    shipping_address: Optional[str] = None


class OrderItemResponse(BaseModel):
    id: int
    item_id: int
    quantity: int
    unit_price: float
    customizations: dict
    item_name: Optional[str] = None

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    user_id: int
    sector_id: int
    status: str
    total: float
    notes: str
    shipping_address: str
    payment_method: str
    created_at: datetime
    updated_at: Optional[datetime]
    user_name: Optional[str] = None
    sector_name: Optional[str] = None
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True


# --- Pagination ---
class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool


# --- Bulk Operations ---
class BulkDeleteRequest(BaseModel):
    ids: List[int]


class BulkUpdateRequest(BaseModel):
    ids: List[int]
    updates: dict


# --- Role Update ---
class RoleUpdate(BaseModel):
    role: str

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        allowed = ["admin", "manager", "user", "viewer"]
        if v not in allowed:
            raise ValueError(f"Role must be one of: {', '.join(allowed)}")
        return v
