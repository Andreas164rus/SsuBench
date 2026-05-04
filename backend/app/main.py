from fastapi import FastAPI
from app.core.config import settings
from app.api.routers import main_router
from app.core.init_db import create_roles, create_superusers
from fastapi_pagination import add_pagination

app = FastAPI(title=settings.app_title)

app.include_router(main_router)
add_pagination(app)  # important! add pagination to your app


# @app.on_event("startup")
# async def startup():
    # await create_roles()
    # await create_superusers()
