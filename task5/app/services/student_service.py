from fastapi import HTTPException
from typing import Optional

from app.database.mongodb import student_collection
from app.models.student import UserRequest


async def create_student(data: UserRequest):

    student={
        "id":data.id,
        "name":data.name,
        "email":str(data.email),
        "course":data.course
    }

    existing_student=await student_collection.find_one({"id":data.id})

    if existing_student:
        raise HTTPException(
            status_code=400,
            detail="Student ID already exists"
        )

    await student_collection.insert_one(student)

    return student


async def get_all_students():

    students=[]

    cursor=student_collection.find()

    async for student in cursor:
        student.pop("_id",None)
        students.append(student)

    return students


async def get_student(id: str):

    student=await student_collection.find_one({"id":id})

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    student.pop("_id",None)

    return student


async def update_student(id: str,data: UserRequest):

    student=await student_collection.find_one({"id":id})

    if not student:
        raise HTTPException(
            status_code=404,
            detail="student not found"
        )

    await student_collection.update_one(
        {"id":id},
        {
            "$set":{
                "name":data.name,
                "email":str(data.email),
                "course":data.course
            }
        }
    )

    student=await student_collection.find_one({"id":id})

    student.pop("_id",None)

    return student


async def delete_student(id: str):

    student=await student_collection.find_one({"id":id})

    if not student:
        raise HTTPException(
            status_code=404,
            detail="student not found"
        )

    await student_collection.delete_one({"id":id})

    student.pop("_id",None)

    return student


async def search_students(name: Optional[str]=None,course: Optional[str]=None):

    results=[]

    if name:

        cursor=student_collection.find({"name":name})

        async for student in cursor:
            student.pop("_id",None)
            results.append(student)

    if course:

        cursor=student_collection.find({"course":course})

        async for student in cursor:
            student.pop("_id",None)
            results.append(student)

    if not results:
        raise HTTPException(
            status_code=404,
            detail="No student found"
        )

    return results


async def filter_students(course: str):

    results=[]

    cursor=student_collection.find({"course":course})

    async for student in cursor:
        student.pop("_id",None)
        results.append(student)

    if not results:
        raise HTTPException(
            status_code=404,
            detail="No students found for this course"
        )

    return results