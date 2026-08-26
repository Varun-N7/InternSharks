from pydantic import Field,EmailStr,BaseModel

class UserRequest(BaseModel):
    username: str=Field(min_length=1,max_length=50)
    email: EmailStr
    password: str=Field(min_length=1,max_length=50)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    message:str
    username:str
    email:EmailStr