from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.event import listens_for
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from . import Base
from .enums import RoleType


class ProfileModel(Base):
    __tablename__ = "profile"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)

    telegram_username = Column(String(100), nullable=False)
    telegram_id = Column(String(100), nullable=False)
    telegram_picture = Column(String(255), nullable=True)

    phone = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)

    role = Column(Enum(RoleType), nullable=False)
    university_id = Column(Integer, ForeignKey("university.id"))

    university_name = Column(String) 
    faculty_name = Column(String) 
    major_name = Column(String)

    # This is for make user to support access
    flag = Column(Boolean, nullable=False, default=False)
    profile_completed = Column(Boolean, nullable=False, default=False)

    date_created = Column(DateTime, nullable=False, server_default=func.now())
    date_updated = Column(DateTime, onupdate=func.now())

    wallet = relationship("WalletBase", back_populates="profile", uselist=False)

    student = relationship(
        "StudentModel", back_populates="profile", uselist=False
    )
    professor = relationship(
        "ProfessorModel", back_populates="profile", uselist=False
    )
    # Keep the relationship as is
    university = relationship(
        "UniversityModel", back_populates="profiles", uselist=False
    )

    @property
    def id_(self):
        return {"uuid": self.uuid}

    @property
    def meta_(self):
        return {
            "date": {"created": self.date_created, "updated": self.date_updated}
        }


@listens_for(ProfileModel, "after_insert")
def create_wallet(mapper, connection, target):
    from .wallet import WalletBase

    connection.execute(
        WalletBase.__table__.insert().values(profile_id=target.id, token=20.00)
    )
