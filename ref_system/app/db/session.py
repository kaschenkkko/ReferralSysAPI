from app.core.config import settings
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    create_async_engine)
from sqlalchemy.orm import declarative_base, sessionmaker

# Создаем общую базу для всех моделей
Base = declarative_base()

# Создаем движок SQLAlchemy
async_engine: AsyncEngine = create_async_engine(url=settings.database_url_asyncpg)

# Создаем фабрику сессий
async_session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


# Зависимость для получения сессии
async def get_db():
    async with async_session() as session:
        yield session
