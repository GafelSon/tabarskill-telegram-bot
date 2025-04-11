from sqlalchemy import (
    BigInteger,
    Column,
    Enum,
    ForeignKey,
    Integer,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from . import Base
from .enums import ProfessorPosType


class ProfessorModel(Base):
    __tablename__ = "professor"

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(BigInteger, ForeignKey("profile.id"), unique=True)

    position = Column(Enum(ProfessorPosType), nullable=False)

    profile = relationship("ProfileModel", back_populates="professor")

    @property
    def uuid(self):
        return self.id

    @property
    def id_(self):
        return {"uuid": self.uuid}

    @property
    def meta_(self):
        return {
            "date": {"created": self.date_created, "updated": self.date_updated}
        }
