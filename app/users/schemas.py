from pydantic import BaseModel, EmailStr, validator

from fastapi import HTTPException, status

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    
    @validator("password")
    def check(cls, value):
        if len(value) < 8:
            raise HTTPException(status_code=422,
                    detail=f"the password must contain at least 8 characters")
        return value
class ShowUser(BaseModel):
    id: int
    email: str
    is_active: bool
    
    class Config:
        orm_mode = True

class UpdateUserRequest(BaseModel):
    email: EmailStr | None

