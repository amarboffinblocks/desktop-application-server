from fastapi import APIRouter, HTTPException, status, Depends
from app.features.auth.schemas import (
    UserCreate,
    UserLogin,
    UserOut,
)
from app.features.auth.controller import AuthController
from app.core.security import create_access_token, create_refresh_token
from app.common.dependencies import authenticated_user
from jose import JWTError
from app.core.security import decode_access_token
from typing import Optional

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register(user: UserCreate):
    """Register a new user with unique email, name, and password."""
    user_obj = await AuthController.register(user)
    return {
        "id": str(user_obj.id),
        "email": user_obj.email,
        "name": user_obj.name,
        "role": user_obj.role,
        "created_at": user_obj.created_at,
    }

@router.post("/login")
async def login(user: UserLogin):
    """Authenticate user and return tokens for Electron Store."""
    return await AuthController.login(user)

@router.post("/refresh")
async def refresh_token_endpoint(refresh_token: str):
    """Issue a new access token using a valid refresh token from body, unless blacklisted."""
    try:
        payload = decode_access_token(refresh_token)
        if payload is None or "sub" not in payload or "jti" not in payload:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        if await AuthController.is_refresh_token_blacklisted(payload["jti"]):
            raise HTTPException(status_code=401, detail="Refresh token revoked. Please login again.")
        access_token = create_access_token({"sub": payload["sub"], "id": payload.get("id")})
        return {"access_token": access_token, "token_type": "bearer"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@router.get("/me", response_model=UserOut)
async def get_me(current_user=Depends(authenticated_user)):
    """Get current logged-in user's info."""
    return UserOut(
        id=str(current_user.id),
        email=current_user.email,
        name=current_user.name,
        role=current_user.role,
        created_at=current_user.created_at,
        is_verified=current_user.is_verified,
    )

@router.post("/logout")
async def logout(refresh_token: str):
    """Logout user by blacklisting refresh token. Token is sent in body."""
    return await AuthController.logout(refresh_token)
