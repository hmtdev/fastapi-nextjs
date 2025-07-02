from typing import Annotated
import uuid

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
    UserUpdate,
    GoogleUserRequest
)
from app.services.auth import (
    authenticate_user,
    get_admin_user,
    verify_access_token,
    register_user,
    verify_password,
    hash_password,
    update_user,
    update_google_user
)
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from app.core.security import oauth2_scheme
from fastapi.responses import RedirectResponse
from fastapi import Request
from urllib.parse import urlencode
from app.core.config import get_settings
import httpx
import jwt 

settings = get_settings()

router = APIRouter(tags=["Authentication"], prefix="/auth")

admin_router = APIRouter(prefix="/admin", dependencies=[Depends(get_admin_user)])

google_router = APIRouter(prefix="/google",tags=['Google Auth'])

@google_router.get("/callback")
async def google_callback(request: Request, db = Depends(get_session)):
    code = request.query_params.get("code")
    if not code:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Not auth")
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(token_url, data=data)
        token_data = resp.json()
    id_token = token_data.get("id_token")
    payload = jwt.decode(id_token, options={"verify_signature": False})
    try:
        user_update = GoogleUserRequest(**payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid Google user data: {e}")
    user = update_google_user(user_update,db)
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    refresh_token = create_refresh_token(data={"sub": user.username})
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        username=user.username,
    )

@google_router.get("/login")
async def login_with_google():
    params = {
        "client_id" : settings.GOOGLE_CLIENT_ID,
        "response_type": "code",
        "scope": "openid email profile",
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "access_type": "offline",
        "prompt": "consent"
    }
    url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    print(url)
    # return RedirectResponse(url)
    return {
        "url" : url
    }

@router.post("/login")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_session)],
) -> Token:
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
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


@router.put("/update", response_model=UserResponse)
async def update_user_info(
    user_update: UserUpdate,
    db: Annotated[Session, Depends(get_session)],
    current_user: User = Depends(verify_access_token),
):
    """
    Update the current user's information
    """
    return update_user(current_user.id, user_update, db)


@admin_router.put("/users/{user_id}", response_model=UserResponse)
async def update_user_by_admin(
    user_id: uuid.UUID,
    user_update: UserUpdate,
    db: Annotated[Session, Depends(get_session)],
    current_user: User = Depends(get_admin_user),
):
    """
    Admin endpoint to update any user's information
    """
    return update_user(user_id, user_update, db)

router.include_router(admin_router)
router.include_router(google_router)