import time

import bcrypt
import jwt
from fastapi import HTTPException, status

from app.core.config import get_settings
from app.schemas.auth import JWTToken, JWTTokenPayload

### PASSWORD ###


def verify_password(hashed_password: str, password: str) -> bool:
    """
    Verifies a password against the stored hash.
    Returns True if the password is correct, otherwise False.
    """
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def get_hashed_password(password: str) -> str:
    """
    Hashes the password using bcrypt.
    Returns the hashed password.
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


### JWT ###


def create_jwt_token(user_id: str) -> JWTToken:
    settings = get_settings()
    iat = int(time.time())
    exp = iat + settings.JWT_EXPIRES_SECONDS

    token_payload = JWTTokenPayload(
        iss=settings.JWT_ISSUER,
        sub=user_id,
        exp=exp,
        iat=iat,
    )

    access_token = jwt.encode(
        token_payload.model_dump(),
        key=settings.JWT_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM,
    )

    return JWTToken(payload=token_payload, access_token=access_token)


def verify_jwt_token(token: str) -> JWTTokenPayload:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.JWT_KEY.get_secret_value(),
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_signature": True},
            issuer=settings.JWT_ISSUER,
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token invalid: {e}",
        )

    return JWTTokenPayload(**payload)
