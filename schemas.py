from pydantic import BaseModel


class StudentCreate(BaseModel):

    name: str

    college: str

    skills: str

    interests: str

    project_idea: str

    domain: str

    looking_for: str


class StudentResponse(BaseModel):

    id: int

    name: str

    college: str

    skills: str

    interests: str

    project_idea: str

    domain: str

    looking_for: str

    class Config:
        from_attributes = True