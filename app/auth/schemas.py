from pydantic import BaseModel

class AccessToken(BaseModel):
    token: str
    type: str

class TokenData(BaseModel):
    id: int
    
class VerifyUser(BaseModel):
    id: int
    hash_password: str