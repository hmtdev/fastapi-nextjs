import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class TokenBlacklist(SQLModel, table=True):
    __tablename__ = "token_blacklists"
    id: Optional[int] = Field(default=None, primary_key=True)
    jti: str = Field(index=True)
    token_type: str
    user_id: Optional[uuid.UUID] = Field(default=None, index=True)
    blacklist_at: datetime = Field(default_factory=datetime.now)
    expires_at: datetime
