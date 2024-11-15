import uuid
from datetime import datetime, timedelta
from typing import Optional

from app.core.security import get_password_hash
from app.db.models import ReferralCode, User, UserReferral
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

REFERRAL_CODE_EXPIRATION_DAYS = 30
MAX_CODE_GENERATION_ATTEMPTS = 5


async def create_referral_code(
        db: AsyncSession,
        user_id: int,
        days: int = REFERRAL_CODE_EXPIRATION_DAYS
) -> ReferralCode:
    """Создание реферального кода."""
    for _ in range(MAX_CODE_GENERATION_ATTEMPTS):
        code = str(uuid.uuid4())[:8]
        expiration_date = datetime.now() + timedelta(days=days)

        new_referral_code = ReferralCode(
            code=code,
            expiration_date=expiration_date,
            user_id=user_id,
            is_archived=False,
        )

        try:
            db.add(new_referral_code)
            await db.commit()
            await db.refresh(new_referral_code)
            return new_referral_code
        except IntegrityError:
            await db.rollback()
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail='Failed to create a unique referral code.'
    )


async def link_referrer_to_referred_user(
        db: AsyncSession,
        referral_code_obj: ReferralCode,
        referred_id: int
) -> None:
    """Создаём связь между пригласившим и приглашённым пользователями."""
    referrer = referral_code_obj.user

    new_user_referral = UserReferral(
        referrer_id=referrer.id,
        referred_id=referred_id,
    )

    db.add(new_user_referral)
    await db.commit()
    await db.refresh(new_user_referral)


async def create_user(
        db: AsyncSession,
        email: str,
        referral_code: Optional[str],
        password: str,
) -> User:
    """Создаём нового пользователя."""
    if referral_code:
        referral_code_obj = await db.execute(select(ReferralCode).filter(ReferralCode.code == referral_code))
        referral_code_obj: ReferralCode = referral_code_obj.scalar_one_or_none()

        if not referral_code_obj or not referral_code_obj.is_active():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid referral code.'
            )

    new_user = User(
        email=email,
        hashed_password=get_password_hash(password),
    )

    try:
        db.add(new_user)
        await db.commit()

        await create_referral_code(db, new_user.id)
        if referral_code:
            await link_referrer_to_referred_user(db, referral_code_obj, new_user.id)

        await db.refresh(new_user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='A user with this email is already registered.'
        )

    return new_user


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Получаем пользователя из базы данных, по полю «email»."""
    user = await db.execute(select(User).filter(User.email == email))
    return user.scalars().one_or_none()
