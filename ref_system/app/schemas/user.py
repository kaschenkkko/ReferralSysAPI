from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class CreateTokenSchema(BaseModel):
    """Pydantic-схема для создания токена."""
    email: str = Field(description='Электронная почта')
    password: str = Field(description='Пароль пользователя')


class ResponseTokenSchema(BaseModel):
    """Pydantic-схема для показа токена."""
    access_token: str = Field(description='Токен')
    token_type: str = Field(description='Тип токена')


class CreateUserSchema(BaseModel):
    """Pydantic-схема для регистрации пользователя."""
    email: str = Field(description='Электронная почта')
    referral_code: Optional[str] = Field(None, description='Код реферала')
    password: str = Field(description='Пароль пользователя')


class CreateReferralCodeSchema(BaseModel):
    """Pydantic-схема для создания реферального кода."""
    days: int = Field(..., ge=1, description='Срок годности реферального кода')


class ReferralCodeSchema(BaseModel):
    """Pydantic-схема для показа реферального кода."""
    code: str = Field(description='Реферальный код')
    expiration_date: datetime = Field(description='Дата истечения срока действия кода')
    is_archived: bool = Field(False, description='Проверка, архивирован ли код')

    class Config:
        from_attributes = True


class UserInfoSchema(BaseModel):
    """Pydantic-схема для вывода информации о пользователе."""
    id: int = Field(description='ID пользователя в БД')
    email: str = Field(description='Электронная почта')
    referral_code: List[ReferralCodeSchema] = Field(description='Информация о реферальном коде')

    class Config:
        from_attributes = True


class DeactivationResponseSchema(BaseModel):
    """Pydantic-схема для вывода статуса о деактивации реферального кода."""
    detail: str = 'The referral code has been successfully deactivated.'


class SearchCodeResponseSchema(BaseModel):
    """Pydantic-схема для поиска реферального кода по email."""
    email: str = Field(description='Электронная почта')
