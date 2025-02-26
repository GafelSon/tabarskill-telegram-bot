# app.database.models.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    DECIMAL
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from enum import Enum
import uuid

Base = declarative_base()

# student data model
class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_id = Column(Integer, unique=True, nullable=False)
    university_id = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    username = Column(String, unique=True, nullable=True)
    profile = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    faculty = Column(String, nullable=True)
    major = Column(String, nullable=True)
    entry_year = Column(Integer, nullable=True)
    is_premium = Column(Boolean, default=False)
    tokens = Column(Integer, default=10, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_interaction = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)