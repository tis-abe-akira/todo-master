from typing import Optional

from pydantic import BaseModel


class CreateTodo(BaseModel):
    """Payload for creating a Todo. Title is required."""

    title: str
    description: Optional[str] = None


class UpdateTodo(BaseModel):
    """Payload for updating a Todo. All fields optional to allow partial updates."""

    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class Todo(BaseModel):
    """Full Todo model returned by the API."""

    id: str
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: str
    updated_at: str
