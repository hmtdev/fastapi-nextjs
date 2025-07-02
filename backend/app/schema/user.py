from pydantic import BaseModel, EmailStr, ConfigDict, Field,ValidationInfo, field_validator
import uuid
from typing import Optional
from app.models.user import Role


class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None


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
    refresh_token: str


class TokenResponse(Token):
    username: Optional[str] = None


class TokenRefresh(BaseModel):
    refresh_token: str


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., description="Confirm new password")
    
    @field_validator('confirm_password')
    def ensure_passwords_match(cls,v: str, info: ValidationInfo) -> str:
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("passwords do not match")
        return v