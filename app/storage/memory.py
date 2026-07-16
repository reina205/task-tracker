"""
In-memory storage for tasks.

Kept intentionally simple (a dict keyed by id) per the Module 1 ADR.
A single module-level instance is used as the app's storage, and tests
reset it via an autouse fixture in conftest.py so tests do not leak
state into each other.
"""

from typing import Dict, Optional

from app.models.task import TaskResponse


class TaskStorage:
    def __init__(self) -> None:
        self._tasks: Dict[str, TaskResponse] = {}

    def reset(self) -> None:
        self._tasks.clear()

    def create(self, task: TaskResponse) -> TaskResponse:
        self._tasks[task.id] = task
        return task

    def get(self, task_id: str) -> Optional[TaskResponse]:
        return self._tasks.get(task_id)

    def list(self) -> list[TaskResponse]:
        return list(self._tasks.values())

    def update(self, task_id: str, task: TaskResponse) -> TaskResponse:
        self._tasks[task_id] = task
        return task

    def delete(self, task_id: str) -> bool:
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False


# Single shared instance used by the app and imported by tests.
storage = TaskStorage()
