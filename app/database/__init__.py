from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from contextlib import asynccontextmanager
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from .models import Base
import os

class Database:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, url: str = None):
        if not hasattr(self, 'engine'):
            self.database_url = url or os.getenv("DATABASE_URL", "sqlite+aiosqlite:///bot.db")
            self.engine = create_async_engine(
                self.database_url,
                poolclass=NullPool,
                echo=False
            )
            self.async_session = sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False
            )

    async def init(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @asynccontextmanager
    async def session(self):
        async with self.async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def get_db(self) -> AsyncSession:
        async with self.async_session() as session:
            try:
                yield session
            finally:
                await session.close()