from fastapi import APIRouter, Depends
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.db import get_db
from app.core.dependencies import get_current_user
from app.core.security import get_hashed_password
from app.models import User
from app.schemas.user import UserResponse, UserUpdateRequest

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/account", response_model=UserResponse)
async def get_account(
        current_user: User = Depends(get_current_user),
) -> User:
    return current_user


@router.delete("/account", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db),
) -> None:
    await session.execute(delete(User).where(User.user_id == current_user.user_id))
    await session.commit()


@router.put("/account", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def update_account(
        user_in: UserUpdateRequest,
        session: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
) -> User:
    update_data = user_in.model_dump(exclude_unset=True)  # Only include provided fields

    if "password" in update_data:
        update_data["hashed_password"] = get_hashed_password(update_data.pop("password"))

    for key, value in update_data.items():
        setattr(current_user, key, value)

    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)

    return current_user
