from typing import Annotated

from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    add_to_blacklist,
    ExpiredSignatureError,
)
from app.database.database import get_session
from app.database.redis import redis_client
from app.models.user import User
from app.schema.user import (
    Role,
    Token,
    TokenRefresh,
    TokenResponse,
    UserCreate,
    UserResponse,
    PasswordChangeRequest,
)
from app.services.auth import (
    authenticate_user,
    get_admin_user,
    verify_access_token,
    register_user,
    verify_password,
    hash_password,
)
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from app.core.security import oauth2_scheme

router = APIRouter(tags=["Authentication"], prefix="/auth")

admin_router = APIRouter(prefix="/admin", dependencies=[Depends(get_admin_user)])


@router.post("/login")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_session)],
) -> Token:
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    refresh_token = create_refresh_token(data={"sub": user.username})
    key = f"refresh_token:{user.username}:{refresh_token}"
    redis_client.setex(key,60*60*24*7,"valid")
    return TokenResponse(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


@router.post("/register")
async def register(user: UserCreate, db: Annotated[Session, Depends(get_session)]):
    return register_user(user, db)


@router.get("/me", response_model=UserResponse)
def read_users_me(current_user=Depends(verify_access_token)):
    return UserResponse.model_validate(current_user)


@router.post("/refresh-token")
async def refresh_token(
    request: TokenRefresh, db: Annotated[Session, Depends(get_session)]
) -> TokenResponse:
    try:
        payload = verify_refresh_token(request.refresh_token)
        username = payload.get("sub")
        statement = select(User).where(User.username == username)
        user = db.exec(statement).first()
        if not user:
            raise HTTPException(
                status=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )
        
        add_to_blacklist(request.refresh_token, user.id, "refresh", db)

        access_token = create_access_token(
            data={"sub": user.username, "role": user.role}
        )
        refresh_token = create_refresh_token(data={"sub": user.username})

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            username=user.username,
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired. Please login again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Failed to refresh token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/admin", response_model=UserResponse)
def read_users_admin(current_user=Depends(get_admin_user)):
    return UserResponse.model_validate(current_user)


@router.post("/change-password", status_code=status.HTTP_202_ACCEPTED)
async def change_password(
    request: PasswordChangeRequest,
    db=Depends(get_session),
    current_user: User = Depends(verify_access_token),
):
    if not verify_password(
        request.current_password, hashed_password=current_user.hashed_password
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    current_user.hashed_password = hash_password(request.new_password)
    db.add(current_user)
    db.commit()
    return {"detail": "Password changed successfully"}


@router.get("/logout")
async def logout(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(verify_access_token)],
):

    success = add_to_blacklist(token, current_user.id, "access", db)
    if success:
        return {"detail": "Successfully logged out"}
    else:
        return {"detail": "Logout processed"}


@admin_router.post("/register")
async def register_admin(
    user: UserCreate,
    db: Annotated[Session, Depends(get_session)],
    current_user=Depends(get_admin_user),
):
    return register_user(user, db, role=Role.ADMIN)

router.include_router(admin_router)
