from pydantic import BaseModel
from typing import Optional


class TaskBase(BaseModel):
    title: str
    description: str
    price: float


class CreateTask(TaskBase):
    pass


class TaskDB(TaskBase):
    selected_executor_id: Optional[int] = None

    class Config:
        from_attributes = True
