from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

POSTGRESQL_URL = f"postgresql+asyncpg://{settings.DB_USER}:"\
    f"{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}"\
        f"/{settings.DB_NAME}"

# Base = declarative_base()

class Base(DeclarativeBase): pass

engine = create_async_engine(POSTGRESQL_URL, 
                             future=True)

async_session = async_sessionmaker(bind=engine,
                             autoflush=False,
                             class_=AsyncSession,
                             expire_on_commit=False)
async def get_session():
    try:
        session: AsyncSession = async_session()
        yield session
    finally:
       await session.close()
