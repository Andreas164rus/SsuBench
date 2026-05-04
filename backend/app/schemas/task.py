from pydantic import BaseModel, ConfigDict
from typing import Optional


class TaskBase(BaseModel):
    title: str
    description: str
    price: float


class CreateTask(TaskBase):
    pass


# class


class TaskDB(TaskBase):
    id: int
    selected_executor_id: Optional[int] = None
    done_executor: bool
    done_customer: bool
    model_config = ConfigDict(from_attributes=True)


class TaskDBForAll(TaskBase):
    model_config = ConfigDict(from_attributes=True)
