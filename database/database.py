from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

POSTGRESQL_URL = f"postgresql+asyncpg://{settings.DB_USER}:"\
    f"{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}"\
        f"/{settings.DB_NAME}"

Base = declarative_base()

engine = create_async_engine(POSTGRESQL_URL, 
                             future=True)

async_session = sessionmaker(bind=engine,
                             autoflush=False,
                             class_=AsyncSession,
                             expire_on_commit=False)
async def get_session():
    try:
        session: AsyncSession = async_session()
        yield session
    finally:
       await session.close()
