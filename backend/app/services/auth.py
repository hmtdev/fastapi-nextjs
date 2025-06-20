from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from app.core.config import settings
from app.database.database import get_session
from app.models.user import User
from app.schema.user import Role, UserCreate, UserResponse
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
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


## create func authenticate_user
def authenticate_user(username: str, password: str, db: Session):
    statement = select(User).filter(User.username == username)
    user = db.exec(statement).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


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


## get current user
def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_session)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, secret_key, ALGORITHM)
        username = payload.get("sub", None)
        if username is None:
            raise credentials_exception
        statement = select(User).filter(User.username == username)
        user = db.exec(statement).first()
        if user is None:
            raise credentials_exception
        return user
    except InvalidTokenError:
        raise credentials_exception


## get_admin user
def get_admin_user(user=Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not admin")
    return user


## register_user
def register_user(user: UserCreate, db: Session, role:Role = Role.USER) -> UserResponse:
    statement = select(User).filter(User.username == user.username)
    exist_user = db.exec(statement).first()
    if exist_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Username already registered")
    hashed_password = hash_password(user.password)
    db_user = User(
        username=user.username,
        full_name=user.full_name,
        hashed_password= hashed_password,
        role = role,
        email=user.email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return UserResponse.model_validate(db_user)