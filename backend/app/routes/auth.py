from typing import Annotated

from app.database.database import get_session
from app.schema.user import (Role, Token, TokenResponse, UserCreate,
                             UserResponse)
from app.services.auth import (authenticate_user, create_access_token,
                               get_admin_user, get_current_user, register_user)
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

router = APIRouter(tags=["Authentication"], prefix="/auth")

admin_router = APIRouter(prefix="/admin",dependencies=[Depends(get_admin_user)])


@router.post("/token")
async def login_for_access_token(
    form_data : Annotated[OAuth2PasswordRequestForm,Depends()],db:Annotated[Session , Depends(get_session)]) -> Token:
    user = authenticate_user(form_data.username,form_data.password,db)
    if not user :
        raise  HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username,"role":user.role}
    )
    return TokenResponse(access_token=access_token, token_type="bearer")

@router.post("/register")
async def register(user:UserCreate, db : Annotated[Session , Depends(get_session)]):
    return register_user(user,db)

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user=Depends(get_current_user)):
    return UserResponse.model_validate(current_user)

@router.get("/admin", response_model=UserResponse)
def read_users_admin(current_user=Depends(get_admin_user)):
    return UserResponse.model_validate(current_user)

@admin_router.post("/register")
async def register_admin(user:UserCreate, db : Annotated[Session , Depends(get_session)], current_user= Depends(get_admin_user)):
    return register_user(user,db,role=Role.ADMIN)

router.include_router(admin_router)