from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from . import Base
from .enums import EventType, RepeatType


class EventModel(Base):
    __tablename__ = "event"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    date = Column(DateTime, nullable=False)
    type = Column(Enum(EventType), nullable=False)
    repeat = Column(Enum(RepeatType), nullable=False, default=RepeatType.NONE)

    created_by = Column(String(100), ForeignKey("profile.telegram_id"), nullable=False)
    profile = relationship("ProfileModel", backref="events")

    notify_before = Column(Integer, nullable=True)

    is_holiday = Column(Boolean, default=False)
    is_religious = Column(Boolean, default=False)
    additional_description = Column(Text, nullable=True)

    image = Column(String(255), nullable=True)
    like_count = Column(Integer, default=0)
    confirmed = Column(Boolean, default=False)

    date_created = Column(DateTime, nullable=False, server_default=func.now())
    date_updated = Column(DateTime, onupdate=func.now())

    @property
    def id_(self):
        return {"id": self.id}

    @property
    def meta_(self):
        return {"date": {"created": self.date_created, "updated": self.date_updated}}


class EventLikeModel(Base):
    __tablename__ = "event_like"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey("event.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(100), nullable=False)
    event = relationship("EventModel", backref="likes")
    __table_args__ = (UniqueConstraint("event_id", "user_id", name="unique_event_user_like"),)
