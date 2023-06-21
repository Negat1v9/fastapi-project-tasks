from sqlalchemy import (select, insert, update, delete, and_)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from database.models import Mission
from .schemas import Task

# func for creating new taks
async def _create_task(session: AsyncSession, owner_id: int, **body: dict,
) -> Task:
    # add owner id to request
    body.update({"owner_id": owner_id})
    # creating query to add Task
    query = (insert(Mission).values(body).
            returning(Mission))
    # start session
    async with session.begin():
        res = await session.execute(query)
        await session.commit()
        
    new_task = res.fetchone()
    # if has problem with database
    if new_task is None:
        raise HTTPException(status_code=500,
            detail=f"server is not available right now")
    return new_task[0]

async def _get_all_task(session: AsyncSession, owner_id: int) -> list[Task]:
    query = (select(Mission)
            .where(Mission.owner_id == owner_id))
    async with session.begin():
        res = await session.execute(query)
        
    data: list[Task] = res.fetchall()
    # create list with Task objects
    if data is not None:
        tasks = [task[0] for task in data]
        return tasks
    # return empty list if tasks is None
    return []
# updating task if it not exist return exception
async def _update_task(session: AsyncSession, owner_id: int, **kwargs,
) -> Task:
    task_id = kwargs.pop("id")
    query = (update(Mission)
            .where(and_(Mission.id == task_id,
            Mission.owner_id == owner_id))
            .values(kwargs)
            .returning(Mission))
    async with session.begin():
        res = await session.execute(query)
        
    updated_task = res.fetchone()
    if updated_task is None:
        raise HTTPException(404,
                    detail=f"Task with id: {task_id} not found")
    return updated_task[0]
        
async def _delete_task(session: AsyncSession, task_id: int, owner_id: int
) -> int:
    query = (delete(Mission)
            .where(and_(Mission.id == task_id,
            Mission.owner_id == owner_id))
            .returning(Mission.id))
    async with session.begin():
        res = await session.execute(query)
        
    task_id = res.fetchone()
    if task_id is None:
        raise HTTPException(404,
                    detail=f"Task with id: {task_id} not found")
    return task_id[0]