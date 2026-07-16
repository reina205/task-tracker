"""
Pydantic v2 models for the Task Tracker.

Design notes (Module 1-2 ADR decisions):
- In-memory storage only (no database yet).
- Status transitions are restricted: a task in Done cannot move back to
  ToDo or InProgress. This is enforced in the route layer (business rule),
  not in the model itself, because it depends on the *current* stored
  state, not just the incoming payload.
- extra="forbid" on all request models so unknown fields are rejected
  with 422 instead of silently ignored.
"""

import uuid
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TaskStatus(str, Enum):
    TODO = "ToDo"
    IN_PROGRESS = "InProgress"
    DONE = "Done"


class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


def _validate_title(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError("title must not be empty or whitespace-only")
    return stripped


class TaskCreate(BaseModel):
    """Request body for POST /tasks."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: Optional[str] = Field(default=None, max_length=100)

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        return _validate_title(v)


class TaskUpdate(BaseModel):
    """Request body for PATCH /tasks/{id}. All fields optional (partial update)."""

    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee: Optional[str] = Field(default=None, max_length=100)

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return _validate_title(v)


class TaskResponse(BaseModel):
    """Response model returned by all task endpoints."""

    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    description: Optional[str] = None
    status: TaskStatus
    priority: TaskPriority
    assignee: Optional[str] = None


def new_task_id() -> str:
    return str(uuid.uuid4())
