from pydantic import BaseModel,EmailStr,Field

class UserRequest(BaseModel):
    username: str = Field(min_length=1,max_length=50)
    email : EmailStr
    password:str = Field(min_length=1,max_length=100)

class UserLogin(BaseModel):
    email:EmailStr
    password:str

class UserResponse(BaseModel):
    message: str
    username: str
    email: EmailStr