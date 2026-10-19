# Backend

Django REST API backed by PostgreSQL. It is **not initialized yet**; issue #17
will add the toolchain (Django, Django REST Framework, PostgreSQL driver, and
uv). This file defines the intended structure so code lands in a predictable
place from the first commit.

## Intended structure

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
a view or serializer.

The root `pyproject.toml` is kept for now; the backend Python project will live
under `backend/` once issue #17 initializes it.

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
