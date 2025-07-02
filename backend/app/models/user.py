import uuid
from enum import Enum

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(unique=True, nullable=False)
    full_name:str = Field(nullable=False)
    hashed_password: str = Field()
    email: EmailStr = Field(unique=True, nullable=False)
    is_active: bool = Field(default=True, nullable=False)
    role: str = Field(default=Role.USER, nullable=False)
