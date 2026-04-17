from fastapi_users import schemas
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class rolesCreate(str, Enum):
    customer = "Заказчик"
    executor = "Исполнитель"


class UserBase(BaseModel):
    username: str = Field(..., max_length=32)
    first_name: str = Field(..., max_length=32)
    last_name: str = Field(..., max_length=32)
    role_id: Optional[rolesCreate]


class UserRead(UserBase):
    role_id: int

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    password: str


class UserUpdate(schemas.BaseUserUpdate):
    pass
