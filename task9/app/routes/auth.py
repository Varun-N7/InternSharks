import uuid

from fastapi import APIRouter, HTTPException, status

from app.auth.jwt_handler import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.models.auth import (
    AccessTokenResponse,
    LoginRequest,
    MessageResponse,
    RefreshRequest,
    TokenResponse,
)
from app.models.user import (
    UserCreate,
    UserResponse,
)
from app.services.auth_service import (
    create_refresh_session,
    get_refresh_session,
    refresh_session_is_expired,
    revoke_refresh_session,
    verify_password,
)
from app.services.user_service import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    serialize_user,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: UserCreate,
):
    user = await create_user(
        username=data.username,
        email=data.email,
        password=data.password,
        full_name=data.full_name,
        phone=data.phone,
        department=data.department,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists",
        )

    return serialize_user(user)


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    data: LoginRequest,
):
    user = await get_user_by_email(
        data.email
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(
        data.password,
        user["password_hash"],
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    user_id = user["_id"]

    access_token = create_access_token(
        user_id
    )

    session_id = str(uuid.uuid4())

    refresh_token = create_refresh_token(
        user_id,
        session_id,
    )

    await create_refresh_session(
        user_id=user_id,
        session_id=session_id,
        refresh_token=refresh_token,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post(
    "/refresh",
    response_model=AccessTokenResponse,
)
async def refresh(
    data: RefreshRequest,
):
    payload = decode_token(
        data.refresh_token
    )

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required",
        )

    user_id = payload.get("sub")
    session_id = payload.get("session_id")

    if not user_id or not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    session = await get_refresh_session(
        session_id,
        data.refresh_token,
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh session not found",
        )

    if session.get("revoked", False):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked",
        )

    if refresh_session_is_expired(
        session
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired",
        )

    if session.get("user_id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh session",
        )

    user = await get_user_by_id(
        user_id
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
        )

    new_access_token = create_access_token(
        user_id
    )

    return AccessTokenResponse(
        access_token=new_access_token,
        token_type="bearer",
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
)
async def logout(
    data: RefreshRequest,
):
    payload = decode_token(
        data.refresh_token
    )

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required",
        )

    session_id = payload.get("session_id")

    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    session = await get_refresh_session(
        session_id,
        data.refresh_token,
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh session not found",
        )

    if session.get("revoked", False):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token already revoked",
        )

    await revoke_refresh_session(
        session_id
    )

    return MessageResponse(
        message="Logout successful"
    )