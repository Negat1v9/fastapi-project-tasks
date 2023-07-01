import asyncio
import pytest
import random
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, insert
from database.models import User, Mission, ManagerGroup
from main import app
from database.database import get_session
from database.database import Base
from app.oauth2 import create_access_token
TEST_POSTGRES_URL = f"postgresql+asyncpg://testus2:testus2@localhost:5432/test"

test_engine = create_async_engine(TEST_POSTGRES_URL)

test_async_session = async_sessionmaker(bind=test_engine, expire_on_commit=False, class_=AsyncSession)


# Base.metadata.bind = test_engine

@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
    
# get test session to all test requets
async def get_test_session():
    async with test_async_session() as session:
        yield session

app.dependency_overrides[get_session] = get_test_session

@pytest.fixture(scope="session", autouse=True)
async def create_drop_test_db():
    async with test_engine.begin() as conn:
        Base.metadata.bind = test_engine
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:     
        await conn.run_sync(Base.metadata.drop_all)
                
# get test 
@pytest.fixture(scope="session")
async def client():
    async with AsyncClient(app=app, base_url="http://localhost:8000/") as client:
        yield client


def create_headers_for_user(id) -> dict[str, str]:
    access_token = create_access_token(
        data={"user_id": str(id)})
    return {"Authorization": f"Bearer {access_token}"}
    
async def create_test_user_in_db(**kwargs) -> tuple:
    async with test_async_session.begin() as ss:
        query = (insert(User).values(kwargs))
        await ss.execute(query)
        await ss.commit()
        
async def get_test_user_by_id(id) -> User:
    async with test_async_session.begin() as ss:
        query = (select(User)
                 .where(User.id == id))
        res = await ss.execute(query)
    user = res.fetchone()
    return user[0] if user else None

async def create_task_in_db(**kwargs) -> tuple:
    async with test_async_session.begin() as ss:
        query = (insert(Mission).
                 values(kwargs)
                 .returning(Mission.task,
                            Mission.owner_id,
                            Mission.id))
        res = await ss.execute(query)
        await ss.commit()
    return res
        
def create_user_not_id() -> dict:
    email = str(random.randint(-10000, 1000)) + "@mail.com"
    id = random.randint(1, 999999)
    user = {
        "id": id,
        "first_name": "John",
        "last_name": "Johnson",
        "email": email,
        "password": "qwerty123"}
    
    return user
