"""
CRUD routes for tasks.

Business rule (Module 1/2): a task in Done status cannot move back to
ToDo or InProgress. This is a state-transition rule, not a field-value
rule, so it is checked here against the currently stored task rather
than in the Pydantic model.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.models.task import (
    TaskCreate,
    TaskPriority,
    TaskResponse,
    TaskStatus,
    TaskUpdate,
    new_task_id,
)
from app.storage.memory import storage

router = APIRouter(prefix="/tasks", tags=["tasks"])

# Statuses that Done is not allowed to move back to.
_ILLEGAL_FROM_DONE = {TaskStatus.TODO, TaskStatus.IN_PROGRESS}


def _get_or_404(task_id: str) -> TaskResponse:
    task = storage.get(task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate) -> TaskResponse:
    task = TaskResponse(id=new_task_id(), **payload.model_dump())
    return storage.create(task)


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    status_filter: Optional[TaskStatus] = Query(default=None, alias="status"),
    priority: Optional[TaskPriority] = Query(default=None),
    overdue: Optional[bool] = Query(default=None),
    tag: Optional[str] = Query(default=None),
) -> list[TaskResponse]:
    tasks = storage.list()
    if status_filter is not None:
        tasks = [t for t in tasks if t.status == status_filter]
    if priority is not None:
        tasks = [t for t in tasks if t.priority == priority]
    if overdue is not None:
        tasks = [t for t in tasks if t.is_overdue == overdue]
    if tag is not None:
        tasks = [t for t in tasks if tag in t.tags]
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: str) -> TaskResponse:
    return _get_or_404(task_id)


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
    existing = _get_or_404(task_id)

    updates = payload.model_dump(exclude_unset=True)

    if "status" in updates:
        new_status = updates["status"]
        if existing.status == TaskStatus.DONE and new_status in _ILLEGAL_FROM_DONE:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="A task in Done cannot move back to ToDo or InProgress",
            )

    updated = existing.model_copy(update=updates)
    return storage.update(task_id, updated)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str) -> None:
    _get_or_404(task_id)
    storage.delete(task_id)
