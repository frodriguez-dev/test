"""Command-line interface for the task manager.

Usage::

    python -m experiments.task_manager add "Buy bread" --description "Whole wheat"
    python -m experiments.task_manager list
    python -m experiments.task_manager complete 1
    python -m experiments.task_manager delete 1
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .task_manager import Task, TaskManager, TaskNotFoundError

DEFAULT_STORAGE = Path("tasks.json")


def _format_task(task: Task) -> str:
    status = "[x]" if task.completed else "[ ]"
    line = f"{task.id:>3} {status} {task.title}"
    if task.description:
        line += f"  ({task.description})"
    return line


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="task-manager",
        description="Console task manager with JSON persistence.",
    )
    parser.add_argument(
        "--file",
        default=str(DEFAULT_STORAGE),
        help="Path to the JSON tasks file (default: tasks.json).",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Create a new task.")
    add_parser.add_argument("title", help="Task title.")
    add_parser.add_argument(
        "-d",
        "--description",
        default="",
        help="Optional task description.",
    )

    subparsers.add_parser("list", help="List all tasks.")

    complete_parser = subparsers.add_parser(
        "complete", help="Mark a task as completed."
    )
    complete_parser.add_argument("id", type=int, help="Task ID.")

    delete_parser = subparsers.add_parser("delete", help="Delete a task.")
    delete_parser.add_argument("id", type=int, help="Task ID.")

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns the exit code."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    manager = TaskManager(storage_path=Path(args.file))

    try:
        if args.command == "add":
            task = manager.add_task(args.title, args.description)
            print(f"Task created: {_format_task(task)}")
        elif args.command == "list":
            tasks = manager.list_tasks()
            if not tasks:
                print("No tasks registered.")
            else:
                for task in tasks:
                    print(_format_task(task))
        elif args.command == "complete":
            task = manager.complete_task(args.id)
            print(f"Task completed: {_format_task(task)}")
        elif args.command == "delete":
            task = manager.delete_task(args.id)
            print(f"Task deleted: {_format_task(task)}")
    except TaskNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
