from database import user_crud
from app.users.schemas import UserCreate, ShowUser
from app.auth.schemas import VerifyUser
from .. import security

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException

async def _create_new_user(body: UserCreate, session: AsyncSession
) -> ShowUser:
    async with session.begin():
        db_user = user_crud.UserCrud(session=session)
        
        user = await db_user.insert_new_user(
            email=body.email,
            hash_password=security.hash_password(body.password),
        )
        return ShowUser(id=user.id,
                        email=user.email, 
                        is_active=user.is_active
                        )
async def _get_user_by_id(user_id: int, session: AsyncSession
) -> ShowUser | HTTPException:
    async with session.begin():
        db_user = user_crud.UserCrud(session=session)
        user = await db_user.select_user_by_id(user_id=user_id)
        if user is  None:
            raise HTTPException(status_code=404,
                    detail=f"user with id {user_id} is not found")
        return ShowUser(id=user.id,
                        email=user.email,
                        is_active=user.is_active,
)
async def _get_user_by_email(email: str, session: AsyncSession
) -> VerifyUser | HTTPException:
    async with session.begin():
        db_user = user_crud.UserCrud(session=session)
        current_user = await db_user.select_user_by_email(
            email=email,)
        if current_user is None:
            raise HTTPException(status_code=404,
                    detail=f"user is not found")
        return VerifyUser(id=current_user.id,
                          hash_password=current_user.password)
            

async def _delete_user(user_id: int, session: AsyncSession
) -> ShowUser | HTTPException:
    async with session.begin():
        db_user = user_crud.UserCrud(session=session)
        del_user = await db_user.delete_user(user_id=user_id)
        if del_user is None:
            raise HTTPException(status_code=404,
                    detail=f"user with id {user_id} is not found")
        return ShowUser(
                id=del_user.id,
                email=del_user.email,
                is_active=del_user.is_active
            )