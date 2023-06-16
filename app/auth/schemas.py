from pydantic import BaseModel

class AccessToken(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: int
    
class VerifyUser(BaseModel):
    id: int
    hash_password: str