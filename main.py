from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, text

import models
import schemas

from database import engine, SessionLocal

# =========================
# Create / Migrate DB
# =========================

models.Base.metadata.create_all(bind=engine)

with engine.connect() as conn:
    for column in ["avatar", "linkedin", "github", "portfolio"]:
        try:
            conn.execute(
                text(f"ALTER TABLE students ADD COLUMN {column} VARCHAR(255)")
            )
            conn.commit()
        except Exception:
            conn.rollback()  # Required — without this, the failed tx blocks the next statement

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
    if (
        not student.name.strip()
        or not student.college.strip()
        or not student.skills.strip()
    ):
        raise HTTPException(
            status_code=400,
            detail="Name, College and Skills are mandatory"
        )

    db: Session = SessionLocal()

    try:
        existing_student = (
            db.query(models.StudentDB)
            .filter(models.StudentDB.name == student.name)
            .first()
        )

        if existing_student:
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
            avatar=student.avatar,
            linkedin=student.linkedin,
            github=student.github,
            portfolio=student.portfolio
        )

        db.add(new_student)
        db.commit()
        db.refresh(new_student)

        return {
            "message": "Student Registered Successfully",
            "student_id": new_student.id
        }

    finally:
        db.close()


# =========================
# View Students
# =========================

@app.get("/students")
def get_students():
    db: Session = SessionLocal()

    try:
        students = db.query(models.StudentDB).all()

        return [
            {
                "id": s.id,
                "name": s.name,
                "college": s.college,
                "skills": s.skills,
                "interests": s.interests,
                "project_idea": s.project_idea,
                "domain": s.domain,
                "looking_for": s.looking_for,
                "avatar": s.avatar or "",
                "linkedin": s.linkedin or "",
                "github": s.github or "",
                "portfolio": s.portfolio or "",
            }
            for s in students
        ]

    finally:
        db.close()


# =========================
# View Projects
# =========================

@app.get("/projects")
def get_projects():
    db: Session = SessionLocal()

    try:
        students = db.query(models.StudentDB).all()

        return [
            {
                "student": s.name,
                "project_idea": s.project_idea,
                "domain": s.domain
            }
            for s in students
        ]

    finally:
        db.close()


# =========================
# Core Matching Logic (plain function, NOT a route)
# This is called by both /match/{name} and /top-match/{name}
# =========================

def compute_matches(name: str):
    """
    Returns a dict:
      - {"error": "Student not found"}  if the name doesn't exist
      - {"student": ..., "matches": [...]}  on success
    """
    db: Session = SessionLocal()

    try:
        current_student = (
            db.query(models.StudentDB)
            .filter(
                func.lower(func.trim(models.StudentDB.name)) == name.strip().lower()
            )
            .first()
        )

        if current_student is None:
            return {"error": "Student not found"}

        # Guard against None skills/interests
        current_skills = {
            skill.strip().lower()
            for skill in (current_student.skills or "").split(",")
            if skill.strip()
        }

        current_interests = {
            interest.strip().lower()
            for interest in (current_student.interests or "").split(",")
            if interest.strip()
        }

        all_students = db.query(models.StudentDB).all()
        matches = []

        for student in all_students:
            if student.id == current_student.id:
                continue

            other_skills = {
                skill.strip().lower()
                for skill in (student.skills or "").split(",")
                if skill.strip()
            }

            other_interests = {
                interest.strip().lower()
                for interest in (student.interests or "").split(",")
                if interest.strip()
            }

            common_skills = current_skills.intersection(other_skills)
            common_interests = current_interests.intersection(other_interests)

            total_skills = len(current_skills.union(other_skills))
            total_interests = len(current_interests.union(other_interests))

            skill_score = (len(common_skills) / max(total_skills, 1)) * 70
            interest_score = (len(common_interests) / max(total_interests, 1)) * 30
            total_score = round(skill_score + interest_score, 2)

            matches.append({
                "id": student.id,
                "avatar": student.avatar or "",
                "name": student.name,
                "college": student.college or "",
                "linkedin": student.linkedin or "",
                "github": student.github or "",
                "portfolio": student.portfolio or "",
                "match_percentage": total_score,
            })

        matches.sort(key=lambda x: x["match_percentage"], reverse=True)

        return {
            "student": current_student.name,
            "matches": matches
        }

    finally:
        db.close()


# =========================
# Team Matching — full list
# =========================

@app.get("/match/{name}")
def find_match(name: str):
    result = compute_matches(name)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


# =========================
# Search Projects
# =========================

@app.get("/search-projects/{keyword}")
def search_projects(keyword: str):
    db: Session = SessionLocal()

    try:
        students = db.query(models.StudentDB).all()
        keyword = keyword.lower().strip()
        result = []

        for student in students:
            project_idea = (student.project_idea or "").lower()
            domain = (student.domain or "").lower()
            skills = (student.skills or "").lower()

            if keyword in project_idea or keyword in domain or keyword in skills:
                result.append({
                    "student": student.name,
                    "project_idea": student.project_idea,
                    "domain": student.domain
                })

        return result

    finally:
        db.close()


# =========================
# Best Match Recommendation
# =========================

@app.get("/top-match/{name}")
def top_match(name: str):
    result = compute_matches(name)  # calls the plain helper, NOT the route

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    if len(result["matches"]) == 0:
        return {"message": "No matches found"}

    best = result["matches"][0]

    return {
        "student": result["student"],  # use the DB-canonical name, not the URL param
        "best_match": {
            "id": best["id"],
            "avatar": best["avatar"],
            "name": best["name"],
            "college": best["college"],
            "linkedin": best["linkedin"],
            "github": best["github"],
            "portfolio": best["portfolio"],
            "match_percentage": best["match_percentage"],
        }
    }
# =========================
# Serve Profile Page
# =========================

@app.get("/profile")
def profile_page():
    return FileResponse("frontend/profile.html")


# =========================
# Get Student Profile by ID
# =========================

@app.get("/profile/{student_id}")
def get_profile(student_id: int):
    db: Session = SessionLocal()

    try:
        student = (
            db.query(models.StudentDB)
            .filter(models.StudentDB.id == student_id)
            .first()
        )

        if student is None:
            raise HTTPException(status_code=404, detail="Student not found")

        return {
            "id": student.id,
            "name": student.name,
            "college": student.college,
            "skills": student.skills,
            "interests": student.interests,
            "project_idea": student.project_idea,
            "domain": student.domain,
            "looking_for": student.looking_for,
            "avatar": student.avatar or "",
            "linkedin": student.linkedin or "",
            "github": student.github or "",
            "portfolio": student.portfolio or "",
        }

    finally:
        db.close()