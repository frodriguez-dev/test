# Agent pipeline tooling

Repository-level Python tooling for the local agent pipeline. Today it owns the
quality gate from issue #44; later issues add their own modules rather than
pre-creating empty packages.

- Runtime: Python 3.11 or newer and the standard library only.
- Development: pytest, declared in this project's `pyproject.toml`.
- Entry point: `uv run --project tools/agent_pipeline python -m agent_pipeline quality`.
  From the repository root, `make quality` wraps the same command.

## Running the gate

```sh
make quality
make quality-backend
make quality-frontend
make quality-complexity
make quality-security
make quality QUALITY_ARGS="--json --output /tmp/quality.json"
make quality QUALITY_ARGS="--security-network"
```

`--layer` and `--check` select a subset. `--list-checks` prints the catalog.
`make quality` writes `.quality/quality.json` and per-check logs under
`.quality/logs/`; both are ignored by Git. GNU Make reports `2` for any failed
recipe, so call the CLI directly when a script needs the exact `1` (required
failure) versus `2` (incomplete) exit code; the same code is in the JSON report.

### Exit codes

| Code | Gate status | Meaning |
| ---- | ----------- | ------- |
| `0` | `PASS` | Every required check passed. |
| `1` | `FAIL` | At least one required check exited non-zero. |
| `2` | `ERROR` | A required check was skipped, timed out, or could not start; or the configuration is invalid. Takes precedence over `FAIL`. |

`SKIP` is only valid for optional checks. A required check that is disabled or
not executable becomes `ERROR`, so a green gate cannot hide missing tooling.

## Configuration

Defaults live in this project's `pyproject.toml` under
`[tool.agent_pipeline.quality]`. Timeouts are per check id, thresholds set the
Python and TypeScript complexity maxima, and `security.*` records the
adopt/defer decision. Unknown keys are rejected, as are unknown check ids in
`timeouts`. CLI flags override thresholds, timeouts, and the output cap for a
single run.

The JSON report has `schema_version = 1` and, for each check, `id`, `layer`,
`command`, `working_directory`, `status`, `exit_code`, `duration_seconds`,
`summary`, `output_path`, and `required`. The overall report adds `status`,
`exit_code`, timestamps, duration, per-status counts, and best-effort
`tool_versions`. `output_path` is relative to the repository root and points at
the capped command log.

## Checks

| Layer | Check id | Required | Command |
| ----- | -------- | -------- | ------- |
| backend | `backend-lint` | yes | `uv run ruff check .` |
| backend | `backend-format` | yes | `uv run ruff format --check .` |
| backend | `backend-typecheck` | yes | `uv run mypy manage.py config apps` |
| backend | `backend-test` | yes | `make backend-test` |
| frontend | `frontend-typecheck` | yes | `pnpm typecheck` |
| frontend | `frontend-lint` | yes | `pnpm lint` |
| frontend | `frontend-format` | yes | `pnpm format:check` |
| frontend | `frontend-test` | yes | `pnpm test` |
| frontend | `frontend-build` | yes | `make frontend-build` |
| complexity | `backend-complexity` | yes | `uv run ruff check --select C901 ...` |
| complexity | `frontend-complexity` | yes | `pnpm exec eslint . --rule ...` |
| security | `python-security` | yes | `uv run ruff check --select S .` |
| security | `uv-audit` | no (opt-in) | `uv audit --locked` |
| security | `pnpm-audit` | no (opt-in) | `pnpm audit` |

Optional checks report `FAIL` when they run and fail, but they do not change the
gate exit code because only required checks gate. Network audits are opt-in; a
skipped audit is `SKIP`, never `PASS`.

Commands run with an absolute working directory, a non-interactive
`CI=1`/`NO_COLOR=1` environment, no shell, a per-check timeout, and a capped
combined log (64 KiB by default, with an explicit truncation marker). Environment
variables and secrets are never printed.

## Development

```sh
uv run --project tools/agent_pipeline pytest
```
