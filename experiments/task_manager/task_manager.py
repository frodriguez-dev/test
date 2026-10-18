"""Lógica de gestión de tareas con persistencia en JSON.

Este módulo implementa :class:`TaskManager`, que administra una colección de
tareas personales y las persiste automáticamente en un archivo JSON. No usa
dependencias externas: solo la biblioteca estándar de Python.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


class TaskNotFoundError(Exception):
    """Se lanza cuando se referencia un ID de tarea inexistente."""

    def __init__(self, task_id: int) -> None:
        self.task_id = task_id
        super().__init__(f"No existe una tarea con el ID {task_id}.")


@dataclass
class Task:
    """Representa una tarea individual."""

    id: int
    title: str
    description: str = ""
    completed: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Devuelve la tarea como un diccionario serializable."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Task":
        """Construye una tarea a partir de un diccionario."""
        return cls(
            id=int(data["id"]),
            title=str(data["title"]),
            description=str(data.get("description", "")),
            completed=bool(data.get("completed", False)),
        )


@dataclass
class TaskManager:
    """Administra tareas y las persiste en un archivo JSON.

    Cada operación que modifica el estado (crear, completar o eliminar) guarda
    automáticamente los cambios en disco.
    """

    storage_path: Path = field(default_factory=lambda: Path("tasks.json"))
    tasks: list[Task] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.storage_path = Path(self.storage_path)
        self.load()

    # ------------------------------------------------------------------
    # Persistencia
    # ------------------------------------------------------------------
    def load(self) -> None:
        """Carga las tareas desde el archivo JSON, si existe."""
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
                f"El archivo {self.storage_path} no contiene JSON válido: {exc}"
            ) from exc

        if not isinstance(data, list):
            raise ValueError(
                f"El archivo {self.storage_path} debe contener una lista de tareas."
            )

        self.tasks = [Task.from_dict(item) for item in data]

    def save(self) -> None:
        """Escribe las tareas actuales en el archivo JSON."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = [task.to_dict() for task in self.tasks]
        self.storage_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    # ------------------------------------------------------------------
    # Operaciones
    # ------------------------------------------------------------------
    def _next_id(self) -> int:
        return max((task.id for task in self.tasks), default=0) + 1

    def add_task(self, title: str, description: str = "") -> Task:
        """Crea una tarea nueva y la persiste.

        Args:
            title: Título de la tarea. No puede estar vacío.
            description: Descripción opcional.

        Returns:
            La tarea creada.
        """
        title = title.strip()
        if not title:
            raise ValueError("El título de la tarea no puede estar vacío.")

        task = Task(id=self._next_id(), title=title, description=description.strip())
        self.tasks.append(task)
        self.save()
        return task

    def list_tasks(self) -> list[Task]:
        """Devuelve todas las tareas ordenadas por ID."""
        return sorted(self.tasks, key=lambda task: task.id)

    def get_task(self, task_id: int) -> Task:
        """Busca una tarea por su ID.

        Raises:
            TaskNotFoundError: si no existe una tarea con ese ID.
        """
        for task in self.tasks:
            if task.id == task_id:
                return task
        raise TaskNotFoundError(task_id)

    def complete_task(self, task_id: int) -> Task:
        """Marca una tarea como completada y persiste el cambio."""
        task = self.get_task(task_id)
        task.completed = True
        self.save()
        return task

    def delete_task(self, task_id: int) -> Task:
        """Elimina una tarea y persiste el cambio."""
        task = self.get_task(task_id)
        self.tasks.remove(task)
        self.save()
        return task
