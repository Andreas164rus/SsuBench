from pydantic import BaseModel


class TaskBase(BaseModel):
    title: str
    description: str
    price: float


class CreateTask(TaskBase):
    pass


class TaskDB(TaskBase):
    class Config:
        orm_mode: True
