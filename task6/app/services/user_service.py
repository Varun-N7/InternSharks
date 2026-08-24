from fastapi import HTTPException
from passlib.context import CryptContext

from app.database.mongodb import users_collection

pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")

async def create_user(data):
    existing_user=await users_collection.find_one({
        "email":data.email
    })
    if existing_user:
        raise HTTPException(
            status_code=409,detail="email already registerd"
        )
    hashed_password=pwd_context.hash(data.password)

    user={
        "username":data.username,
        "email":data.email,
        "password":hashed_password
    }

    result = await users_collection.insert_one(user)

    return {
        "id":str(result.inserted_id),
        "username":user["username"],
        "email":user["email"]
    }

async def login_user(data):
    user = await users_collection.find_one({
        "email":data.email
    })
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    password_correct=pwd_context.verify(
        data.password,user["password"]
    )  

    if not password_correct:
        raise HTTPException(
           status_code=401,detail="Invalid email or password"       
        )    
    return {
    "message": "login successful",
    "username": user["username"],
    "email": user["email"]
    }

async def get_user_profile(email):

    user = await users_collection.find_one({
        "email": email
    })

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "username": user["username"],
        "email": user["email"]
    }
    



    