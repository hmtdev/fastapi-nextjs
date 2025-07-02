from typing import Annotated
import uuid
import jwt

from app.database.database import get_session
from app.models.user import User
from app.schema.user import Role, UserCreate, UserResponse, UserUpdate
from fastapi import Depends, HTTPException, status
from jwt.exceptions import InvalidTokenError
from sqlmodel import Session, select
from app.core.security import verify_password, oauth2_scheme ,hash_password, secret_key,ALGORITHM,is_blacklisted

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
def verify_access_token(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_session)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if is_blacklisted(token, db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = jwt.decode(token, secret_key,algorithms=[ALGORITHM],options={"verify_signature":True, "verify_exp":True})
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
def get_admin_user(user=Depends(verify_access_token)):
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not admin")
    return user
## register_user

def register_user(user: UserCreate, db: Session, role:Role = Role.USER) -> UserResponse:
    # Check if username already exists
    username_statement = select(User).filter(User.username == user.username)
    exist_user = db.exec(username_statement).first()
    if exist_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    
    # Check if email already exists
    if user.email:
        email_statement = select(User).filter(User.email == user.email)
        exist_email = db.exec(email_statement).first()
        if exist_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
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

def update_user(user_id: uuid.UUID, user_update: UserUpdate, db: Session) -> UserResponse:
    """
    Update user information and check for email uniqueness
    """
    statement = select(User).filter(User.id == user_id)
    db_user = db.exec(statement).first()
    
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Check if email is being updated and if it's already in use
    if user_update.email and user_update.email != db_user.email:
        email_statement = select(User).filter(User.email == user_update.email)
        exist_email = db.exec(email_statement).first()
        if exist_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    # Update user fields
    user_data = user_update.model_dump(exclude_unset=True)
    if user_update.password:
        user_data["hashed_password"] = hash_password(user_update.password)
        # Remove the original password field
        user_data.pop("password", None)
    
    for key, value in user_data.items():
        setattr(db_user, key, value)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserResponse.model_validate(db_user)