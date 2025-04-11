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

    student_id = Column(BigInteger, nullable=False, unique=True)
    enter_year = Column(Integer, nullable=False)

    dormitory = Column(Integer, default=False, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint([student_id], ["university.id"]),
        ForeignKeyConstraint(
            [profile_id], ["profile.id"], onupdate="CASCADE", ondelete="CASCADE"
        ),
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
