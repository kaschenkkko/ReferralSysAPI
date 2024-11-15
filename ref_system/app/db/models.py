from datetime import datetime

from app.db.session import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    referral_code = relationship(
        'ReferralCode', back_populates='user',
        cascade='all, delete-orphan', lazy='selectin'
    )

    def __str__(self):
        return self.email


class UserReferral(Base):
    __tablename__ = 'user_referrals'

    id = Column(Integer, primary_key=True, index=True)
    referrer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    referred_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    referrer = relationship('User', foreign_keys=[referrer_id], backref='referred_users', lazy='selectin')
    referred = relationship('User', foreign_keys=[referred_id], backref='referrer_user', lazy='selectin')


class ReferralCode(Base):
    __tablename__ = 'referral_codes'

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    expiration_date = Column(DateTime, nullable=False)
    is_archived = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    user = relationship('User', back_populates='referral_code', lazy='selectin')

    def __str__(self):
        return self.code

    def is_active(self):
        return not self.is_archived and self.expiration_date > datetime.now()
