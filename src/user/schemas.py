from uuid import UUID

from pydantic import BaseModel, Field


class CurrentUserSchema(BaseModel):
    id: UUID
    full_name: str
    username: str
    active: bool

    class Config:
        from_attributes = True


class CreateUser(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=20)
    username: str
    password: str


class UserLoginSchema(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: UUID
    username: str

    class Config:
        from_attributes = True


class AccessTokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class RefreshTokenSchema(BaseModel):
    refresh_token: str
