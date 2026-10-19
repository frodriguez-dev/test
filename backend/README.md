# Backend

Django REST API backed by PostgreSQL. Django and the PostgreSQL connection are
initialized; Django REST Framework and the API surface arrive with issue #17.
This file defines the structure so code lands in a predictable place from the
first commit.

## Structure

```
backend/
├── manage.py
├── pyproject.toml          # Backend Python project and dependencies (uv)
├── uv.lock
├── config/
│   ├── settings.py         # Single settings module, configured via environment
│   ├── urls.py             # Root URL configuration and /api/v1/ routing
│   ├── asgi.py
│   └── wsgi.py
├── apps/
│   └── <domain>/           # One Django app per business domain
│       ├── models.py
│       ├── serializers.py
│       ├── views.py
│       ├── urls.py
│       ├── services.py     # Write-side business logic, when needed
│       ├── selectors.py    # Read-side queries, when needed
│       ├── migrations/
│       └── tests/
└── .env.example            # Documented variables, no secret values
```

Only create the modules that are actually needed. `services.py` and
`selectors.py` are optional and should appear when logic stops fitting cleanly in
a view or serializer. There are no business apps yet.

The root `pyproject.toml` is kept for now; the backend Python project lives under
`backend/` and is managed with uv.

## Local setup

Requirements: Python 3.10+ (uv can install it), [uv](https://docs.astral.sh/uv/),
and a running PostgreSQL server.

1. Create the local role and database. The credentials are examples; use your
   own values and keep them out of Git.

   ```sql
   CREATE ROLE app LOGIN PASSWORD 'change-me-in-development';
   CREATE DATABASE app OWNER app;
   ```

2. Create the environment file and adjust it if your credentials differ.

   ```sh
   cp backend/.env.example backend/.env
   ```

3. Install dependencies and apply the initial migrations.

   ```sh
   cd backend
   uv sync
   uv run --env-file .env manage.py migrate
   ```

4. Start the development server.

   ```sh
   uv run --env-file .env manage.py runserver
   ```

`uv run --env-file .env` loads the variables for that command only. If you prefer
a shell session, export the same variables yourself (for example with
`set -a; source .env; set +a`). Without `DJANGO_SECRET_KEY` the settings module
fails fast with an explicit error.

### Environment variables

| Variable | Purpose | Development default |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | Django cryptographic signing key | Required; placeholder in `.env.example` |
| `DJANGO_DEBUG` | Enable debug mode | `false` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost,127.0.0.1` |
| `POSTGRES_DB` | Database name | `app` |
| `POSTGRES_USER` | Database user | `app` |
| `POSTGRES_PASSWORD` | Database password | Empty |
| `POSTGRES_HOST` | Database host | `localhost` |
| `POSTGRES_PORT` | Database port | `5432` |

The database variables match the official PostgreSQL image, so the future Docker
Compose setup can reuse them without renaming. `.env` is ignored by Git; only
`.env.example` is committed.

## Ownership and boundaries

- `config/` contains project wiring only: settings, URL composition, and ASGI/WSGI
  entry points. Business logic does not belong here.
- `apps/<domain>/` owns its models, migrations, API surface, and tests. Name apps
  by domain (`accounts`, `billing`, `catalog`), not by technical layer.
- Request flow: `urls → views → serializers/services → models`. Views stay thin;
  business rules live in services or model methods when they are shared.
- Cross-app access goes through the other app's public Python API (imports from
  its models/services) or the REST API. Do not read another app's tables through
  raw SQL.
- The backend never imports frontend code. The contract is the versioned REST
  API under `/api/v1/`.

## Conventions

- Follow PEP 8 and the Python conventions in
  [`docs/ai/conventions.md`](../docs/ai/conventions.md).
- Keep every model change in a migration committed with the code that needs it.
- Serializers validate input and shape output; they do not contain multi-step
  business workflows.
- Return DRF-standard JSON errors so the frontend can handle failures
  consistently.
- Add a dependency only with a clear use case and record it in
  `backend/pyproject.toml`. Commit `uv.lock` with every dependency change.
- Configuration comes from environment variables. Provide an `.env.example` with
  variable names and safe defaults, never real credentials.
- Tests live next to their app under `apps/<domain>/tests/`.

See [`docs/decisions.md`](../docs/decisions.md) for the rationale behind these
choices.
