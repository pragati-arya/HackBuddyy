from pydantic import BaseModel


class StudentCreate(BaseModel):

    name: str

    college: str

    skills: str

    interests: str

    domain: str

    looking_for: str

    delete_code: str


class StudentResponse(BaseModel):

    id: int

    name: str

    college: str

    skills: str

    interests: str

    domain: str

    looking_for: str


    class Config:
        from_attributes = True