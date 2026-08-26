from fastapi import APIRouter, status,Depends,HTTPException
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials

from app.auth.jwt_handler import decode_access_token


from app.models.user import UserRequest, UserLogin, UserResponse
from app.services import user_services


router = APIRouter()

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    try:
        payload = decode_access_token(token)

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    return payload


@router.get("/")
def home():

    return {
        "message": "API is running"
    }


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
async def register_user(data: UserRequest):

    user = await user_services.create_user(data)

    return {
        "message": "user created successfully",
        "username": user["username"],
        "email": user["email"]
    }


@router.post("/login")
async def login_user(data: UserLogin):

    user = await user_services.login_user(data)

    return user


@router.get("/me")
async def get_me(
    current_user: dict = Depends(get_current_user)
):

    email = current_user.get("email")

    if not email:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user = await user_services.get_user_profile(email)

    return {
        "message": "current user profile retrieved successfully",
        "username": user["username"],
        "email": user["email"]
    }