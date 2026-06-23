from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func

import models
import schemas

from database import engine, SessionLocal

# Create database tables
models.Base.metadata.create_all(bind=engine)
from sqlalchemy import text

with engine.connect() as conn:
    try:
        conn.execute(
            text("ALTER TABLE students ADD COLUMN avatar VARCHAR(255)")
        )
        conn.commit()
        print("Avatar column added")
    except Exception as e:
        print("Avatar column already exists or error:", e)

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory="frontend"),
    name="static"
)

# =========================
# CORS
# =========================

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
        project_idea=student.project_idea,
        domain=student.domain,
        looking_for=student.looking_for,
        avatar=student.avatar
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
            "project_idea": student.project_idea,
            "domain": student.domain,
            "looking_for": student.looking_for,
            "avatar": student.avatar

        })

    db.close()

    return result


# =========================
# View Projects
# =========================

@app.get("/projects")
def get_projects():

    db: Session = SessionLocal()

    students = db.query(models.StudentDB).all()

    projects = []

    for student in students:

        projects.append({
            "student": student.name,
            "project_idea": student.project_idea,
            "domain": student.domain
        })

    db.close()

    return projects


# =========================
# Team Matching
# =========================

@app.get("/match/{name}")
def find_match(name: str):

    db: Session = SessionLocal()

    current_student = (
        db.query(models.StudentDB)
        .filter(
            func.lower(
                func.trim(models.StudentDB.name)
            ) == name.strip().lower()
        )
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

        total_skills = len(
            current_skills.union(other_skills)
        )

        total_interests = len(
            current_interests.union(other_interests)
        )

        skill_score = (
            len(common_skills)
            / max(total_skills, 1)
        ) * 70

        interest_score = (
            len(common_interests)
            / max(total_interests, 1)
        ) * 30

        total_score = round(
            skill_score + interest_score,
            2
        )
        matches.append({
            "name": student.name,
            "college": student.college,
            "project_idea": student.project_idea,
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
# Search Projects
# =========================

@app.get("/search-projects/{keyword}")
def search_projects(keyword: str):

    db: Session = SessionLocal()

    students = db.query(models.StudentDB).all()

    result = []

    keyword = keyword.lower().strip()

    for student in students:

        project_idea = (
            student.project_idea or ""
        ).lower()

        domain = (
            student.domain or ""
        ).lower()

        skills = (
            student.skills or ""
        ).lower()

        if (
            keyword in project_idea
            or keyword in domain
            or keyword in skills
        ):

            result.append({
                "student": student.name,
                "project_idea": student.project_idea,
                "domain": student.domain
            })

    db.close()

    return result


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