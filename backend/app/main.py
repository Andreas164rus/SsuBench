from fastapi import FastAPI
from app.core.config import settings
from app.api.routers import main_router
from app.core.init_db import create_roles, create_superusers
from fastapi_pagination import add_pagination
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from app.core.middleware import LoggingMiddleware

logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        RotatingFileHandler(
            logs_dir / "app.log",
            maxBytes=10_000_000,  # 10 MB
            backupCount=5,
            encoding="utf-8",
        )
    ],
)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_title)
app.add_middleware(LoggingMiddleware)


app.include_router(main_router)
add_pagination(app)  # important! add pagination to your app


@app.on_event("startup")
async def startup():
    await create_roles()
    await create_superusers()
