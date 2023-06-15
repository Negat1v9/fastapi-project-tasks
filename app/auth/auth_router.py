from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession

from . import schemas
from ..oauth2 import authenticate_user
from database.database import get_session

auth_router = APIRouter(tags=["Authentication"])

@auth_router.post("/login")
async def login(user_credentails: OAuth2PasswordRequestForm = Depends(),
                session: AsyncSession = Depends(get_session)
) -> schemas.AccessToken:
    token = await authenticate_user(email=user_credentails.username,
                                     password=user_credentails.password,
                                     session=session)
    access_token = schemas.AccessToken(token=token,
                                       type="bearer")
    return access_token