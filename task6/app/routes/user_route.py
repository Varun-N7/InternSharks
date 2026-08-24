from fastapi import APIRouter,status

from app.models.user import UserRequest,UserLogin,UserResponse
from app.services import user_service

router=APIRouter()

@router.get("/")
def home():
    return{"message":"API is running"}

@router.post("/register",response_model=UserResponse,status_code=status.HTTP_201_CREATED)
async def register_user(data: UserRequest):
    user = await user_service.create_user(data)

    return{
        "message":"user created successfully",
        "username":user["username"],
        "email":user["email"]
    }

@router.post("/login")
async def login_use(data: UserLogin):
    user = await user_service.login_user(data)

    return user 

@router.get("/profile")
async def get_profile(email: str):
    user = await user_service.get_user_profile(email)
    return {
        "message":"user profile retrieved successfully",
        "username":user["username"],
        "email":user["email"]
}




