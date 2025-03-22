from pydantic import BaseModel, EmailStr


class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    user_id: str
    email: EmailStr


class UserUpdateRequest(BaseModel):
    password: str | None
