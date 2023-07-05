from fastapi import APIRouter, HTTPException, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from ..users.user_actions import _get_user_by_id
from ..database.database import get_session
from app.oauth2 import get_current_user
from app.auth.schemas import TokenData

from . import schemas as sh
from . import group_action as ga

router = APIRouter(prefix="/group", tags=["Group"])

@router.post("/create", status_code=201,
             response_model=sh.ManagerGroupShow)
async def create_group(group: sh.GroupCreate,
                       current_user: TokenData = Depends(get_current_user),
                       session: AsyncSession = Depends(get_session),
):
    # create group -> manager, group_id, name
    current_group = await ga._create_group_users(session, current_user.id,
                                                 group.name)
    # add manager in group table
    owner_in_group = await ga._add_user_in_group(session, current_user.id,
                                                 current_group.id)
    return current_group

@router.post("/add/user", status_code=200, response_model=sh.UserAddInGroup)
async def add_group_user(body: sh.UserAddInGroup,
                        current_user: TokenData = Depends(get_current_user),
                        session: AsyncSession = Depends(get_session)
) -> sh.UserAddInGroup:
    owner_group = await ga._get_group_by_id(session, body.group_id)
    # check user is owner of group
    if current_user.id != owner_group.manager_id:
        raise HTTPException(404,
                detail=f"group with id {owner_group.id} not found")
    # check user in database
    user_in_db = await _get_user_by_id(body.user_id, session)
    # add new user in group
    new_user_in_group = await ga._add_user_in_group(session, user_in_db.id,
                                                    owner_group.id,)
    return new_user_in_group

@router.delete("/drop/user", status_code=200)
async def delete_user_from_group(del_user_id: int,
                                 group_id: int,
                                current_user: TokenData = Depends(get_current_user),
                                session: AsyncSession = Depends(get_session)):
    current_group = await ga._get_group_by_id(session, group_id)
    # check user is owner group
    if current_group.manager_id != current_user.id:
         raise HTTPException(404,
                detail=f"group with id {current_group.id} not found")
    delete_user = await ga._delete_user_from_group(session, del_user_id,
                                                   current_group.id)
    return {"status": "success", "message": "deleted"}

@router.get("/user", status_code=200, response_model=list[sh.UsersGroupResponse])
async def get_all_users_group(current_user: TokenData = Depends(get_current_user),
                              session: AsyncSession = Depends(get_session),
) -> list[sh.UsersGroupResponse]:
    users_group = await ga._get_all_user_group(session, current_user.id)
    return users_group

@router.post("/add/task", status_code=201,
             response_model=sh.UserGroupTaskRespone)
async def create_group_task(body: sh.UserGroupAddTask,
                            current_user: TokenData = Depends(get_current_user),
                            session: AsyncSession = Depends(get_session)):
    # check user in group if not -> exception
    user_in_group = await ga._get_user_from_group(session, current_user.id,
                                                  body.group_id)
    # create dict 
    task = body.dict()
    new_group_task = await ga._create_group_task(session, user_in_group.user_id,
                                                 **task)
    return new_group_task

@router.get("/all/task", response_model=list[sh.UserGroupTasksResponse])
async def get_all_group_task(group_id : int,
                            current_user: TokenData = Depends(get_current_user),
                            session: AsyncSession = Depends(get_session)):
    # check user in current group
    user_in_group = await ga._get_user_from_group(session, current_user.id, group_id)
    # select all tasks from group
    group_task = await ga._get_all_group_task(session, user_in_group.group_id)
    return group_task
    
@router.patch("/edit/task", status_code=200,
              response_model=sh.UserGroupTaskRespone)
async def edit_group_task(body: sh.UserGroupEditTask,
                          current_user: TokenData = Depends(get_current_user),
                          session: AsyncSession = Depends(get_session)):
    to_edit_task = body.dict()
    # check user give task id
    if to_edit_task["task_id"] is None:
        raise HTTPException(400,
                            detail=f"not transmitted task id")
    task_id = to_edit_task.pop("task_id")
    edited_task = await ga._edit_group_task(session, current_user.id,
                                            task_id, **to_edit_task)
    return edited_task
    
@router.delete("/delete/task", status_code=200)
async def delete_group_task(task_id: int,
                            current_user: TokenData = Depends(get_current_user),
                            session: AsyncSession = Depends(get_session)):
    del_task_id = await ga._delete_group_task(session, current_user.id,
                                              task_id)
    return del_task_id