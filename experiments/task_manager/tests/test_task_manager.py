"""Pruebas unitarias del gestor de tareas (biblioteca estándar: unittest)."""

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

# Permite importar el paquete al ejecutar las pruebas directamente.
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from experiments.task_manager.cli import main
from experiments.task_manager.task_manager import TaskManager, TaskNotFoundError


class TaskManagerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.storage = Path(self.tmp.name) / "tasks.json"
        self.manager = TaskManager(storage_path=self.storage)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    # ------------------------------------------------------------------
    # Creación
    # ------------------------------------------------------------------
    def test_add_task_assigns_incremental_ids(self) -> None:
        first = self.manager.add_task("Primera")
        second = self.manager.add_task("Segunda", "con descripción")

        self.assertEqual(first.id, 1)
        self.assertEqual(second.id, 2)
        self.assertEqual(second.description, "con descripción")
        self.assertFalse(first.completed)

    def test_add_task_rejects_empty_title(self) -> None:
        with self.assertRaises(ValueError):
            self.manager.add_task("   ")

    # ------------------------------------------------------------------
    # Listado
    # ------------------------------------------------------------------
    def test_list_tasks_returns_sorted_tasks(self) -> None:
        self.manager.add_task("A")
        self.manager.add_task("B")

        titles = [task.title for task in self.manager.list_tasks()]
        self.assertEqual(titles, ["A", "B"])

    # ------------------------------------------------------------------
    # Completar
    # ------------------------------------------------------------------
    def test_complete_task_marks_as_completed(self) -> None:
        task = self.manager.add_task("Hacer la compra")

        completed = self.manager.complete_task(task.id)

        self.assertTrue(completed.completed)
        self.assertTrue(self.manager.get_task(task.id).completed)

    def test_complete_nonexistent_task_raises(self) -> None:
        with self.assertRaises(TaskNotFoundError):
            self.manager.complete_task(99)

    # ------------------------------------------------------------------
    # Eliminar
    # ------------------------------------------------------------------
    def test_delete_task_removes_it(self) -> None:
        task = self.manager.add_task("Temporal")

        self.manager.delete_task(task.id)

        self.assertEqual(self.manager.list_tasks(), [])

    def test_delete_nonexistent_task_raises(self) -> None:
        with self.assertRaises(TaskNotFoundError):
            self.manager.delete_task(42)

    # ------------------------------------------------------------------
    # Persistencia
    # ------------------------------------------------------------------
    def test_tasks_persist_between_instances(self) -> None:
        self.manager.add_task("Persistente", "guardada")
        self.manager.complete_task(1)

        reloaded = TaskManager(storage_path=self.storage)

        self.assertEqual(len(reloaded.list_tasks()), 1)
        task = reloaded.get_task(1)
        self.assertEqual(task.title, "Persistente")
        self.assertEqual(task.description, "guardada")
        self.assertTrue(task.completed)

    def test_storage_file_is_valid_json(self) -> None:
        self.manager.add_task("JSON válido")

        data = json.loads(self.storage.read_text(encoding="utf-8"))

        self.assertIsInstance(data, list)
        self.assertEqual(data[0]["title"], "JSON válido")

    def test_load_raises_on_invalid_json(self) -> None:
        self.storage.write_text("{ no es json", encoding="utf-8")

        with self.assertRaises(ValueError):
            TaskManager(storage_path=self.storage)


class CliTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.storage = Path(self.tmp.name) / "tasks.json"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _run(self, *args: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(["--file", str(self.storage), *args])
        return code, out.getvalue(), err.getvalue()

    def test_add_and_list_flow(self) -> None:
        code, out, _ = self._run("add", "Estudiar", "-d", "Python")
        self.assertEqual(code, 0)
        self.assertIn("Estudiar", out)

        code, out, _ = self._run("list")
        self.assertEqual(code, 0)
        self.assertIn("Estudiar", out)
        self.assertIn("[ ]", out)

    def test_complete_and_delete_flow(self) -> None:
        self._run("add", "Tarea")

        code, out, _ = self._run("complete", "1")
        self.assertEqual(code, 0)
        self.assertIn("[x]", out)

        code, out, _ = self._run("delete", "1")
        self.assertEqual(code, 0)
        self.assertIn("eliminada", out)

        _, out, _ = self._run("list")
        self.assertIn("No hay tareas", out)

    def test_nonexistent_id_returns_error(self) -> None:
        code, _, err = self._run("complete", "99")

        self.assertEqual(code, 1)
        self.assertIn("No existe", err)

    def test_invalid_arguments_exit(self) -> None:
        with self.assertRaises(SystemExit):
            main(["--file", str(self.storage), "complete", "no-un-numero"])


if __name__ == "__main__":
    unittest.main()
