from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core import db
from app.core.security import verify_password, create_jwt_token, get_hashed_password
from app.models.user import User
from app.schemas.auth import AccessTokenResponse
from app.schemas.user import UserResponse, UserCreateRequest

router = APIRouter(tags=["Authentication"])


@router.post("/login", response_model=AccessTokenResponse)
async def login(
        session: AsyncSession = Depends(db.get_db),
        data: OAuth2PasswordRequestForm = Depends(),
) -> AccessTokenResponse:
    user = await session.scalar(select(User).where(User.email == data.username))

    if not verify_password(user.hashed_password, data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid username or password",
        )

    jwt_token = create_jwt_token(user_id=user.user_id)

    return AccessTokenResponse(
        access_token=jwt_token.access_token,
        expires_at=jwt_token.payload.exp,
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
        user_in: UserCreateRequest,
        session: AsyncSession = Depends(db.get_db),
) -> User:
    user = await session.scalar(select(User).where(User.email == user_in.email))
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = User(
        email=user_in.email,
        hashed_password=get_hashed_password(user_in.password),
    )
    session.add(user)
    await session.commit()
    return user
