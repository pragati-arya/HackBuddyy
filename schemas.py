from pydantic import BaseModel


class StudentCreate(BaseModel):

    name: str

    college: str

    skills: str

    interests: str

    project_idea: str

    domain: str

    looking_for: str

    avatar: str

    linkedin: str | None = None
    github: str | None = None
    portfolio: str | None = None


class StudentResponse(BaseModel):

    id: int

    name: str

    college: str

    skills: str

    interests: str

    project_idea: str

    domain: str

    looking_for: str

    avatar: str

    linkedin: str | None = None
    github: str | None = None
    portfolio: str | None = None

    class Config:
        from_attributes = True

class StudentUpdate(BaseModel):
    confirm_name: str      # used for identity verification
    college: str
    skills: str
    interests: str = ""
    project_idea: str = ""
    domain: str = ""
    looking_for: str = ""
    avatar: str = ""
    linkedin: str = ""
    github: str = ""
    portfolio: str = ""