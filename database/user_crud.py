from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update


from . import models

class UserCrud:
    """Crud for User all operation with async"""
    
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session
    # method for creating new user
    async def insert_new_user(self, email, hash_password) -> models.User:
        # create new user
        new_user = models.User(email=email, 
                               password=hash_password,
                               )
        # add new user in database
        self.session.add(new_user)
        # flush user 
        await self.session.flush()
        return new_user
    # method for secect current user
    async def select_user_by_id(self, user_id: int) -> models.User | None:
        query = (select(models.User)
                .where(models.User.id == user_id))
        
        res = await self.session.execute(query)
        
        current_user = res.fetchone()
        if current_user is not None:
            return current_user[0]
        
    async def select_user_by_email(self, email: str) -> models.User | None:
        query = (select(models.User)
                .where(and_(models.User.email == email,
                models.User.is_active == True)))
        res = await self.session.execute(query)
        current_user = res.fetchone()
        if current_user is not None:
            return current_user[0]

    async def delete_user(self, user_id: int) -> models.User | None:
        query = (update(models.User)
                .where(and_(models.User.id == user_id,
                models.User.is_active == True))
                .values(is_active=False)
                .returning(models.User))
        
        res = await self.session.execute(query)
        deleted_user = res.fetchone()
        if deleted_user is not None:
            return deleted_user[0]
        
        
        
        
    