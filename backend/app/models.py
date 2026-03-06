from typing import Optional

from pydantic import BaseModel, Field


class CreateTodo(BaseModel):
    """Payload for creating a Todo. Title is required."""

    title: str = Field(..., max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)


class UpdateTodo(BaseModel):
    """Payload for updating a Todo. All fields optional to allow partial updates."""

    title: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: Optional[bool] = None


class Todo(BaseModel):
    """Full Todo model returned by the API."""

    id: str
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: str
    updated_at: str
