from pydantic import BaseModel


class AccessTokenResponse(BaseModel):
    token_type: str = "Bearer"
    access_token: str
    expires_at: int


class JWTTokenPayload(BaseModel):
    iss: str
    sub: str
    exp: int
    iat: int


class JWTToken(BaseModel):
    payload: JWTTokenPayload
    access_token: str
