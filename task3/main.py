from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,Field,EmailStr
from typing import Optional 

app=FastAPI(title="CRUD operation")

students=[]


class Stud_create(BaseModel):
    id: str=Field(min_length=1,max_length=35)
    name: str=Field(min_length=1,max_length=40)
    email: EmailStr
    course: str=Field(min_length=1,max_length=70)

class UserResponce(BaseModel):
    message: str
    id: str
    name: str
    email: EmailStr
    course: str
@app.post("/students",response_model=UserResponce,status_code=201)


def create_user(data: Stud_create):

    students.append(data)
    return {
        "message":"student created succefully",
        "id": data.id,
        "name": data.name,
        "email": data.email,
        "course": data.course
    }

@app.put("/students/{id}")
def update_student(id: str, data: Stud_create):
    for student in students:
        if student.id ==id:
            student.name=data.name
            student.email=data.email
            student.course=data.course
            return{
                "message":"Student upadted successfully",
                "data":student
            }
    raise HTTPException(
        status_code=404,
        detail="Student not found"
    )
##############################

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

@app.get("/students/search") 
def search_course(course: str):
    for student in students:
           if student.course==course:
               return {
                   "message":"student retrived successfully",
                   "data":student
               }
    raise HTTPException(status_code=404,detail="course not found")
#######################################3
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
    return {"API is running"}



