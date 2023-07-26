from sqlalchemy import select, and_, update, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from fastapi import HTTPException

from ..database.models import User
from app.users.schemas import ShowUser
from .. import security


async def _create_new_user(session: AsyncSession, **kwargs,
) -> User:
# get password from body
    simple_password = kwargs.pop("password")
# hash password and put it in Fool body
    kwargs.update({"password": security.hash_password(simple_password)})
    query = (insert(User).values(kwargs).returning(User))
    try:
        async with session.begin():
            #add in session new_user
           res = await session.execute(query)
    # catch errors with db
    except IntegrityError:
        raise HTTPException(500, "Server is not available")   
    new_user = res.fetchone()
    return new_user[0]
async def _get_user_by_id(user_id: int, session: AsyncSession
) -> ShowUser | HTTPException:
    # query to select user with id
    query = (select(User)
            .where(User.id == user_id))
    async with session.begin():
        data = await session.execute(query)
    # returning objects with rows User
    user = data.fetchone()
    if user is None:
        raise HTTPException(404,
                        detail=f"user is not found")
    current_user = user[0]
    return ShowUser(id=current_user.id,
                    first_name=current_user.first_name,
                    last_name=current_user.last_name,
                    email=current_user.email
                    )
async def _get_user_by_email(email: str, session: AsyncSession
) -> User:
    # select user with email for auth
    query = (select(User).where(and_(
        User.email == email, User.is_active == True)))
    async with session.begin():
        data = await session.execute(query)
       
    user = data.fetchone()
    if user is None:
        raise HTTPException(status_code=404,
                    detail=f"user is not found") 
    return user[0]
    
async def _update_user_by_email(
    session: AsyncSession,
    user_email: str,
    **kwargs,
) -> int:
    query = (update(User).values(kwargs).where(
        User.email == user_email).returning(User.id))
    try:
        async with session.begin():
            res = await session.execute(query)
    except IntegrityError:
        raise HTTPException(404, "No user")
    user_id = res.fetchone()
    return user_id[0]
    
async def _delete_user(user_id: int, session: AsyncSession
) -> ShowUser | HTTPException:
    query = (update(User)
            .where(and_(User.id == user_id, User.is_active == True))
            .values(is_active=False)
            .returning(User))
    async with session.begin():
        data = await session.execute(query)

    user: User = data.fetchone()    
    if user is None:
        raise HTTPException(status_code=404,
                    detail=f"user with id {user_id} is not found")
    del_user = user[0]
    return ShowUser(id=del_user.id,
                    first_name=del_user.first_name,
                    last_name=del_user.last_name,
                    email=del_user.email,)