from .config import settings
from .security import verify_user_password
from . import config
from app.auth.schemas import TokenData
from database.database import get_session
from .users.user_actions import _get_user_by_id, _get_user_by_email
from . users.schemas import ShowUser

from datetime import datetime, timedelta

from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from jose import jwt, JWTError


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def authenticate_user(email: str,
                            password: str,
                            session: AsyncSession
) -> str | HTTPException:
    current_user = await _get_user_by_email(email=email,
                                         session=session)
    if not verify_user_password(password, current_user.hash_password):
        raise HTTPException(status_code=403,
                            detail="Invalid Data")
    access_token = create_access_token({"user_id": current_user.id})
    return access_token


def create_access_token(data: dict) -> str:
    work_data = data.copy()
    
    expire = datetime.utcnow() + timedelta(
        minutes=config.settings.ACCESS_TOKEN_MINUTS
)   
    work_data.update({"exp": expire})
    
    encoded_token = jwt.encode(work_data,
                    settings.SECRET_KEY, settings.ALGORITHM
)
    return encoded_token
# decode access token return user
def verify_access_token(token: str) -> TokenData:
    critical_error = HTTPException(status_code=status.HTTP_401,
                        detail=f"Could not valided token")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY,
                                 settings.ALGORITHM)
        user_id = payload.get("user_id")
        if user_id is None:
            raise critical_error
        token_data = TokenData(id=user_id)
    except JWTError:
        raise critical_error
    return token_data

async def get_current_user(token: str = Depends(oauth2_scheme),
                           session: AsyncSession = Depends(get_session)
) -> TokenData:
    current_token = verify_access_token(token=token)
    current_user = await _get_user_by_id(user_id=current_token.id,
                                         session=session)
    return current_user
    