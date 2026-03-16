from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import User
from app.repositories import UserRepository, RefreshTokenRepository
from app.utils.security import hash_password, verify_password

# === Настройки JWT ===
import os
SECRET_KEY = os.getenv("SECRET_KEY", "mfti-python-final-secret-key-change-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_SECONDS = 604800  # 7 дней

# === Инициализация ===
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
router = APIRouter(tags=["auth"])


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
) -> User:
    """
    Извлекает текущего пользователя из JWT-токена.
    Используется как зависимость в защищённых эндпоинтах.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await UserRepository.get_by_username(session, username)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, session: AsyncSession = Depends(get_session)):
    if await UserRepository.get_by_username(session, user.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    db_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        password_hash=hash_password(user.password)
    )
    session.add(db_user)
    await session.commit()
    return {"message": "User registered"}

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    user = await UserRepository.get_by_username(session, form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token_obj = await RefreshTokenRepository.create(
        session, user.uuid, expires_in=REFRESH_TOKEN_EXPIRE_SECONDS
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token_obj.token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    token: str,
    session: AsyncSession = Depends(get_session)
):
    rt = await RefreshTokenRepository.get_valid(session, token)
    if not rt:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user = await UserRepository.get_by_id(session, rt.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    await RefreshTokenRepository.delete_by_token(session, token)

    new_access = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    new_refresh = await RefreshTokenRepository.create(
        session, user.uuid, expires_in=REFRESH_TOKEN_EXPIRE_SECONDS
    )

    return {
        "access_token": new_access,
        "refresh_token": new_refresh.token,
        "token_type": "bearer"
    }
@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    if len(request.new_password) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters")
    if not verify_password(request.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid old password")

    current_user.password_hash = hash_password(request.new_password)
    session.add(current_user)
    await session.commit()
    return {"message": "Password updated"}