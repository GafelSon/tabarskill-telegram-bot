from sqlalchemy import (
    BigInteger,
    Column,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
)
from sqlalchemy.orm import relationship

from . import Base


class StudentModel(Base):
    __tablename__ = "student"

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(BigInteger, ForeignKey("profile.id"), unique=True)
    university_id = Column(BigInteger, nullable=True)

    student_id = Column(BigInteger, nullable=True, unique=True)
    enter_year = Column(Integer, nullable=True)

    dormitory = Column(Integer, default=False, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            [profile_id], ["profile.id"], onupdate="CASCADE", ondelete="CASCADE"
        ),
        ForeignKeyConstraint([university_id], ["university.id"]),
    )

    profile = relationship(
        "ProfileModel", back_populates="student", uselist=False
    )
    university = relationship(
        "UniversityModel", back_populates="students", uselist=False
    )

    @property
    def id_(self):
        return {"uuid": self.uuid}

    @property
    def meta_(self):
        return {
            "date": {"created": self.date_created, "updated": self.date_updated}
        }
