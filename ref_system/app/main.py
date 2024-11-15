from app.admin.admin_panel import setup_admin
from app.api.users import user_router
from app.db.session import async_engine
from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

app = FastAPI(title='Referral System API', description='Простой RESTful API сервис для реферальной системы.')

# Роутеры
app.include_router(user_router)

# Админ-панель
setup_admin(app, async_engine)

# Ограничение количества запросов (в минуту)
limits = ['30/minute']
limiter = Limiter(key_func=get_remote_address, default_limits=limits)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
