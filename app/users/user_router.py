from fastapi import APIRouter, Depends, status, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from . user_actions import (_create_new_user,
                              _get_user_by_id,
                              _delete_user,
                              _update_user)

from database.database import get_session

from . import schemas

router = APIRouter(prefix="/user", tags=["User"])

@router.post("/", status_code=201,
             response_model=schemas.ShowUser)
async def create_user(new_user: schemas.UserCreate, 
               session: AsyncSession = Depends(get_session),
) -> schemas.ShowUser:
    try:
        return await _create_new_user(body=new_user,
                                    session=session,)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Try it latter")
        
@router.get("/", status_code=200,
            response_model=schemas.ShowUser)
async def show_user_by_id(user_id: int,
                         session: AsyncSession = Depends(get_session),
) -> schemas.ShowUser:
    user = await _get_user_by_id(user_id=user_id,
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
    user_for_deletetion = await _get_user_by_id(user_id=user_id,
                                                session=session)
    if user_for_deletetion is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"user with id {user_id} not found",
        )
    del_user = await _delete_user(user_id=user_id, session=session)
    if del_user is None:
        raise HTTPException(status_code=status.HTTP_404,
                        detail=f"user with id {user_id} not found",
        )
    return del_user

@router.patch("/", status_code=200,
              response_model=schemas.ShowUser)
async def update_user(user_id: int,
                      body: schemas.UpdateUserRequest,
                      session: AsyncSession = Depends(get_session)
) -> schemas.ShowUser:
    user_for_update = await _get_user_by_id(user_id=user_id,
                                            session=session,)
    if user_for_update is None:
        raise HTTPException(status_code=status.HTTP_404,
                        detail=f"user with id {user_id} not found",
        )
    updation_data = body.dict(exclude_none=True)
    if updation_data == {}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"The field with updated data cannot be None",)
    updated_user = await _update_user(new_user_params=updation_data,
                                      user_id=user_id,
                                      session=session,)
    return updated_user