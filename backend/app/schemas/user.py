from fastapi_users import schemas
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from enum import Enum


class rolesCreate(str, Enum):
    customer = "Заказчик"
    executor = "Исполнитель"

class allRoles(str, Enum):
    customer = "Заказчик"
    executor = "Исполнитель"
    admin = 'Админ'

class UserBase(BaseModel):
    username: str = Field(..., max_length=32)
    first_name: str = Field(..., max_length=32)
    last_name: str = Field(..., max_length=32)
    role_id: Optional[allRoles]


class UserRead(UserBase):
    id: int
    role_id: int
    balance: float

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    password: str
    role_id: int


class UserUpdate(schemas.BaseUserUpdate):
    pass
