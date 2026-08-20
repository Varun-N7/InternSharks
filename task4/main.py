from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,Field,EmailStr
from typing import Optional
import os
import json

app=FastAPI(title="crud operation with database")
FILE_NAME="students.json"

students=[] 

def load_students():
    global students

    try:
        if not os.path.exists(FILE_NAME):
            students=[]
            return 
    
        with open(FILE_NAME,"r") as file:
            data=json.load(file)
            students=[UserRequest(**student) for student in data]

    except json.JSONDecodeError:
        students=[]
    except Exception:
        students=[]


def save_students():
    try:
        with open(FILE_NAME,"w") as file:
            json.dump(
                [student.model_dump(mode="json") for student in students],
                file,
                indent=4
            )
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Error saving students: {str(e)}")


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


load_students()


@app.post("/students",response_model=UserResponce,status_code=201)
def create_user(data: UserRequest):
    students.append(data)
    save_students()

    return{
        "message":"student created successfully",
        "id":data.id,
        "name":data.name,
        "email":data.email,
        "course":data.course
    }


@app.put("/students/{id}")
def update_student(id: str,data: UserRequest):
    for student in students:
        if student.id==id:
            student.name=data.name
            student.email=data.email
            student.course=data.course
            save_students()

            return{
                "message":"student updated successfully",
                "data":student
            }

    raise HTTPException(status_code=404,detail="student not found")


@app.get("/students/search")
def search_student(name: Optional[str]=None,course: Optional[str]=None ):

    results=[]

    for student in students:
        if student.name==name:
            results.append(student)

        if student.course==course:
            results.append(student)

    if not results:
        raise HTTPException(
            status_code=404,
            detail="No student found in that name"
        )
    return {
        "message":"students found successfully",
        "data":results
    }


@app.get("/students/{id}")
def get_student(id: str):
    for student in students:
        if student.id==id:
            return {
                "message":"student retived successfully",
                "data":student}
    raise HTTPException(
        status_code=404,
        detail="Student not found"
    ) 


@app.delete("/students/{id}")
def del_student(id: str):
    for student in students:
        if student.id==id:
            students.remove(student)
            save_students()

            return {
                "message":"student deleted successfully",
                "data":student
            }
    raise HTTPException(
        status_code=404,
        detail="student not found"
    )


@app.get("/students")
def home():
    return {"message":"student retrieved successfully",
            "data":students}


@app.get("/")
def home():
    return {"message":"API running successfully"}