from fastapi import HTTPException
from app.features.auth.models import UserModel
from app.core.security import hash_password, verify_password
from app.db.mongo import get_user_collection
from app.features.auth.schemas import UserCreate, UserLogin
from typing import Optional
from datetime import datetime
from app.db.mongo import get_blacklist_collection, get_access_blacklist_collection
from jose import JWTError
from app.core.security import decode_access_token

class AuthController:
    @staticmethod
    async def register(user: UserCreate):
        user_col = await get_user_collection()
        if await AuthController.get_user_by_email(user.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        if len(user.password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters long.")
        hashed = hash_password(user.password)
        user_obj = UserModel(
            email=user.email,
            name=user.name,
            hashed_password=hashed,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_synced=False,
        )
        result = await user_col.insert_one(user_obj.dict(by_alias=True, exclude={"id"}))
        user_obj.id = result.inserted_id
        return user_obj

    @staticmethod
    async def login(user: UserLogin):
        db_user = await AuthController.authenticate_user(user.email, user.password)
        if not db_user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        from app.core.security import create_access_token, create_refresh_token
        access_token = create_access_token({"sub": db_user.email, "id": str(db_user.id)})
        refresh_token = create_refresh_token({"sub": db_user.email, "id": str(db_user.id)})
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[UserModel]:
        user_col = await get_user_collection()
        user_data = await user_col.find_one({"email": email})
        if user_data:
            return UserModel(**user_data)
        return None

    @staticmethod
    async def get_user_by_name(name: str) -> Optional[UserModel]:
        user_col = await get_user_collection()
        user_data = await user_col.find_one({"name": name})
        if user_data:
            return UserModel(**user_data)
        return None

    @staticmethod
    async def authenticate_user(email: str, password: str) -> Optional[UserModel]:
        user = await AuthController.get_user_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    async def logout(refresh_token: str):
        try:
            payload = decode_access_token(refresh_token)
            if payload is None or "jti" not in payload:
                raise HTTPException(status_code=401, detail="Invalid refresh token")
            jti = payload["jti"]
            blacklist_col = get_blacklist_collection()
            already_blacklisted = await blacklist_col.find_one({"jti": jti})
            if already_blacklisted:
                return {"message": "User already logged out."}
            await blacklist_col.insert_one({"jti": jti})
            return {"message": "Logged out successfully. Token revoked."}
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

    @staticmethod
    async def is_refresh_token_blacklisted(jti: str) -> bool:
        blacklist_col = get_blacklist_collection()
        return await blacklist_col.find_one({"jti": jti}) is not None

    @staticmethod
    async def is_access_token_blacklisted(jti: str) -> bool:
        access_blacklist_col = get_access_blacklist_collection()
        return await access_blacklist_col.find_one({"jti": jti}) is not None
