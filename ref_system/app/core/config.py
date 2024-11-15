from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    JWT_SECRET_KEY: str

    @property
    def database_url_asyncpg(self):
        """URL для асинхронного подключения к БД PostgreSQL."""
        # postgresql+asyncpg://postgres:password@localhost:5432/postgres
        return (
            f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}'
            f'@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
        )

    class Config:
        env_file = '.env'


settings = Settings()
