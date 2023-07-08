from fastapi import APIRouter, Depends, Response, Body
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession

from . import schemas
from .. import oauth2 as oa
from .auth_actions import delete_refresh_token, create_refresh_cookie,\
    update_user_password
from ..database.database import get_session
from .. database.models import User

auth_router = APIRouter(tags=["Authentication"])

@auth_router.post("/login")
async def login(response: Response,
                user_credentails: OAuth2PasswordRequestForm = Depends(),
                session: AsyncSession = Depends(get_session),
                
) -> schemas.AccessToken:
    tokens: dict = await oa.authenticate_user(email=user_credentails.username,
                                     password=user_credentails.password,
                                     session=session)
    access_token = schemas.AccessToken(access_token=tokens["access_token"],
                                       token_type="bearer")
    # set cockie with refresh token
    response.set_cookie(**create_refresh_cookie(tokens["refresh_token"]))
    
    return access_token
# create new access token with refresh token
@auth_router.put("/login")
async def create_new_access_token(
    response: Response,
    refresh_token = Depends(oa.valid_refresh_token),
    session: AsyncSession = Depends(get_session),
) -> schemas.AccessToken:
# delete old refresh token
    await delete_refresh_token(session, refresh_token.id)
    # create new refresh token and save it in db
    new_refrech_token: dict = await oa.create_refresh_token(
        refresh_token.user_id, session,
        old_token=refresh_token.refresh_token)
    
    # create new access token with data from refresk token
    new_access_token: str = oa.create_access_token(refresh_token.user_id)
    # creaet cookie with refresh token
    
    response.set_cookie(**create_refresh_cookie(new_refrech_token["token"]))
    
    return schemas.AccessToken(access_token=new_access_token,
                               token_type="bearer")
    
@auth_router.post("/change/password")
async def change_user_password(response: Response,
                               current_password: str = Body(),
                               new_password: str = Body(),
                               current_user: User = Depends(oa.get_current_user),
                               session: AsyncSession = Depends(get_session)
) -> schemas.AccessToken:
    new_hashed_password: str = oa.create_new_password(current_password,
                                                 current_user.password,
                                                 new_password)
    user_id: int = await update_user_password(session,
                                              current_user.id,
                                              new_hashed_password)
# put here current password to check is valid it
    tokens = await oa.authenticate_user(current_user.email,current_password,
                                        session, auth_by_id=True,
                                        user_id=user_id)
    response.set_cookie(**create_refresh_cookie(tokens["refresh_token"]))
    response.init_headers()
    return schemas.AccessToken(
        access_token=tokens["access_token"],
        token_type="bearer")