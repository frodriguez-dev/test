"""Unit tests for the task manager (standard library: unittest)."""

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

# Allow importing the package when running the tests directly.
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
    # Creation
    # ------------------------------------------------------------------
    def test_add_task_assigns_incremental_ids(self) -> None:
        first = self.manager.add_task("First")
        second = self.manager.add_task("Second", "with description")

        self.assertEqual(first.id, 1)
        self.assertEqual(second.id, 2)
        self.assertEqual(second.description, "with description")
        self.assertFalse(first.completed)

    def test_add_task_rejects_empty_title(self) -> None:
        with self.assertRaises(ValueError):
            self.manager.add_task("   ")

    # ------------------------------------------------------------------
    # Listing
    # ------------------------------------------------------------------
    def test_list_tasks_returns_sorted_tasks(self) -> None:
        self.manager.add_task("A")
        self.manager.add_task("B")

        titles = [task.title for task in self.manager.list_tasks()]
        self.assertEqual(titles, ["A", "B"])

    # ------------------------------------------------------------------
    # Completion
    # ------------------------------------------------------------------
    def test_complete_task_marks_as_completed(self) -> None:
        task = self.manager.add_task("Do the shopping")

        completed = self.manager.complete_task(task.id)

        self.assertTrue(completed.completed)
        self.assertTrue(self.manager.get_task(task.id).completed)

    def test_complete_nonexistent_task_raises(self) -> None:
        with self.assertRaises(TaskNotFoundError):
            self.manager.complete_task(99)

    # ------------------------------------------------------------------
    # Deletion
    # ------------------------------------------------------------------
    def test_delete_task_removes_it(self) -> None:
        task = self.manager.add_task("Temporary")

        self.manager.delete_task(task.id)

        self.assertEqual(self.manager.list_tasks(), [])

    def test_delete_nonexistent_task_raises(self) -> None:
        with self.assertRaises(TaskNotFoundError):
            self.manager.delete_task(42)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def test_tasks_persist_between_instances(self) -> None:
        self.manager.add_task("Persistent", "saved")
        self.manager.complete_task(1)

        reloaded = TaskManager(storage_path=self.storage)

        self.assertEqual(len(reloaded.list_tasks()), 1)
        task = reloaded.get_task(1)
        self.assertEqual(task.title, "Persistent")
        self.assertEqual(task.description, "saved")
        self.assertTrue(task.completed)

    def test_storage_file_is_valid_json(self) -> None:
        self.manager.add_task("Valid JSON")

        data = json.loads(self.storage.read_text(encoding="utf-8"))

        self.assertIsInstance(data, list)
        self.assertEqual(data[0]["title"], "Valid JSON")

    def test_load_raises_on_invalid_json(self) -> None:
        self.storage.write_text("{ not json", encoding="utf-8")

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
        code, out, _ = self._run("add", "Study", "-d", "Python")
        self.assertEqual(code, 0)
        self.assertIn("Study", out)

        code, out, _ = self._run("list")
        self.assertEqual(code, 0)
        self.assertIn("Study", out)
        self.assertIn("[ ]", out)

    def test_complete_and_delete_flow(self) -> None:
        self._run("add", "Task")

        code, out, _ = self._run("complete", "1")
        self.assertEqual(code, 0)
        self.assertIn("[x]", out)

        code, out, _ = self._run("delete", "1")
        self.assertEqual(code, 0)
        self.assertIn("deleted", out)

        _, out, _ = self._run("list")
        self.assertIn("No tasks", out)

    def test_nonexistent_id_returns_error(self) -> None:
        code, _, err = self._run("complete", "99")

        self.assertEqual(code, 1)
        self.assertIn("No task found", err)

    def test_invalid_arguments_exit(self) -> None:
        with self.assertRaises(SystemExit):
            main(["--file", str(self.storage), "complete", "not-a-number"])


if __name__ == "__main__":
    unittest.main()
