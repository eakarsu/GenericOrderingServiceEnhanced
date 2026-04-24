from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from ..database import get_db
from ..models import User, UserSettings, PasswordResetToken, EmailVerificationToken
from ..schemas import (
    UserRegister, UserLogin, TokenResponse,
    PasswordResetRequest, PasswordResetConfirm, ChangePassword, UserResponse
)
from ..auth_utils import (
    hash_password, verify_password, create_access_token, get_current_user
)
from ..config import RESET_TOKEN_EXPIRE_MINUTES, VERIFICATION_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    """User registration endpoint with password strength validation."""
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
        phone=data.phone,
        role="user",
        is_verified=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create default settings
    settings = UserSettings(user_id=user.id)
    db.add(settings)

    # Create email verification token
    token = str(uuid.uuid4())
    verification = EmailVerificationToken(
        user_id=user.id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(minutes=VERIFICATION_TOKEN_EXPIRE_MINUTES)
    )
    db.add(verification)
    db.commit()

    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    return TokenResponse(
        access_token=access_token,
        user={
            "id": user.id, "username": user.username, "email": user.email,
            "role": user.role, "first_name": user.first_name, "last_name": user.last_name,
            "is_verified": user.is_verified
        }
    )


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    """Login endpoint."""
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    return TokenResponse(
        access_token=access_token,
        user={
            "id": user.id, "username": user.username, "email": user.email,
            "role": user.role, "first_name": user.first_name, "last_name": user.last_name,
            "is_verified": user.is_verified
        }
    )


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """Logout endpoint - invalidates token on client side."""
    return {"message": "Successfully logged out", "username": current_user.username}


@router.post("/password-reset/request")
def request_password_reset(data: PasswordResetRequest, db: Session = Depends(get_db)):
    """Request password reset - sends token."""
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        # Return success even if email not found (security best practice)
        return {"message": "If that email exists, a reset link has been sent"}

    # Invalidate old tokens
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.used == False
    ).update({"used": True})

    token = str(uuid.uuid4())
    reset_token = PasswordResetToken(
        user_id=user.id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    )
    db.add(reset_token)
    db.commit()

    return {"message": "If that email exists, a reset link has been sent", "token": token}


@router.post("/password-reset/confirm")
def confirm_password_reset(data: PasswordResetConfirm, db: Session = Depends(get_db)):
    """Confirm password reset with token and new password."""
    reset = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == data.token,
        PasswordResetToken.used == False,
        PasswordResetToken.expires_at > datetime.utcnow()
    ).first()
    if not reset:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user = db.query(User).filter(User.id == reset.user_id).first()
    user.password_hash = hash_password(data.new_password)
    reset.used = True
    db.commit()

    return {"message": "Password reset successfully"}


@router.post("/change-password")
def change_password(data: ChangePassword, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Change password for authenticated user."""
    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    current_user.password_hash = hash_password(data.new_password)
    db.commit()
    return {"message": "Password changed successfully"}


@router.post("/verify-email/{token}")
def verify_email(token: str, db: Session = Depends(get_db)):
    """Email verification endpoint."""
    verification = db.query(EmailVerificationToken).filter(
        EmailVerificationToken.token == token,
        EmailVerificationToken.used == False,
        EmailVerificationToken.expires_at > datetime.utcnow()
    ).first()
    if not verification:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")

    user = db.query(User).filter(User.id == verification.user_id).first()
    user.is_verified = True
    verification.used = True
    db.commit()

    return {"message": "Email verified successfully"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return current_user
