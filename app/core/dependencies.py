from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.db import get_db
from app.core.security import verify_jwt_token
from app.models import User

oauth2_scheme = HTTPBearer()


async def get_current_user(
        token: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],
        session: AsyncSession = Depends(get_db),
) -> User:
    token_payload = verify_jwt_token(token.credentials)

    user = await session.scalar(select(User).where(User.user_id == token_payload.sub))

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    return user
