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

# @router.post("/group/create", status_code=201,
#              response_model=ManagerGroupShow)
# async def create_group(group: GroupCreate,
#                        current_user: TokenData = Depends(get_current_user),
#                        session: AsyncSession = Depends(get_session),
# ):
#     # create group -> manager, group_id, name
#     current_group = await ma._create_group_users(session, current_user.id,
#                                                  group.name)
#     # add manager in group table
#     owner_in_group = await ma._add_user_in_group(session, current_user.id,
#                                                  current_group.id)
#     return current_group

# @router.post("/group/add/user", status_code=200, response_model=UserAddInGroup)
# async def add_group_user(body: UserAddInGroup,
#                         current_user: TokenData = Depends(get_current_user),
#                         session: AsyncSession = Depends(get_session)
# ) -> UserAddInGroup:
#     owner_group = await ma._get_group_by_id(session, body.group_id)
#     # check user is owner of group
#     if current_user.id != owner_group.manager_id:
#         raise HTTPException(404,
#                 detail=f"group with id {owner_group.id} not found")
#     # check user in database
#     user_in_db = await _get_user_by_id(body.user_id, session)
#     # add new user in group
#     new_user_in_group = await ma._add_user_in_group(session, user_in_db.id,
#                                                     owner_group.id,)
#     return new_user_in_group

# @router.delete("/group/drop/user", status_code=200)
# async def delete_user_from_group(del_user_id: int,
#                                  group_id: int,
#                                 current_user: TokenData = Depends(get_current_user),
#                                 session: AsyncSession = Depends(get_session)):
#     current_group = await ma._get_group_by_id(session, group_id)
#     # check user is owner group
#     if current_group.manager_id != current_user.id:
#          raise HTTPException(404,
#                 detail=f"group with id {current_group.id} not found")
#     delete_user = await ma._delete_user_from_group(session, del_user_id,
#                                                    current_group.id)
#     return {"status": "success", "message": "deleted"}

# @router.get("/group/user", status_code=200, response_model=list[UsersGroupResponse])
# async def get_all_users_group(current_user: TokenData = Depends(get_current_user),
#                               session: AsyncSession = Depends(get_session),
# ) -> list[UsersGroupResponse]:
#     users_group = await ma._get_all_user_group(session, current_user.id)
#     return users_group

# @router.post("/group/add/task", status_code=201,
#              response_model=UserGroupTaskRespone)
# async def create_group_task(body: UserGroupAddTask,
#                             current_user: TokenData = Depends(get_current_user),
#                             session: AsyncSession = Depends(get_session)):
#     # check user in group if not -> exception
#     user_in_group = await ma._get_user_from_group(session, current_user.id,
#                                                   body.group_id)
#     # create dict 
#     task = body.dict()
#     new_group_task = await ma._create_group_task(session, user_in_group.user_id,
#                                                  **task)
#     return new_group_task

# @router.get("/group/all/task", response_model=list[UserGroupTasksResponse])
# async def get_all_group_task(group_id : int,
#                             current_user: TokenData = Depends(get_current_user),
#                             session: AsyncSession = Depends(get_session)):
#     # check user in current group
#     user_in_group = await ma._get_user_from_group(session, current_user.id, group_id)
#     # select all tasks from group
#     group_task = await ma._get_all_group_task(session, user_in_group.group_id)
#     return group_task
    
# @router.patch("/group/edit/task", status_code=200,
#               response_model=UserGroupTaskRespone)
# async def edit_group_task(body: UserGroupEditTask,
#                           current_user: TokenData = Depends(get_current_user),
#                           session: AsyncSession = Depends(get_session)):
#     to_edit_task = body.dict()
#     # check user give task id
#     if to_edit_task["task_id"] is None:
#         raise HTTPException(400,
#                             detail=f"not transmitted task id")
#     task_id = to_edit_task.pop("task_id")
#     edited_task = await ma._edit_group_task(session, current_user.id,
#                                             task_id, **to_edit_task)
#     return edited_task
    
# @router.delete("/group/delete/task", status_code=200)
# async def delete_group_task(task_id: int,
#                             current_user: TokenData = Depends(get_current_user),
#                             session: AsyncSession = Depends(get_session)):
#     del_task_id = await ma._delete_group_task(session, current_user.id,
#                                               task_id)
#     return del_task_id