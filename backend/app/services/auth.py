from typing import Annotated

import jwt
from app.database.database import get_session
from app.models.user import User
from app.schema.user import Role, UserCreate, UserResponse
from fastapi import Depends, HTTPException, status
from jwt.exceptions import InvalidTokenError
from sqlmodel import Session, select
from app.core.security import verify_password, oauth2_scheme ,hash_password, secret_key,ALGORITHM

## create func authenticate_user
def authenticate_user(username: str, password: str, db: Session):
    statement = select(User).filter(User.username == username)
    user = db.exec(statement).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


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
        payload = jwt.decode(token, secret_key,ALGORITHM)
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