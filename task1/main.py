from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, EmailStr

app=FastAPI(title="Simple JSON API")


class UserRequest(BaseModel):
    name: str=Field(min_length=1,max_length=100)
    email: EmailStr
    age: int=Field(gt=18,le=150)

class UserResponse(BaseModel):
    message: str
    name: str
    email: EmailStr
    age: int

@app.post("/users",response_model=UserResponse,status_code=201)
def create_user(data: UserRequest):
    return {
        "message":"User created successfully",
        "name": data.name,
        "email": data.email,
        "age": data.age
        }
@app.get("/")
def home():
    return {"message":"Api is running"}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    if user_id !=1:
        raise HTTPException(
            status_code=404,detail="User not found"
        )
    return {
        "id":user_id,
        "message":"User found"
    }
