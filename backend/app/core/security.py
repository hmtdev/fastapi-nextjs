import uuid
from datetime import datetime, timedelta, timezone

import jwt
from app.core.config import settings
from app.models.auth import TokenBlacklist
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import ExpiredSignatureError, InvalidTokenError
from passlib.context import CryptContext
from sqlmodel import Session, select

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
def create_token(
    data: dict, token_type: str = None, expires_delta: timedelta | None = None
):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        if token_type == "refresh":
            expire = datetime.now(timezone.utc) + timedelta(days=7)
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                access_token_expires_minutes
            )
    jti = str(uuid.uuid4())
    to_encode.update({"exp": expire, "jti": jti})
    if token_type == "refresh":
        to_encode.update({"type": "refresh"})
    encode_jwt = jwt.encode(to_encode, secret_key, ALGORITHM)
    return encode_jwt


def create_access_token(data: dict, expires_delta: timedelta = None):
    return create_token(data, token_type="access", expires_delta=expires_delta)


def create_refresh_token(data: dict, expires_delta: timedelta = None):
    return create_token(data, token_type="refresh", expires_delta=expires_delta)


def verify_refresh_token(token: str):
    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])

        if not payload.get("jti"):
            raise InvalidTokenError("Missing JWT ID")

        if payload.get("type") != "refresh":
            raise InvalidTokenError("Not a refresh token")

        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired",
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )


def add_to_blacklist(token: str, user_id: str, token_type: str, db: Session) -> bool:
    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        exp_timestamp = payload.get("exp")
        if not jti:
            return False
        expires_at = datetime.fromtimestamp(exp_timestamp)
        statement = select(TokenBlacklist).where(TokenBlacklist.jti == jti)
        existing = db.exec(statement).first()
        if existing:
            return True

        token_blacklist = TokenBlacklist(
            jti=jti, token_type=token_type, user_id=user_id, expires_at=expires_at
        )
        db.add(token_blacklist)
        db.commit()
        return True
    except Exception as e:
        return False


def is_blacklisted(token, db: Session) -> bool:
    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        if not jti:
            return False
        statement = select(TokenBlacklist).where(TokenBlacklist.jti == jti)
        blacklisted = db.exec(statement).first()

        return blacklisted is not None

    except Exception as e:
        return False
