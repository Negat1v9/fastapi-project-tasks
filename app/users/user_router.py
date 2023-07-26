from fastapi import APIRouter, Depends, status, HTTPException, Request, Body

from redis.asyncio import Redis

from sqlalchemy.ext.asyncio import AsyncSession
from . import user_actions as ua
from ..database.database import get_session
from .. database import redis
from app.oauth2 import get_current_user
from app.auth.schemas import TokenData
from .. auth.auth_actions import create_random_string
from .. tasks import email_sender as es
from . import schemas

router = APIRouter(prefix="/user", tags=["User"])

@router.post("/", status_code=201, response_model=schemas.ShowUser)
async def create_user(new_user: schemas.UserCreate,
                      request: Request,
                      redis_client: Redis = Depends(redis.get_redis_client),
                      session: AsyncSession = Depends(get_session),
) -> schemas.ShowUser:
# check user not in db or He is not confirmed
    user_is_confirmed: bool = True # flag to confirm email
    try:
# check user in db
        user_from_db = await ua._get_user_by_email(new_user.email, session)
# if user not in db create him exception from func _get_user_by_email()
    except HTTPException:
        new_user_in_db = await ua._create_new_user(session, **new_user.dict())
        user_is_confirmed = False
# Exception if user exist and he is confirmed
    else:
        if user_from_db.is_confirmed:
            raise HTTPException(422, "User alredy exixst")
# create final of url to confirmed
    secret_link: str = create_random_string(15)
# generate url for confirm email user
    url_for_confirm = str(
        request.url_for("confirm_user_email", secret_link=secret_link))
# add user email in redis
    await redis.add_value(redis_client, secret_link, new_user.email)
# add task in celery to send email
    es.send_confirm_email.delay(new_user.email, url_for_confirm, new_user.last_name)
# return user_without confirm if He was in db or return new user
    return new_user_in_db if not user_is_confirmed else user_from_db
        
@router.get("/", status_code=200,
            response_model=schemas.ShowUser)
async def show_user_by_id(user_id: int,
                         session: AsyncSession = Depends(get_session),
                         current_user: TokenData = Depends(get_current_user),
) -> schemas.ShowUser:
    user = await ua._get_user_by_id(user_id=user_id,
                                session=session,)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"user with id: {user_id} not found"
        )
    return user

@router.delete("/", status_code=200, 
               response_model=schemas.ShowUser)
async def delete_user(user_id: int,
                      session: AsyncSession = Depends(get_session)
) -> schemas.ShowUser:
    user_for_deletetion = await ua._get_user_by_id(user_id=user_id,
                                                session=session)
    if user_for_deletetion is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"user with id {user_id} not found",
        )
    del_user = await ua._delete_user(user_id=user_id, session=session)
    if del_user is None:
        raise HTTPException(status_code=status.HTTP_404,
                        detail=f"user with id {user_id} not found",
        )
    return del_user

@router.get("/confirm/{secret_link}")
async def confirm_user_email(secret_link: str,
                             session: AsyncSession = Depends(get_session),
                             redis_client: Redis = Depends(redis.get_redis_client)
) -> None:
# get user email from redis
    user_email = await redis.get_and_del_by_key(redis_client, secret_link)
# if not user in db
    if user_email is None:
        raise HTTPException(404, "No user found")
# is_confirmed -> True
    user_id = await ua._update_user_by_email(session, user_email, **{"is_confirmed": True})
    return {"status": "success",
            "message": "Email has been successfully confirmed"}