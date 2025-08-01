from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from app.core.security import decode_access_token
from app.features.auth.controller import AuthController

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def authenticated_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated. Please login to access this resource.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None or "sub" not in payload or "jti" not in payload:
        raise credentials_exception
    # Check if access token is blacklisted
    if await AuthController.is_access_token_blacklisted(payload["jti"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token revoked. Please login again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await AuthController.get_user_by_email(payload["sub"])
    if user is None or not user.is_verified:
        raise credentials_exception
    return user


