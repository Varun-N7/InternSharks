from fastapi import FastAPI,HTTPException
from typing import Optional

from app.models.student import UserRequest,UserResponce
from app.services import student_service

app=FastAPI(title="crud operation with MongoDB")


@app.post("/students",response_model=UserResponce,status_code=201)
async def create_user(data: UserRequest):

    student=await student_service.create_student(data)

    return{
        "message":"student created successfully",
        "id":student["id"],
        "name":student["name"],
        "email":student["email"],
        "course":student["course"]
    }


@app.put("/students/{id}")
async def update_student(id: str,data: UserRequest):

    student=await student_service.update_student(id,data)

    return{
        "message":"student updated successfully",
        "data":student
    }


@app.get("/students/search")
async def search_student(name: Optional[str]=None,course: Optional[str]=None):

    results=await student_service.search_students(name,course)

    return{
        "message":"students found successfully",
        "data":results
    }


@app.get("/students/{id}")
async def get_student(id: str):

    student=await student_service.get_student(id)

    return{
        "message":"student retived successfully",
        "data":student
    }


@app.delete("/students/{id}")
async def del_student(id: str):

    student=await student_service.delete_student(id)

    return{
        "message":"student deleted successfully",
        "data":student
    }


@app.get("/students")
async def home(course: Optional[str]=None):

    if course:

        results=await student_service.filter_students(course)

        return{
            "message":"students filtered successfully",
            "data":results
        }

    students=await student_service.get_all_students()

    return{
        "message":"student retrieved successfully",
        "data":students
    }


@app.get("/")
def home():
    return {"message":"API running successfully"}