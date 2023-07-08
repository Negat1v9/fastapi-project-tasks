from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
class AccessToken(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: int
    
class VerifyUser(BaseModel):
    id: int
    hash_password: str

class RefreshData(BaseModel):
    id: UUID
    user_id: int
    refresh_token: str
    expires_at: datetime
    