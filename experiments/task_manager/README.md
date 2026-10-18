# Console Task Manager

A command-line application written in Python that lets you manage personal
tasks and persists them automatically to a JSON file.

It uses **only the Python standard library** (no extra dependencies required).

## Requirements

- Python 3.10 or higher.

## Structure

```
experiments/task_manager/
├── __init__.py              # Exposes the public classes
├── __main__.py              # Allows running with python -m
├── cli.py                   # Command-line interface (argparse)
├── task_manager.py          # Task logic and JSON persistence
├── README.md
└── tests/
    └── test_task_manager.py # Unit tests with unittest
```

## Usage

Run the application as a module from the repository root:

```bash
python -m experiments.task_manager <command> [options]
```

### Available commands

| Command    | Description                              |
| ---------- | ---------------------------------------- |
| `add`      | Create a new task.                       |
| `list`     | List all tasks with their status.        |
| `complete` | Mark a task as completed.                |
| `delete`   | Delete a task.                           |

Global options:

- `--file PATH`: path to the JSON tasks file (default: `tasks.json`).

### Examples

Create a task with an optional description:

```bash
python -m experiments.task_manager add "Buy bread" -d "Whole wheat"
# Task created:   1 [ ] Buy bread  (Whole wheat)

python -m experiments.task_manager add "Study Python"
# Task created:   2 [ ] Study Python
```

List tasks (status is shown as `[ ]` pending and `[x]` completed):

```bash
python -m experiments.task_manager list
#   1 [ ] Buy bread  (Whole wheat)
#   2 [ ] Study Python
```

Mark a task as completed:

```bash
python -m experiments.task_manager complete 1
# Task completed:   1 [x] Buy bread  (Whole wheat)
```

Delete a task:

```bash
python -m experiments.task_manager delete 2
# Task deleted:   2 [ ] Study Python
```

Use a different storage file:

```bash
python -m experiments.task_manager --file my_tasks.json list
```

### Error handling

- A nonexistent ID prints an error message and returns exit code `1`:

  ```bash
  python -m experiments.task_manager complete 99
  # Error: No task found with ID 99.
  ```

- An empty title in `add` also ends with an error.
- Invalid arguments (for example, a non-numeric ID) are rejected by `argparse`
  with a usage message.

## Persistence

Tasks are saved automatically after every operation that modifies state
(`add`, `complete`, `delete`) in the specified JSON file (default
`tasks.json`). When you run the application again, tasks are loaded from that
file.

File format:

```json
[
  {
    "id": 1,
    "title": "Buy bread",
    "description": "Whole wheat",
    "completed": true
  }
]
```

> The `tasks.json` file is a runtime-generated artifact and should not be
> versioned.

## Tests

The tests use the standard library `unittest`. Run them from the repository
root:

```bash
python -m unittest discover -s experiments/task_manager/tests -v
```

You can also run the test file directly:

```bash
python experiments/task_manager/tests/test_task_manager.py
```
