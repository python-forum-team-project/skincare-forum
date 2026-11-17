from pydantic import BaseModel, Field, EmailStr, StringConstraints, ConfigDict, field_validator
from typing import Literal, Annotated


class Role:
    USER = 'user'
    ADMIN = 'admin'
    MODERATOR = 'moderator'

USERNAME = Annotated[str,StringConstraints(min_length=2, max_length=16)]

class User(BaseModel):
    user_id: int
    username: USERNAME
    role_name: str
    is_blocked: bool

    def is_admin(self) -> bool:
        return self.role_name == Role.ADMIN

    @classmethod
    def from_query_result(cls, user_id, username, role_name, is_blocked):
        return cls(
            user_id=user_id,
            username=username,
            role_name=role_name,
            is_blocked=is_blocked
        )


class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    first_name: str = Field(min_length=2, max_length=32)
    last_name: str = Field(min_length=2, max_length=32)
    email: EmailStr
    username: USERNAME
    password: str = Field(min_length=8, max_length=128)

    @field_validator("first_name", "last_name", "username", mode="before")
    @classmethod
    def strip_spaces(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value


class UserProfile(User):
    first_name: str = Field(min_length=2, max_length=32)
    last_name: str = Field(min_length=2, max_length=32)
    email: EmailStr

    @classmethod
    def from_query_result(cls, user_id, username, role_name, is_blocked, first_name, last_name, email):
        return cls(
            user_id=user_id,
            username=username,
            role_name=role_name,
            is_blocked=is_blocked,
            first_name=first_name,
            last_name=last_name,
            email=email
        )


class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    first_name: str | None = Field(default=None, min_length=2, max_length=32)
    last_name: str | None = Field(default=None, min_length=2, max_length=32)
    email: EmailStr | None = None

    @field_validator("first_name", "last_name", mode="before")
    @classmethod
    def strip_spaces(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value

class LoginData(BaseModel):
    username: USERNAME
    password: str

    @field_validator("username", mode="before")
    @classmethod
    def strip_spaces(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value


class BlockUpdate(BaseModel):
    is_blocked: bool


class RoleUpdate(BaseModel):
    role_name: Literal['user', 'admin', 'moderator']