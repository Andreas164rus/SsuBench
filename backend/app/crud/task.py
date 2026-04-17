from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.crud.base import CRUDBase
from app.models.role import Role


class CRUDTask(CRUDBase):
    pass


task_crud = CRUDTask(Role)
