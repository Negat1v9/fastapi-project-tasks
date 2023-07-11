from pydantic import BaseModel
from datetime import datetime


class TaskCreate(BaseModel):
    task: str
    
    
class Task(TaskCreate):
    id: int
    created_at: datetime
    owner_id: int
    
    class Config:
        orm_mode = True
        
class TaskUpdate(TaskCreate):
    id: int