from uuid import uuid4 as _uuid4

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKeyConstraint,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from . import Base


class WalletBase(Base):
    __tablename__ = "wallet"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(
        String(36), default=lambda: str(_uuid4()), nullable=False, unique=True
    )
    token = Column(Numeric(10, 2), default=20.00, nullable=False)
    profile_id = Column(Integer, nullable=False)
    date_created = Column(DateTime, nullable=False, server_default=func.now())
    date_updated = Column(DateTime, onupdate=func.now())

    __table_args__ = (
        ForeignKeyConstraint(
            [profile_id], ["profile.id"], onupdate="CASCADE", ondelete="CASCADE"
        ),
    )

    profile = relationship(
        "ProfileModel", back_populates="wallet", uselist=False
    )

    @property
    def id_(self):
        return {"uuid": self.uuid}

    @property
    def meta_(self):
        return {
            "date": {"created": self.date_created, "updated": self.date_updated}
        }
