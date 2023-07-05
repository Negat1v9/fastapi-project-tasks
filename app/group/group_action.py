from sqlalchemy import (select, insert, update, delete, and_)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import aliased
from fastapi import HTTPException

from ..database.models import (ManagerGroup, GeneralMiss, UserGroup, User)

from .schemas import UsersGroupResponse, UserGroupTasksResponse
# create new group with manager 
async def _create_group_users(session: AsyncSession, user_id: int,
                              group_name: str | None = None) -> ManagerGroup:
    # crate manager group
    query_in_managers = (insert(ManagerGroup).values(
            name=group_name, manager_id=user_id)
            .returning(ManagerGroup))
    async with session.begin():
        res = await session.execute(query_in_managers)

    group = res.fetchone()
    return group[0]

# select group by id after check user is owner this
async def _get_group_by_id(session: AsyncSession, group_id,
) -> ManagerGroup:
    query = select(ManagerGroup).where(ManagerGroup.id == group_id)
    async with session.begin():
        res = await session.execute(query)
    group = res.fetchone()
    if group is None:
        raise HTTPException(404,
                detail=f"the group with id: {group_id} does not exist")
    return group[0]

async def _add_user_in_group(session: AsyncSession, user_id: int,
                             group_id: int
) -> UserGroup:
    query = (insert(UserGroup)
            .values(group_id=group_id, user_id=user_id)
            .returning(UserGroup))
# catch exception user in group
    try:
        async with session.begin():
            res = await session.execute(query)
    except IntegrityError:
        raise HTTPException(409,
                detail=f"user is already in group")
        
    user_group = res.fetchone()
    if user_group is None:
        raise HTTPException(500,
                            detail=f"server error")
    return user_group[0]

async def _delete_user_from_group(session: AsyncSession, user_id: int, group_id: int
) -> UserGroup:
    query = (delete(UserGroup).where(
            and_(UserGroup.user_id == user_id, UserGroup.group_id == group_id))
            .returning(UserGroup))
# try delete user, catch exception user not in group
    try:
        async with session.begin():
            res = await session.execute(query)
    except NoResultFound:
        raise HTTPException(404,
                detail=f"user with id {user_id} not in this group")
        
    delete_user = res.fetchone()
    return delete_user[0]
# select user from his group 
async def _get_user_from_group(session: AsyncSession, user_id: int, group_id: int
) -> UserGroup:
    query = (select(UserGroup)
            .where(and_(UserGroup.user_id == user_id, 
                        UserGroup.group_id == group_id)))
    async with session.begin():
        res = await session.execute(query)
    user_fr_group = res.fetchone()
    if user_fr_group is None:
        raise HTTPException(404,
                    detail=f"user with id {user_id} not in group")
    return user_fr_group[0]

async def _get_all_user_group(session: AsyncSession ,user_id: int
) -> list[UsersGroupResponse]:
    group = aliased(ManagerGroup, name="group")
    query = (select(UserGroup.user_id, group)
            .join(group, UserGroup.group_id == group.id)
            .where(UserGroup.user_id == user_id))

    async with session.begin():
        res = await session.execute(query)
        
    users_group = res.fetchall()
    if users_group is not None:
        return users_group
    return []

async def _create_group_task(session: AsyncSession, owner_id: int, **kwargs,
) -> GeneralMiss:
# add owner id in data
    kwargs.update({"owner_id": owner_id})
    query = (insert(GeneralMiss).values(kwargs).returning(GeneralMiss))
    async with session.begin():
        res = await session.execute(query)
    group_task = res.fetchone()
    if group_task is None:
        raise HTTPException(500,
                    detail=f"the server is not responding now")
    return group_task[0]

async def _get_all_group_task(session: AsyncSession, group_id: int
) -> list[UserGroupTasksResponse]:
    owner = aliased(User, name="owner")
    debtor = aliased(User, name="debtor")

# query to select all groups tasks with foreign params
    query = (select(GeneralMiss.id.label("task_id"), GeneralMiss.task, 
                    GeneralMiss.created_at , owner, debtor)
        .join(owner, owner.id == GeneralMiss.owner_id)
        .join(debtor, GeneralMiss.debtor_id == debtor.id, isouter=True)
        .where(and_(GeneralMiss.group_id == group_id)))
    async with session.begin():
        res = await session.execute(query)
    groups_tasks = res.fetchall()
    if groups_tasks is not None:
        return groups_tasks
    return []
    
async def _edit_group_task(session: AsyncSession, owner_id: int, task_id,
                           **kwargs) -> GeneralMiss:
# dont need checking user in group -> user cant be owner it task id
    query = (update(GeneralMiss).where(and_(
            GeneralMiss.id == task_id, GeneralMiss.owner_id == owner_id))
            .values(kwargs).returning(GeneralMiss))
    try:
        async with session.begin():
            res = await session.execute(query)
    except NoResultFound:
        raise HTTPException(404, detail=f"task not found")
    
    edit_task = res.fetchone()
    return edit_task[0]

async def _delete_group_task(session: AsyncSession, owner_id, task_id
) -> int:
    query = (delete(GeneralMiss)
            .where(and_(
            GeneralMiss.id == task_id, GeneralMiss.owner_id == owner_id))
            .returning(GeneralMiss.id))
    try:
        async with session.begin():
            res = await session.execute(query)
    except NoResultFound:
        raise HTTPException(404,
                        detail=f"task is not found")
    del_task_id = res.fetchone()
    return del_task_id[0]