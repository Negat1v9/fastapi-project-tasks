from sqlalchemy import select, and_, update 
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException

from ..database.models import User
from app.users.schemas import UserCreate, ShowUser
from app.auth.schemas import VerifyUser
from .. import security


async def _create_new_user(body: UserCreate, session: AsyncSession
) -> ShowUser:
    # create model new user for insert password in model is hashed
    new_user = User(first_name=body.first_name,
                    last_name=body.last_name,
                    email=body.email,
                    password=security.hash_password( #hash password
                                    body.password))
    # open session 
    async with session.begin():
        #add in session new_user
        session.add(new_user)
        # flush session for new_user
        await session.flush()
       
        return ShowUser(id=new_user.id,
                        first_name=new_user.first_name,
                        last_name=new_user.last_name,
                        email=new_user.email,
                        )
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
) -> VerifyUser | HTTPException:
    # select user with email for auth
    query = (select(User).where(and_(
        User.email == email, User.is_active == True)))
    async with session.begin():
        data = await session.execute(query)
       
    user = data.fetchone()
    if user is None:
        raise HTTPException(status_code=404,
                    detail=f"user is not found")
    current_user = user[0]
    return VerifyUser(id=current_user.id,
                    hash_password=current_user.password
                    )
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