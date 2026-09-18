from pydantic import BaseModel


class Employee(BaseModel):
    employee_id: int
    name: str
    department: str
    designation: str
    casual_leave: int
    sick_leave: int