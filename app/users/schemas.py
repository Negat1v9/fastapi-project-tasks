from pydantic import BaseModel, EmailStr, validator

from fastapi import HTTPException

BAD_SYMBOL = set("!~`@#$%^&*()_+{}[]")

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    
    @validator("first_name") # is valid first_name
    def valid_f_name(cls, first_name: str):
        # first_name = first_name.strip()
        if not all((w not in BAD_SYMBOL) for w in first_name):
            raise HTTPException(status_code=422,
                    detail=f"First name must contain only letters")
        return first_name
    @validator("last_name") # is valid last name
    def valid_l_name(cls, last_name: str):
        last_name = last_name.strip()
        if not all((w not in BAD_SYMBOL) for w in last_name):
            raise HTTPException(status_code=422,
                    detail=f"Last name must contain only letters")
        return last_name
    @validator("password") # is valid password
    def check(cls, value):
        if len(value) < 8:
            raise HTTPException(status_code=422,
                    detail=f"the password must contain at least 8 characters")
        return value
class ShowUser(BaseModel):
    id: int
    first_name: str
    last_name: str
    
    class Config:
        orm_mode = True

