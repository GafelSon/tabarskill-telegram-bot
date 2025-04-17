from uuid import uuid4 as _uuid4

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from . import Base


class UniversityModel(Base):
    __tablename__ = "university"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(
        String(36), nullable=True, unique=True
    )
    name = Column(String(255), nullable=False)
    short_name = Column(String(50))
    logo = Column(String(255))
    website = Column(String(255))
    address = Column(String(500))
    date_created = Column(DateTime, nullable=False, server_default=func.now())
    date_updated = Column(DateTime, onupdate=func.now())

    # Relationships
    profiles = relationship("ProfileModel", back_populates="university", lazy="selectin")
    students = relationship("StudentModel", back_populates="university", lazy="selectin")
    faculties = relationship("FacultyModel", back_populates="university", lazy="selectin")

    @property
    def id_(self):
        return {"uuid": self.uuid}

    @property
    def meta_(self):
        return {
            "date": {"created": self.date_created, "updated": self.date_updated}
        }
