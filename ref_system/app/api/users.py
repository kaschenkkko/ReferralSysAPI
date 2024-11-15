from datetime import datetime
from typing import List, Optional

from app.core.security import (create_access_token, get_current_user,
                               verify_password)
from app.db.crud import create_referral_code, create_user, get_user_by_email
from app.db.models import ReferralCode, User, UserReferral
from app.db.session import get_db
from app.schemas.user import (CreateReferralCodeSchema, CreateTokenSchema,
                              CreateUserSchema, DeactivationResponseSchema,
                              ReferralCodeSchema, ResponseTokenSchema,
                              SearchCodeResponseSchema, UserInfoSchema)
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import false

user_router = APIRouter()


@user_router.post('/api/v1/users/create', response_model=UserInfoSchema, status_code=201,
                  summary='Регистрация пользователя', tags=['Регистрация и аутентификация пользователя'])
async def register_user(user: CreateUserSchema, db: AsyncSession = Depends(get_db)) -> User:
    """"""
    user_data = user.model_dump()
    return await create_user(db=db, **user_data)


@user_router.post('/api/v1/users/token', response_model=ResponseTokenSchema,
                  summary='Получение токена для пользователя',
                  tags=['Регистрация и аутентификация пользователя'])
async def login_for_user_access_token(
    login_request: CreateTokenSchema,
    db: AsyncSession = Depends(get_db)
) -> ResponseTokenSchema:
    """"""
    user: Optional[User] = await get_user_by_email(db, login_request.email)

    if user is None or not verify_password(login_request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid email or password.',
        )
    access_token: str = create_access_token({'sub': user.email})
    return ResponseTokenSchema(access_token=access_token, token_type='Bearer')


@user_router.post('/api/v1/users/new_referral_code', response_model=ReferralCodeSchema, status_code=200,
                  summary='Создать новый реферальный код', tags=['Создать или удалить реферальный код'])
async def change_referral_code(
    expiration_date: CreateReferralCodeSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ReferralCode:
    """Создаёт новый реферальный код для пользователя, если активный код отсутствует."""
    if not expiration_date.days or expiration_date.days <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid input data.'
        )
    if any(code.is_active() for code in current_user.referral_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='The user already has an active referral code.'
        )

    return await create_referral_code(db, current_user.id, expiration_date.days)


@user_router.post('/api/v1/users/deactivate_referral_code', status_code=200,
                  summary='Деактивировать активный реферальный код',
                  tags=['Создать или удалить реферальный код'])
async def deactivate_referral_code(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> DeactivationResponseSchema:
    """Деактивирует активный реферальный код пользователя, если такой код существует."""
    active_code = next(
        (code for code in current_user.referral_code if code.is_active()), None
    )

    if not active_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='No active referral code found.'
        )

    await db.execute(
        update(ReferralCode)
        .where(ReferralCode.id == active_code.id)
        .values(
            expiration_date=datetime.now(),
            is_archived=True
        )
    )
    await db.commit()

    return DeactivationResponseSchema()


@user_router.post('/api/v1/users/search_referral_code', response_model=Optional[ReferralCodeSchema],
                  status_code=200, summary='Получение реферального кода по email адресу реферера',
                  tags=['Получение реферального кода по email'])
async def get_referral_code_by_email(
    input_data: SearchCodeResponseSchema,
    db: AsyncSession = Depends(get_db)
) -> Optional[ReferralCode]:
    user_obj = await get_user_by_email(db, input_data.email)

    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User not found.'
        )
    result = await db.execute(
        select(ReferralCode)
        .where(ReferralCode.user_id == user_obj.id, ReferralCode.is_archived == false())
        .limit(1)
    )
    return result.scalar_one_or_none()


@user_router.post('/api/v1/users/search_referred/{referrer_id}',
                  response_model=List[UserInfoSchema], status_code=200,
                  summary='Получает всех пользователей, которых пригласил пользователь с данным referrer_id.',
                  tags=['Получение информации о рефералах по id'])
async def get_referred_users(
    db: AsyncSession = Depends(get_db),
    referrer_id: int = Path(..., description='ID реферера')
):
    result = await db.execute(
        select(User)
        .join(UserReferral, User.id == UserReferral.referred_id)
        .where(UserReferral.referrer_id == referrer_id)
    )
    referred_users = result.scalars().all()
    return referred_users
