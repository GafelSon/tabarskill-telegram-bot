from uuid import uuid4 as _uuid4

from sqlalchemy import (
    BigInteger,
    Integer,
    Column,
    DateTime,
    ForeignKeyConstraint,
    String,
    Text,
)
from sqlalchemy import (
    text as sqlalchemy_text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from . import Base


class MajorModel(Base):
    __tablename__ = "major"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    short_name = Column(String(50))
    faculty_id = Column(BigInteger, nullable=False)
    date_created = Column(DateTime, nullable=False, server_default=func.now())
    date_updated = Column(DateTime, onupdate=func.now())

    __table_args__ = (
        ForeignKeyConstraint([faculty_id], ["faculty.id"]),
    )

    # Relationships
    faculty = relationship("FacultyModel", back_populates="majors")

    @property
    def id_(self):
        return {"id": self.id}

    @property
    def meta_(self):
        return {
            "date": {"created": self.date_created, "updated": self.date_updated}
        }