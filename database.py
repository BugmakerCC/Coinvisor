# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

DATABASE_URL = "postgresql://dev_user:cc010426.@localhost:5432/ccai_db"
ASYNC_DATABASE_URL = "postgresql+asyncpg://dev_user:cc010426.@localhost:5432/ccai_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async_engine = create_async_engine(ASYNC_DATABASE_URL, pool_size=20)
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


Base = declarative_base()