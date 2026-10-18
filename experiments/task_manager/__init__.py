"""Console task manager.

Package that contains the task-management logic and the command-line
interface used to operate on tasks.
"""

from .task_manager import Task, TaskManager, TaskNotFoundError

__all__ = ["Task", "TaskManager", "TaskNotFoundError"]
