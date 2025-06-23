from pydantic import BaseModel, EmailStr, ConfigDict, Field
import uuid
from typing import Optional
from app.models.user import Role

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str

class UserCreate(UserBase):
    password: str = Field(min_length=8)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: uuid.UUID
    is_active: bool
    role: Role
    model_config = ConfigDict(from_attributes=True)


# Schemas for authentication
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenResponse(Token):
    username: Optional[str] = None