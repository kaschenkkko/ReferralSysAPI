from datetime import datetime, timedelta, timezone
from typing import Dict

from app.core.config import settings
from app.db.models import User
from app.db.session import get_db
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 240

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


def get_password_hash(password: str) -> str:
    """Создаём хэш пароля."""
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password: str) -> bool:
    """Проверяем соответствие введённого пароля и хэшированного пароля пользователя."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: Dict[str, str]) -> str:
    """Создаём JWT-токен."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )


async def get_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    """Получаем текущего пользователя из токена."""
    payload = verify_token(token)
    user_email = payload.get('sub')
    user = await db.execute(select(User).filter(User.email == user_email))
    user = user.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User not found',
        )
    return user
