import uuid
from pydantic import BaseModel, ConfigDict, field_validator, Field
from datetime import datetime


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
