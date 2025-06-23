from datetime import datetime, timedelta, timezone

import jwt
from app.core.config import settings
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

ALGORITHM = "HS256"
access_token_expires_minutes = settings.access_token_expire_minutes
secret_key = settings.secret_key

## create CryptContext for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


## Create func to verify password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


## Create func to hash password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


## create access token
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(access_token_expires_minutes)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, secret_key, ALGORITHM)
    return encode_jwt
