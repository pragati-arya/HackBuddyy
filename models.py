from sqlalchemy import Column, Integer, String
from database import Base


class StudentDB(Base):
    __tablename__ = "students"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        unique=True,
        index=True
    )

    college = Column(String)

    skills = Column(String)

    interests = Column(String)

    domain = Column(String)

    looking_for = Column(String)

    delete_code = Column(String)