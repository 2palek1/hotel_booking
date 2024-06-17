import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from prometheus_fastapi_instrumentator import Instrumentator
from redis import asyncio as aioredis
from sqladmin import Admin
from fastapi_versioning import VersionedFastAPI

from app.admin.auth import authentication_backend
from app.admin.views import BookingsAdmin, HotelsAdmin, RoomsAdmin, UsersAdmin
from app.bookings.router import router as router_bookings
from app.config import settings
from app.database import engine
from app.hotels.rooms.router import router as router_rooms
from app.hotels.router import router as router_hotels
from app.images.router import router as router_images
from app.pages.router import router as router_pages
from app.users.router import router as router_users
from app.importer.router import router as router_importer
from app.logger import logger

from app.prometheus.router import router as router_prometheus

app = FastAPI()

import sentry_sdk

sentry_sdk.init(
    dsn="https://a2a15f71c435143f3dbff83f97a06f90@o4507391041273856.ingest.de.sentry.io/4507391043895376",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)



app.include_router(router_users)
app.include_router(router_bookings)
app.include_router(router_hotels)
app.include_router(router_rooms)

app.include_router(router_pages)
app.include_router(router_images)
app.include_router(router_importer)

app.include_router(router_prometheus)

# Подключение CORS, чтобы запросы к API могли приходить из браузера 
origins = [
    # 3000 - порт, на котором работает фронтенд на React.js 
    "all",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", 
                   "Access-Control-Allow-Origin",
                   "Authorization"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-PRocess-Time"] = str(process_time)
    logger.info("Request execution time", extra={
        "process_time": round(process_time, 4),
    })
    return response

@app.on_event("startup")
def startup():
    redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="cache")


app = VersionedFastAPI(
    app,
    version_format='{major}',
    prefix_format="/v{major}",
    #    description="Great users with a nice message",
    #    middleware=[
    #        Middleware(SessionMiddleware, secret_key="mysecretkey")
    #    ]
    )


admin = Admin(app, engine, authentication_backend=authentication_backend)
app.mount("/static", StaticFiles(directory="app/static"), "static")


instrumentator = Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=[".*admin.*", "/metrics"],
)
instrumentator.instrument(app).expose(app)


admin.add_view(UsersAdmin)
admin.add_view(BookingsAdmin)
admin.add_view(HotelsAdmin)
admin.add_view(RoomsAdmin)


