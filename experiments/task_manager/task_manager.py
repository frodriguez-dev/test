"""Task-management logic with JSON persistence.

This module implements :class:`TaskManager`, which manages a collection of
personal tasks and persists them automatically to a JSON file. It uses no
external dependencies: only the Python standard library.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


class TaskNotFoundError(Exception):
    """Raised when a nonexistent task ID is referenced."""

    def __init__(self, task_id: int) -> None:
        self.task_id = task_id
        super().__init__(f"No task found with ID {task_id}.")


@dataclass
class Task:
    """Represents a single task."""

    id: int
    title: str
    description: str = ""
    completed: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Return the task as a serializable dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Task":
        """Build a task from a dictionary."""
        return cls(
            id=int(data["id"]),
            title=str(data["title"]),
            description=str(data.get("description", "")),
            completed=bool(data.get("completed", False)),
        )


@dataclass
class TaskManager:
    """Manage tasks and persist them to a JSON file.

    Every operation that modifies state (create, complete, or delete)
    automatically saves the changes to disk.
    """

    storage_path: Path = field(default_factory=lambda: Path("tasks.json"))
    tasks: list[Task] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.storage_path = Path(self.storage_path)
        self.load()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def load(self) -> None:
        """Load tasks from the JSON file, if it exists."""
        if not self.storage_path.exists():
            self.tasks = []
            return

        raw = self.storage_path.read_text(encoding="utf-8").strip()
        if not raw:
            self.tasks = []
            return

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"File {self.storage_path} does not contain valid JSON: {exc}"
            ) from exc

        if not isinstance(data, list):
            raise ValueError(
                f"File {self.storage_path} must contain a list of tasks."
            )

        self.tasks = [Task.from_dict(item) for item in data]

    def save(self) -> None:
        """Write the current tasks to the JSON file."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = [task.to_dict() for task in self.tasks]
        self.storage_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    # ------------------------------------------------------------------
    # Operations
    # ------------------------------------------------------------------
    def _next_id(self) -> int:
        return max((task.id for task in self.tasks), default=0) + 1

    def add_task(self, title: str, description: str = "") -> Task:
        """Create a new task and persist it.

        Args:
            title: Task title. It cannot be empty.
            description: Optional description.

        Returns:
            The created task.
        """
        title = title.strip()
        if not title:
            raise ValueError("Task title cannot be empty.")

        task = Task(id=self._next_id(), title=title, description=description.strip())
        self.tasks.append(task)
        self.save()
        return task

    def list_tasks(self) -> list[Task]:
        """Return all tasks sorted by ID."""
        return sorted(self.tasks, key=lambda task: task.id)

    def get_task(self, task_id: int) -> Task:
        """Look up a task by its ID.

        Raises:
            TaskNotFoundError: if no task with that ID exists.
        """
        for task in self.tasks:
            if task.id == task_id:
                return task
        raise TaskNotFoundError(task_id)

    def complete_task(self, task_id: int) -> Task:
        """Mark a task as completed and persist the change."""
        task = self.get_task(task_id)
        task.completed = True
        self.save()
        return task

    def delete_task(self, task_id: int) -> Task:
        """Delete a task and persist the change."""
        task = self.get_task(task_id)
        self.tasks.remove(task)
        self.save()
        return task
