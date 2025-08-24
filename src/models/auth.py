import re
from pydantic import BaseModel, ConfigDict, field_validator
from src.exc.auth import InvalidEmail, PasswordTooShort, EmailTooLong, PasswordTooLong


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
