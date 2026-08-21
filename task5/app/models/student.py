from pydantic import BaseModel,Field,EmailStr
from typing import Optional

class UserRequest(BaseModel):
    id: str=Field(min_length=1,max_length=35)
    name: str=Field(min_length=1,max_length=50)
    email: EmailStr
    course: str=Field(min_length=1,max_length=50)

class UserResponce(BaseModel):
    message: str
    id: str
    name: str
    email: EmailStr
    course: str