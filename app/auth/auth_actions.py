from sqlalchemy import insert, select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, NoResultFound

from fastapi import HTTPException

from uuid import uuid4
import random
import string

from .. config import settings
from ..database.models import RefreshToken, User

# string to generate refresh token
FOOL_STRING = string.ascii_letters + string.digits + settings.REFRESH_SECRET

# get user with all his data only for auth
async def get_user_by_id_to_auth(
    session: AsyncSession,
    user_id: int
) -> User:
    query = select(User).where(User.id == user_id)
    async with session.begin():
        res = await session.execute(query)
    auth_user = res.fetchone()
# if call whis func user must be in db -> user_id from token 
    if auth_user is None:
        raise HTTPException(500, "Something went wrong")
    return auth_user[0]

async def update_user_password(
    session: AsyncSession,
    user_id: int,
    new_hashed_password: str
) -> int:
    query = update(User).values(password=new_hashed_password).returning(User.id)
    try:
        async with session.begin():
            res = await session.execute(query)
    except NoResultFound:
        raise HTTPException(500,
                        detail=f"Somthing went wrong")
    user_id = res.fetchone()
    return user_id[0]
            
async def create_refresh_token_in_db(
    user_id: int, 
    session: AsyncSession,
    exp: int,
    old_token: str | None
) -> RefreshToken:
    refresh_token: str = " "
# create new token != old token if it exist
    if old_token:
        while refresh_token == old_token or refresh_token == " ":
            refresh_token = create_random_string()
    else:
        refresh_token = create_random_string()
    query = (insert(RefreshToken).values(
            id=uuid4(),
            user_id=user_id,
            refresh_token=refresh_token,
            expires_at=exp).returning(RefreshToken))
    try:
        async with session.begin():
            res = await session.execute(query)
    except IntegrityError:
        raise HTTPException(500, f"something went wrong")
    
    refresh_token = res.fetchone()
    return refresh_token[0]

async def get_refresh_token(session: AsyncSession, refresh_token: str
) -> RefreshToken | None:
    query = (select(RefreshToken).where(
        RefreshToken.refresh_token== refresh_token))
    async with session.begin():
        res = await session.execute(query)
    refresh_data = res.fetchone()
    if refresh_data is not None:
        return refresh_data[0]
    return None

async def get_user_with_refresh_token(session: AsyncSession, user_id: int
) -> RefreshToken | None:
    query = (select(RefreshToken).where(RefreshToken.user_id == user_id))
    async with session.begin():
        res = await session.execute(query)
    user_data = res.fetchone()
    if user_data is not None:
        return user_data[0]
    return None
    
async def delete_refresh_token(session: AsyncSession, refresh_token_id: str
) -> None:
    query = (delete(RefreshToken).where(RefreshToken.id == refresh_token_id))
    
    try:
        async with session.begin():
            await session.execute(query)
    except IntegrityError:
        raise HTTPException(500, f"the user is not found")
    
# create random string to refresh_token
def create_random_string(lenght: int = 20) -> string:
    return ("".join(random.choices(FOOL_STRING, k=lenght)))

def create_refresh_cookie(refresh_token: str,) -> dict:
    base_cookie = {
        "key": "refreshToken",
        "value": refresh_token,
        "max_age": settings.REFRESH_TOKEN_MINUTS,
        "secure": True,
        "httponly": True,
    }
    return base_cookie