from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models
import schemas

from database import engine, SessionLocal

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount(
    "/static",
    StaticFiles(directory="frontend"),
    name="static"
)

# CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Home
# =========================

@app.get("/")
def home():
    return FileResponse("frontend/index.html")

# =========================
# Register Student
# =========================

@app.post("/register")
def register(student: schemas.StudentCreate):

    db: Session = SessionLocal()

    existing_student = (
        db.query(models.StudentDB)
        .filter(models.StudentDB.name == student.name)
        .first()
    )

    if existing_student:

        db.close()

        raise HTTPException(
            status_code=400,
            detail="Student already exists"
        )

    new_student = models.StudentDB(
        name=student.name,
        college=student.college,
        skills=student.skills,
        interests=student.interests,
        domain=student.domain,
        looking_for=student.looking_for,
        delete_code=student.delete_code
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    db.close()

    return {
        "message": "Student Registered Successfully",
        "student_id": new_student.id
    }


# =========================
# View Students
# =========================

@app.get("/students")
def get_students():

    db: Session = SessionLocal()

    students = db.query(models.StudentDB).all()

    result = []

    for student in students:

        result.append({
            "id": student.id,
            "name": student.name,
            "college": student.college,
            "skills": student.skills,
            "interests": student.interests,
            "domain": student.domain,
            "looking_for": student.looking_for
        })

    db.close()

    return result
# =========================
# Delete Student
# =========================

@app.delete("/delete-student/{name}/{delete_code}")
def delete_student(name: str, delete_code: str):

    db: Session = SessionLocal()

    student = (
        db.query(models.StudentDB)
        .filter(models.StudentDB.name == name)
        .first()
    )

    if not student:

        db.close()

        return {
            "message": "Student not found"
        }

    if student.delete_code != delete_code:

        db.close()

        return {
            "message": "Incorrect delete code"
        }

    db.delete(student)
    db.commit()

    db.close()

    return {
        "message": f"{name} deleted successfully"
    }



# =========================
# Team Matching
# =========================

@app.get("/match/{name}")
def find_match(name: str):

    db: Session = SessionLocal()

    current_student = (
        db.query(models.StudentDB)
        .filter(models.StudentDB.name == name)
        .first()
    )

    if current_student is None:

        db.close()

        return {
            "message": "Student not found"
        }

    current_skills = {
        skill.strip().lower()
        for skill in current_student.skills.split(",")
    }

    current_interests = {
        interest.strip().lower()
        for interest in current_student.interests.split(",")
    }

    matches = []

    all_students = db.query(models.StudentDB).all()

    for student in all_students:

        if student.name == current_student.name:
            continue

        other_skills = {
            skill.strip().lower()
            for skill in student.skills.split(",")
        }

        other_interests = {
            interest.strip().lower()
            for interest in student.interests.split(",")
        }

        common_skills = current_skills.intersection(
            other_skills
        )

        common_interests = current_interests.intersection(
            other_interests
        )

        skill_score = (
            len(common_skills)
            / max(len(current_skills), 1)
        ) * 70

        interest_score = (
            len(common_interests)
            / max(len(current_interests), 1)
        ) * 30

        total_score = round(
            skill_score + interest_score,
            2
        )

        matches.append({
            "name": student.name,
            "college": student.college,
            "domain": student.domain,
            "match_percentage": total_score,
            "common_skills": list(common_skills),
            "common_interests": list(common_interests)
        })

    matches.sort(
        key=lambda x: x["match_percentage"],
        reverse=True
    )

    db.close()

    return {
        "student": current_student.name,
        "matches": matches
    }



# =========================
# Best Match Recommendation
# =========================

@app.get("/top-match/{name}")
def top_match(name: str):

    result = find_match(name)

    if "matches" not in result:

        return result

    if len(result["matches"]) == 0:

        return {
            "message": "No matches found"
        }

    return {
        "student": name,
        "best_match": result["matches"][0]
    }