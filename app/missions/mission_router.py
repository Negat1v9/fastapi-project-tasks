from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import (Task, TaskCreate, TaskUpdate)
from . import mission_action as ma

from ..database.database import get_session
from app.oauth2 import get_current_user
from app.auth.schemas import TokenData

router = APIRouter(prefix="/task", tags=["Missions"])

@router.post("/", status_code=200, response_model=Task)
async def create_task(body: TaskCreate,
                    current_user: TokenData = Depends(get_current_user),
                    session: AsyncSession = Depends(get_session),
) -> Task:
    task = body.dict(exclude_none=True)
    if task == {}:
        raise HTTPException(403,
                            detail=f"The Request is Empty")
    created_task: Task = await ma._create_task(session=session,
                                               owner_id=current_user.id,
                                               **task)
    return created_task

@router.get("/", status_code=200, response_model=list[Task])
async def get_all_task(curent_user: TokenData = Depends(get_current_user),
                       session: AsyncSession = Depends(get_session)
):
    tasks: list[Task] = await ma._get_all_task(session=session, 
                                                    owner_id=curent_user.id)

    return tasks

@router.patch("/", status_code=200, response_model=Task)
async def update_task(body: TaskUpdate,
                      current_user: TokenData = Depends(get_current_user),
                      session: AsyncSession = Depends(get_session)
) -> Task:
    # body contain the id
    task = body.dict(exclude_none=True)
    if task == {}:
        raise HTTPException(403,
                            detail=f"the request field is empty")
    updated_task: Task = await ma._update_task(session=session,
                                               owner_id=current_user.id,
                                               **task)
    return updated_task

@router.delete("/", status_code=200)
async def delete_task(task_id: int, 
                      current_user: TokenData = Depends(get_current_user),
                      session: AsyncSession = Depends(get_session),
) -> int:
    if task_id is None:
        raise HTTPException(403,
                            detail=f"the request field is empty")
    deleted_task_id = await ma._delete_task(session, task_id, 
                                         current_user.id)
    return deleted_task_id