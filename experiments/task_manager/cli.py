"""Interfaz de línea de comandos del gestor de tareas.

Uso::

    python -m experiments.task_manager add "Comprar pan" --description "Integral"
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
        description="Gestor de tareas por consola con persistencia en JSON.",
    )
    parser.add_argument(
        "--file",
        default=str(DEFAULT_STORAGE),
        help="Ruta del archivo JSON de tareas (por defecto: tasks.json).",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Crear una tarea nueva.")
    add_parser.add_argument("title", help="Título de la tarea.")
    add_parser.add_argument(
        "-d",
        "--description",
        default="",
        help="Descripción opcional de la tarea.",
    )

    subparsers.add_parser("list", help="Listar todas las tareas.")

    complete_parser = subparsers.add_parser(
        "complete", help="Marcar una tarea como completada."
    )
    complete_parser.add_argument("id", type=int, help="ID de la tarea.")

    delete_parser = subparsers.add_parser("delete", help="Eliminar una tarea.")
    delete_parser.add_argument("id", type=int, help="ID de la tarea.")

    return parser


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada de la CLI. Devuelve el código de salida."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    manager = TaskManager(storage_path=Path(args.file))

    try:
        if args.command == "add":
            task = manager.add_task(args.title, args.description)
            print(f"Tarea creada: {_format_task(task)}")
        elif args.command == "list":
            tasks = manager.list_tasks()
            if not tasks:
                print("No hay tareas registradas.")
            else:
                for task in tasks:
                    print(_format_task(task))
        elif args.command == "complete":
            task = manager.complete_task(args.id)
            print(f"Tarea completada: {_format_task(task)}")
        elif args.command == "delete":
            task = manager.delete_task(args.id)
            print(f"Tarea eliminada: {_format_task(task)}")
    except TaskNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
