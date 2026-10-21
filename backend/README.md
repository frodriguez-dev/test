# Backend

Django REST API backed by PostgreSQL. Django, the PostgreSQL connection, Django
REST Framework, and the OpenAPI contract are initialized, and the first endpoint
(`GET /api/health/`) is available. This file defines the structure so code lands
in a predictable place from the first commit.

## Structure

```
backend/
├── manage.py
├── pyproject.toml          # Backend Python project and dependencies (uv)
├── uv.lock
├── config/
│   ├── settings.py         # Single settings module, configured via environment
│   ├── urls.py             # Root URL configuration; includes each app's URLs
│   ├── asgi.py
│   └── wsgi.py
├── apps/
│   ├── core/               # Infrastructure endpoints (health check)
│   │   ├── apps.py
│   │   ├── views.py
│   │   ├── serializers.py  # Response shapes documented in the OpenAPI schema
│   │   ├── urls.py
│   │   └── tests/
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
a view or serializer. There are no business apps yet; `apps/core/` holds
cross-cutting infrastructure endpoints.

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

3. Install dependencies, run the configuration check, and apply the initial
   migrations.

   ```sh
   cd backend
   uv sync
   uv run --env-file .env manage.py check
   uv run --env-file .env manage.py migrate
   ```

4. Start the development server.

   ```sh
   uv run --env-file .env manage.py runserver
   ```

`uv run --env-file .env` loads the variables for that command only. If you prefer
a shell session, export the same variables yourself (for example with
`set -a; source .env; set +a`). When `DJANGO_DEBUG` is enabled and
`DJANGO_SECRET_KEY` is unset, the settings module generates an ephemeral key and
warns, so commands such as `manage.py check` run without a `.env`. With
`DJANGO_DEBUG` disabled the key is required and the settings module fails fast
with an explicit error.

Run the backend tests (Django's test runner; they need no database):

```sh
uv run --env-file .env manage.py test
```

### Docker Compose

From the repository root, `docker compose up --build` starts PostgreSQL, the
backend, and the frontend. The backend container runs migrations and then
Django's autoreloading development server on port 8000; the source directory is
bind-mounted so code changes reload automatically. Compose overrides
`POSTGRES_HOST` with the `db` service name, so the non-Docker `localhost`
default does not apply inside the container.

Run commands and tests inside the container with:

```sh
docker compose exec backend uv run --no-sync manage.py check
docker compose exec backend uv run --no-sync manage.py test
```

See the root [`README.md`](../README.md#local-development-with-docker-compose)
for the full up, logs, and down workflow.

### Environment variables

| Variable | Purpose | Development default |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | Django cryptographic signing key | Required when `DJANGO_DEBUG=false`; ephemeral in development |
| `DJANGO_DEBUG` | Enable debug mode | `false` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost,127.0.0.1` |
| `POSTGRES_DB` | Database name | `app` |
| `POSTGRES_USER` | Database user | `app` |
| `POSTGRES_PASSWORD` | Database password | Empty |
| `POSTGRES_HOST` | Database host | `localhost` |
| `POSTGRES_PORT` | Database port | `5432` |

The database variables match the official PostgreSQL image, so the Docker
Compose setup reuses them without renaming. `.env` is ignored by Git; only
`.env.example` is committed.

## API

Django REST Framework serves JSON only (see `REST_FRAMEWORK` in
`config/settings.py`), so responses and errors have a predictable content type.

| Method | Path | Response |
| --- | --- | --- |
| `GET` | `/api/health/` | `200` with `{"status": "ok"}` |
| `GET` | `/api/schema/` | `200` with the generated OpenAPI 3 document |
| `GET` | `/api/docs/` | Swagger UI for the generated document |

`/api/health/` is an unversioned infrastructure endpoint for probes and startup
checks. Business endpoints live under the versioned `/api/v1/` prefix
(decision [0005](../docs/decisions.md)); the versioned surface is added with the
first business domain.

### OpenAPI contract

The API contract is generated from the Django REST Framework code with
[drf-spectacular](https://drf-spectacular.readthedocs.io/) and is the single
source of truth for the API. `docs/api/openapi.yaml` is a committed snapshot for
review and consumption; do not edit it by hand. Regenerate it after changing the
API surface:

```sh
uv run --env-file .env manage.py spectacular --file ../docs/api/openapi.yaml
```

Validate the generated document without writing it:

```sh
uv run --env-file .env manage.py spectacular --validate --file /dev/null
```

Tests fail when the committed snapshot differs from the code, and they validate
both the generated and the committed documents. Describe endpoint parameters,
request bodies, and responses with serializers and
`drf_spectacular.utils.extend_schema` so they appear in the schema; keep
prose documentation to what the schema cannot express.

## Ownership and boundaries

- `config/` contains project wiring only: settings, URL composition, and ASGI/WSGI
  entry points. Business logic does not belong here.
- `apps/<domain>/` owns its models, migrations, API surface, and tests. Name apps
  by domain (`accounts`, `billing`, `catalog`), not by technical layer.
- `apps/core/` holds cross-cutting infrastructure endpoints only (for example the
  health check); business rules never belong there.
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
