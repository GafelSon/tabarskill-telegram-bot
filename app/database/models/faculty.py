from uuid import uuid4 as _uuid4

from sqlalchemy import (
    BigInteger,
    Integer,
    Column,
    DateTime,
    ForeignKeyConstraint,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from . import Base


class FacultyModel(Base):
    __tablename__ = "faculty"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    short_name = Column(String(50))
    university_id = Column(BigInteger, nullable=False)
    date_created = Column(DateTime, nullable=False, server_default=func.now())
    date_updated = Column(DateTime, onupdate=func.now())

    __table_args__ = (
        ForeignKeyConstraint([university_id], ["university.id"]),
    )

    # Relationships
    university = relationship("UniversityModel", back_populates="faculties")
    majors = relationship("MajorModel", back_populates="faculty", lazy="selectin")

    @property
    def id_(self):
        return {"id": self.id}

    @property
    def meta_(self):
        return {
            "date": {"created": self.date_created, "updated": self.date_updated}
        }