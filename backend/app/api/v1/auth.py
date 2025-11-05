from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token,
    get_current_active_user
)
from app.models.user import User
from app.schemas.user import UserCreate, User as UserSchema, Token

router = APIRouter()


@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new user with role-based restrictions:
    - HR, PM, MANAGER can create BENEFICIARY users
    - Only ADMIN can create users with elevated roles (HR, PM, MANAGER, ADMIN)
    """
    from app.models.user import UserRole
    
    # Define elevated roles that only ADMIN can create
    ELEVATED_ROLES = {UserRole.ADMIN, UserRole.HR, UserRole.PM, UserRole.MANAGER}
    
    # Define roles that can create users
    CREATOR_ROLES = {UserRole.ADMIN, UserRole.HR, UserRole.PM, UserRole.MANAGER}
    
    # Check if current user has permission to create users
    if current_user.role not in CREATOR_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only HR, PM, MANAGER, and ADMIN can create users"
        )
    
    # Check if trying to create elevated role user
    if user_in.role in ELEVATED_ROLES and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only ADMIN can create users with elevated roles (HR, PM, MANAGER, ADMIN)"
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        contract_id=user_in.contract_id,
        department_id=user_in.department_id,
        reports_to_id=user_in.reports_to_id
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login and get JWT tokens."""
    # Find user
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    # Check if password change is required
    if user.force_password_change:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Password change required. Please change your password before logging in."
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token."""
    payload = verify_token(refresh_token, token_type="refresh")
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    access_token = create_access_token(data={"sub": user.id})
    new_refresh_token = create_refresh_token(data={"sub": user.id})
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }
