from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Student(BaseModel):
    name: str
    college: str
    skills: str
    interests: str

students = []

@app.get("/")
def home():
    return {"message": "Welcome to HackBuddy 🚀"}

@app.post("/register")
def register(student: Student):
    students.append(student)
    return {
        "message": "Student Registered Successfully",
        "student": student
    }

@app.get("/students")
def get_students():
    return students

@app.get("/match/{name}")
def find_match(name: str):

    current_student = None

    for student in students:
        if student.name.lower() == name.lower():
            current_student = student

    if not current_student:
        return {"message": "Student not found"}

    matches = []

    current_skills = set(
        current_student.skills.lower().split(",")
    )

    for student in students:

        if student.name == current_student.name:
            continue

        other_skills = set(
            student.skills.lower().split(",")
        )

        common = current_skills.intersection(other_skills)

        score = len(common)

        matches.append({
            "name": student.name,
            "match_score": score
        })

    matches.sort(
        key=lambda x: x["match_score"],
        reverse=True
    )

    return matches