from pydantic import BaseModel
from datetime import datetime

from ..users.schemas import ShowUser

class GroupCreate(BaseModel):
    name: str | None
    
class ManagerGroupShow(BaseModel):
    id: int
    name: str | None
    manager_id: int
    
    class Config:
        orm_mode = True
        
class UserAddInGroup(BaseModel):
    user_id: int
    group_id: int
    
    class Config:
        orm_mode = True

class GroupTaskCreate(BaseModel):
    task: str
    group_id: int
    debtot_id: int | None = None
    
class UsersGroupResponse(BaseModel):
    user_id: int
    group: ManagerGroupShow
    
    class Config:
        orm_mode = True
        
class UserGroupAddTask(BaseModel):
    task: str
    group_id: int
    debtor_id: int | None = None

class UserGroupTaskRespone(UserGroupAddTask):
    id: int
    created_at: datetime
    owner_id: int
    
    class Config:
        orm_mode = True
        
class UserGroupEditTask(BaseModel):
    task_id: int
    task: str | None = None
    debtor_id: int | None = None
    
class UserGroupTasksResponse(BaseModel):
    task_id: int
    task: str
    created_at: datetime
    owner: ShowUser
    debtor: ShowUser | None
    
    class Config:
        orm_mode = True