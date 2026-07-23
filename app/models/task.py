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
from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator


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


_MAX_TAGS = 10
_MAX_TAG_LENGTH = 30


def _validate_tags(tags: Optional[list[str]]) -> Optional[list[str]]:
    """
    Trim whitespace, reject empty/blank tags, enforce a max length per tag,
    de-duplicate (case-sensitive as written), and cap the total count.
    None means "not provided" (leave unchanged on update); an empty list
    means "clear all tags".
    """
    if tags is None:
        return None

    cleaned: list[str] = []
    for tag in tags:
        stripped = tag.strip()
        if not stripped:
            raise ValueError("tags must not be empty or whitespace-only")
        if len(stripped) > _MAX_TAG_LENGTH:
            raise ValueError(f"each tag must be {_MAX_TAG_LENGTH} characters or fewer")
        if stripped not in cleaned:
            cleaned.append(stripped)

    if len(cleaned) > _MAX_TAGS:
        raise ValueError(f"a task may have at most {_MAX_TAGS} tags")

    return cleaned


def _reject_explicit_none(value, field_name: str, hint: str = ""):
    """
    Shared guard for TaskUpdate fields where explicit `null` is invalid
    (unlike omission, which means "leave unchanged"). Extracted so the
    status/priority/tags validators don't each repeat the same None-check
    and error-message pattern.
    """
    if value is None:
        message = f"{field_name} cannot be explicitly set to null"
        if hint:
            message += f"; {hint}"
        raise ValueError(message)
    return value


class TaskCreate(BaseModel):
    """Request body for POST /tasks."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: Optional[str] = Field(default=None, max_length=100)
    due_date: Optional[date] = Field(default=None)
    tags: list[str] = Field(default_factory=list)

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        return _validate_title(v)

    @field_validator("tags")
    @classmethod
    def tags_valid(cls, v: list[str]) -> list[str]:
        return _validate_tags(v) or []


class TaskUpdate(BaseModel):
    """
    Request body for PATCH /tasks/{id}. All fields are optional in the sense
    that they may be *omitted* to mean "leave unchanged". However, once a
    field is included in the request at all, an explicit `null` is treated
    as invalid for title/status/priority/tags — none of these represent a
    valid "no value" state for an existing task. `description`, `assignee`,
    and `due_date` are true optional attributes, so explicit null is valid
    for those (it means "clear this field").

    Implementation note: Pydantic v2 field validators only run when a field
    is actually present in the request body, not when its default is used
    because the field was omitted. That is what lets us tell "omitted"
    (validator skipped, field silently ignored by exclude_unset) apart from
    "explicitly null" (validator runs and rejects it) using the same
    Optional[...] = None type.
    """

    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee: Optional[str] = Field(default=None, max_length=100)
    due_date: Optional[date] = Field(default=None)
    tags: Optional[list[str]] = Field(default=None)

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: Optional[str]) -> str:
        v = _reject_explicit_none(v, "title")
        return _validate_title(v)

    @field_validator("status")
    @classmethod
    def status_not_null(cls, v: Optional[TaskStatus]) -> TaskStatus:
        return _reject_explicit_none(v, "status")

    @field_validator("priority")
    @classmethod
    def priority_not_null(cls, v: Optional[TaskPriority]) -> TaskPriority:
        return _reject_explicit_none(v, "priority")

    @field_validator("tags")
    @classmethod
    def tags_valid(cls, v: Optional[list[str]]) -> list[str]:
        v = _reject_explicit_none(
            v, "tags", hint="send an empty list to clear tags"
        )
        return _validate_tags(v) or []


class TaskResponse(BaseModel):
    """Response model returned by all task endpoints."""

    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    description: Optional[str] = None
    status: TaskStatus
    priority: TaskPriority
    assignee: Optional[str] = None
    due_date: Optional[date] = None
    tags: list[str] = Field(default_factory=list)

    @computed_field  # type: ignore[misc]
    @property
    def is_overdue(self) -> bool:
        """
        Computed at read time (not stored), so it always reflects "today"
        rather than the date the task was created or last updated.
        A task with no due date, or one already Done, is never overdue.
        """
        if self.due_date is None or self.status == TaskStatus.DONE:
            return False
        return self.due_date < date.today()


def new_task_id() -> str:
    return str(uuid.uuid4())
