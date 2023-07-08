from .config import settings
from .security import verify_user_password, hash_password
from . import config
from app.auth.schemas import TokenData, RefreshData
from . database.database import get_session
from . database.models import User
from .users.user_actions import _get_user_by_email
from . auth import auth_actions as aa

from datetime import datetime, timedelta

from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status, Depends, Cookie
from sqlalchemy.ext.asyncio import AsyncSession

from jose import jwt, JWTError


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# authenticate user -> create 2 tokens and verify password
async def authenticate_user(email: str, password: str, session: AsyncSession,
                            user_id: int | None = None
) -> dict | HTTPException:
# if authentificate user get user id from db else it from request
    if not user_id:
        current_user = await _get_user_by_email(email=email, session=session)
# ckeck user password
        if not verify_user_password(password, current_user.hash_password):
            raise HTTPException(status_code=403,
                                detail="Invalid Data")
        user_id = current_user.id # user id = user id from db
# create access token with payload user inside
    access_token = create_access_token(user_id)
# check user have`t refresh token
    user_with_refresh = await aa.get_user_with_refresh_token(
        session, user_id)
# if user alredy have refresh -> delete it from db and create new
    old_refresh_token = None
    if user_with_refresh:
        await aa.delete_refresh_token(session, user_with_refresh.id)
# if user alredy had token -> create 100% another token
        old_refresh_token = user_with_refresh.refresh_token
# create new token 
    refresh_token_data: dict = await create_refresh_token(
                                        user_id, 
                                        session,
                                        old_refresh_token)
                    
    return {"access_token": access_token,
            "refresh_token": refresh_token_data["token"],
            "refresh_exp": refresh_token_data["exp"]}

# create access token with payload
def create_access_token(user_id: int) -> str:
    
    expire = datetime.utcnow() + timedelta(
        minutes=config.settings.ACCESS_TOKEN_MINUTS)   
    
    work_data: dict = {"user_id": user_id,
                       "exp": expire,
                       }
    
    encoded_token = jwt.encode(work_data,
                    settings.SECRET_KEY, settings.ALGORITHM
)
    return encoded_token

async def create_refresh_token(user_id: int,
                         session: AsyncSession,
                         old_token: str | None,
                         life_time: int = settings.REFRESH_TOKEN_MINUTS,
) -> dict:
    # time life token
    exp = datetime.utcnow()+timedelta(minutes=life_time)
    refresh_token = await aa.create_refresh_token_in_db(user_id, session,
                                                     exp, old_token)
    
    return {"token": refresh_token.refresh_token,
            "exp": exp}
    
# decode access token return user
def verify_access_token(token: str) -> TokenData:
    critical_error = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
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
    
async def valid_refresh_token(session: AsyncSession = Depends(get_session),
                              refresh_token: str = Cookie(alias="refreshToken")
) -> RefreshData | HTTPException:
    
    exception_auth = HTTPException(401, detail="User not authenticated")
# get token from db
    current_refresh_token = await aa.get_refresh_token(session, refresh_token)
# if user have`t refresh token
    if not current_refresh_token:
        raise exception_auth
# if token is expired
    if not is_valid_refresh_token(current_refresh_token.expires_at):
        raise exception_auth
    return RefreshData(
        id=current_refresh_token.id,
        user_id=current_refresh_token.user_id,
        refresh_token=current_refresh_token.refresh_token,
        expires_at=current_refresh_token.expires_at)
    
def create_new_password(current_password, 
                        current_hashed_pasword, 
                        new_password: str,
) -> str:
    # 
    if not verify_user_password(current_password, current_hashed_pasword):
        raise HTTPException(400,
            detail=f"Invalid Data")
    # if new password as old -> exception
    if verify_user_password(new_password, current_hashed_pasword):
        raise HTTPException(400,
            detail=f"New password should be different that current password")
        
    new_hash_password = hash_password(new_password)
    return new_hash_password

# function for geting user from token
async def get_current_user(token: str = Depends(oauth2_scheme),
                           session: AsyncSession = Depends(get_session)
) -> User:
    current_token = verify_access_token(token=token)
    current_user = await aa.get_user_by_id_to_auth(
        session, current_token.id)
    return current_user
    
def is_valid_refresh_token(refresh_token_exp: int) -> bool:
    return datetime.utcnow() <= refresh_token_exp