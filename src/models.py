import uuid
from pydantic import BaseModel, ConfigDict, field_validator, Field
from datetime import datetime

# Errors and models should be divided into
# their respective files

class NameLength(ValueError):
    pass


class InvalidDateFormat(ValueError):
    pass


class CreateTask(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=True)
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task: str
    info: str
    deadline: str

    @field_validator("task", mode="before")
    @classmethod
    def validate_name_length(cls, v: str):
        if len(v) > 79:
            raise NameLength("Task name must be under 79 characters.")
        return v

    @field_validator("deadline", mode="before")
    @classmethod
    def validate_due_format(cls, v: str):
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise InvalidDateFormat("Due date must be in YYYY-MM-DD format.")
        return v


class UpdateTask(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=True)
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task: str
    info: str
    deadline: str

    @field_validator("task", mode="before")
    @classmethod
    def validate_task_name_length(cls, v: str):
        if len(v) > 79:
            raise NameLength("Task name must be under 79 characters.")
        return v

    @field_validator("deadline", mode="before")
    @classmethod
    def validate_due_format(cls, v: str):
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise InvalidDateFormat("Due date must be in YYYY-MM-DD format.")
        return v


import re
from pydantic import BaseModel, ConfigDict, field_validator
from src.exc.excs import InvalidEmail, PasswordTooShort, EmailTooLong, PasswordTooLong


class UserRegister(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=True)
    email: str
    password: str

    @field_validator("email", mode="after")
    @classmethod
    def validate_email_format(cls, v: str | str) -> str:
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", v):
            raise InvalidEmail("Invalid email format")
        if len(v) > 254:
            raise EmailTooLong("Email must be under 255 characters.")
        return str(v)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise PasswordTooShort("Password must be 8 characters or longer.")
        if len(v) > 254:
            raise PasswordTooLong("Password must be under 255 characters.")
        return v


class UserLogin(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=True)
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        if "@" not in v:
            raise InvalidEmail("Invalid email format")
        return v
