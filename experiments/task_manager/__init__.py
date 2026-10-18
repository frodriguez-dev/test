"""Gestor de tareas por consola.

Paquete que contiene la lógica de gestión de tareas y la interfaz de línea
de comandos para administrarlas.
"""

from .task_manager import Task, TaskManager, TaskNotFoundError

__all__ = ["Task", "TaskManager", "TaskNotFoundError"]
