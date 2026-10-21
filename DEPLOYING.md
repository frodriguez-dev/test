# Deploying the development environment

This guide explains how to run the monorepo locally. It covers the Docker
Compose workflow and the equivalent workflow with the backend and frontend
toolchains installed on the host.

This is a **development** environment. It is not a production deployment guide:
the defaults are not secret, the servers run in development mode, and the
Dockerfiles are development images.

The common commands are wrapped in the root `Makefile`. Run `make help` to list
them. Each target delegates to Docker Compose, uv, or pnpm; this guide explains
what to run and how to verify the result. See the root [`README.md`](README.md)
for the repository overview.

## Prerequisites

Choose one workflow.

### Docker Compose

- Docker Engine with the Compose plugin (`docker compose version`).
- GNU Make (`make --version`).
- Git.

### Local toolchains

- GNU Make.
- Python 3.10 or higher and [uv](https://docs.astral.sh/uv/) (`uv --version`).
- Node.js 20.19 or higher and pnpm 10.15 (`node --version`, `pnpm --version`).
- PostgreSQL 17 running locally (`psql --version`). The backend does not fall
  back to SQLite.
- Git.

Both workflows use these ports by default:

| Service  | Port |
| -------- | ---- |
| Frontend | 5173 |
| Backend  | 8000 |
| Database | 5432 |

Docker publishes only the frontend and backend ports. The database is reachable
from the other Compose services on `db:5432`. If a port is already in use, see
[Changing ports](#changing-ports).

## Environment variables

The `.env` files are ignored by Git. Never commit real credentials. The values
in the examples and in `compose.yaml` are non-secret development defaults.

### With Docker Compose

Docker Compose works without an `.env` file because `compose.yaml` defines safe
defaults. To override them, create a root `.env` file and set any of these
variables, which reuse the names from `backend/.env.example`:

```dotenv
POSTGRES_DB=app
POSTGRES_USER=app
POSTGRES_PASSWORD=change-me-in-development
DJANGO_SECRET_KEY=change-me-in-development
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,backend
DJANGO_CSRF_TRUSTED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
BACKEND_PORT=8000
FRONTEND_PORT=5173
```

Compose reads the root `.env` automatically. Do not copy `backend/.env` into the
root: inside Compose, `POSTGRES_HOST` is always the `db` service, and Compose
sets it for you.

### Without Docker

Create the backend environment file from its example and adjust it if your local
PostgreSQL credentials differ:

```sh
cp backend/.env.example backend/.env
```

The backend reads that file through `uv run --env-file .env` in the Makefile.
The main variables are:

| Variable               | Purpose                          | Example                  |
| ---------------------- | -------------------------------- | ------------------------ |
| `DJANGO_SECRET_KEY`    | Django cryptographic signing key | `change-me-in-development` |
| `DJANGO_DEBUG`         | Enable debug mode                | `true`                   |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated allowed hosts    | `localhost,127.0.0.1`    |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Origins allowed on unsafe requests | `http://localhost:5173,http://127.0.0.1:5173` |
| `POSTGRES_DB`          | Database name                    | `app`                    |
| `POSTGRES_USER`        | Database user                    | `app`                    |
| `POSTGRES_PASSWORD`    | Database password                | `change-me-in-development` |
| `POSTGRES_HOST`        | Database host                    | `localhost`              |
| `POSTGRES_PORT`        | Database port                    | `5432`                   |

The frontend does not need an `.env` file for the default setup. Its Vite dev
server proxies `/api` to `http://localhost:8000`. If the backend runs on another
port or host, copy the example and change the target:

```sh
cp frontend/.env.example frontend/.env
# then edit VITE_API_PROXY_TARGET in frontend/.env
```

## Start with Docker Compose

From the repository root:

1. Build the images and start PostgreSQL, the backend, and the frontend:

   ```sh
   make up-build
   ```

   The first run must build the images. Use `make up` on later runs when the
   images do not need rebuilding; it starts the existing images without a
   build. Both targets run the stack in the background.

2. Follow the startup logs:

   ```sh
   make logs
   ```

   The backend waits for the PostgreSQL healthcheck and applies migrations
   automatically before starting Django's development server.

3. Check the status of the services in another terminal:

   ```sh
   make status
   ```

4. Verify that the stack is healthy (see
   [URLs and health checks](#urls-and-health-checks)).

Source directories are bind-mounted, so frontend and backend changes reload
automatically. Frontend dependencies live in a named volume, so the container
does not depend on a host `node_modules/`.

To open a shell in a container:

```sh
make shell-backend    # sh in the backend container
make shell-frontend   # sh in the frontend container
make shell-db         # psql in the database container
```

## Start without Docker

This workflow runs PostgreSQL on the host and starts Django and Vite directly.
Open two terminals after completing the setup.

1. Start PostgreSQL and create the local role and database. The credentials are
   examples; use your own values and keep them out of Git.

   ```sql
   CREATE ROLE app LOGIN PASSWORD 'change-me-in-development';
   CREATE DATABASE app OWNER app;
   ```

2. Create `backend/.env` from the example and adjust it if your credentials
   differ, as described in
   [Environment variables](#without-docker).

   ```sh
   cp backend/.env.example backend/.env
   ```

3. Install the backend dependencies and apply the migrations:

   ```sh
   make backend-install
   make backend-migrate
   ```

4. Start the Django development server on port 8000:

   ```sh
   make backend-dev
   ```

5. In the second terminal, install the frontend dependencies and start Vite:

   ```sh
   make frontend-install
   make frontend-dev
   ```

6. Verify the environment (see
   [URLs and health checks](#urls-and-health-checks)).

The frontend build is separate from the dev server:

```sh
make frontend-build
```

Run the backend test suite with:

```sh
make backend-test
```

The tests use PostgreSQL and create a test database, so the configured role
needs permission to create databases. The frontend checks are not wrapped in
`Makefile`; run `pnpm check` from `frontend/` as documented in
[`frontend/README.md`](frontend/README.md#testing-and-quality).

## URLs and health checks

With the default ports:

| Service     | Address                              | Notes                                                       |
| ----------- | ------------------------------------ | ----------------------------------------------------------- |
| Frontend    | <http://localhost:5173>              | Vite dev server; `/` is protected by the login screen.      |
| Backend     | <http://localhost:8000>              | Django development server.                                  |
| Health      | <http://localhost:8000/api/health/>  | Expected response: `{"status": "ok"}`.                      |
| API docs    | <http://localhost:8000/api/docs/>    | Swagger UI for the generated OpenAPI document.              |
| API schema  | <http://localhost:8000/api/schema/>  | Generated OpenAPI document.                                 |
| Database    | `db:5432` (Compose)                  | Only reachable from the Compose services.                   |
| Database    | `localhost:5432` (local toolchains)  | The PostgreSQL instance running on the host.                |

Verify the health endpoint from the host:

```sh
make health
# or
curl --fail --silent --show-error http://localhost:8000/api/health/
```

The expected output is:

```json
{"status": "ok"}
```

If the frontend loads but API requests fail, check the backend logs and the
`VITE_API_PROXY_TARGET` value as described in
[Troubleshooting](#troubleshooting).

## Stopping and cleaning up

Stop the Docker Compose services and keep the PostgreSQL data:

```sh
make down
```

Stop the services and **delete the PostgreSQL data** in the `postgres_data`
volume:

```sh
make down-volumes
```

`make down-volumes` is destructive and cannot be undone. Use `make down` unless
you intentionally want a clean database to re-run migrations from scratch.

When running without Docker, stop the backend and frontend with `Ctrl+C` in
their terminals. The local PostgreSQL server and its data are managed by your
operating system and are not removed by the `Makefile`.

## Changing ports

The `Makefile` passes `BACKEND_PORT` and `FRONTEND_PORT` to Docker Compose and
uses them for the local servers and the health check. Override them on the
command line:

```sh
make up-build BACKEND_PORT=8080 FRONTEND_PORT=3000
make health BACKEND_PORT=8080
```

Without Docker, start each server with matching values and point the frontend
proxy at the backend port:

```sh
make backend-dev BACKEND_PORT=8080
make frontend-dev FRONTEND_PORT=3000
# set VITE_API_PROXY_TARGET=http://localhost:8080 in frontend/.env
```

The service names used by the shell targets can also be overridden, for example
`make shell-db DB_SERVICE=db`. Compose, its file, and the application
directories are configurable through `COMPOSE`, `COMPOSE_FILE`, `BACKEND_DIR`,
and `FRONTEND_DIR`.

## Troubleshooting

### `make: command not found`

Install GNU Make with your operating system's package manager. The targets use
POSIX shell commands and GNU Make features, so a plain `make` from a different
implementation is not supported.

### `Cannot connect to the Docker daemon`

Start Docker Engine and confirm that your user can access the Docker socket
(for example, that you are in the `docker` group on Linux). Then run
`docker compose version` to confirm the Compose plugin is installed.

### A port is already in use

Identify the process and either stop it or choose another port:

```sh
ss -ltnp | grep -E ':(5173|8000|5432)\b'
make up-build BACKEND_PORT=8080 FRONTEND_PORT=3000
```

For the local workflow, start Django and Vite with the same overrides and update
`frontend/.env` as described in [Changing ports](#changing-ports).

### `make up` starts but the backend is not ready

`make up` does not build images. On a fresh clone, use `make up-build`. If the
images already exist, inspect the logs and status:

```sh
make logs
make status
```

The backend starts only after PostgreSQL passes its healthcheck. Database
connection errors usually mean the Compose service is still starting or the
credentials in the root `.env` no longer match the existing volume.

### The backend cannot connect to PostgreSQL without Docker

Check that PostgreSQL is running on `localhost:5432`, that `backend/.env` has
the expected `POSTGRES_*` values, and that the role and database exist. The
default host in `backend/.env.example` is `localhost`, which is correct for the
host workflow and is overridden to `db` by Compose.

### `backend/.env` is missing or Django exits at startup

The Makefile passes `backend/.env` to every backend command. Create it from the
example and set the values that differ from your environment:

```sh
cp backend/.env.example backend/.env
```

With `DJANGO_DEBUG=true`, Django can start without `DJANGO_SECRET_KEY`, but it
uses an ephemeral key and sessions do not survive a restart. Set a stable value
for normal development.

### `DisallowedHost` or a host validation error

Add the host you use to `DJANGO_ALLOWED_HOSTS`. For the Docker workflow, put it
in the root `.env`; for the local workflow, put it in `backend/.env`. The
Compose default already includes `localhost`, `127.0.0.1`, and `backend`.

### `CSRF verification failed` when logging in

Django rejects unsafe requests whose `Origin` header is not listed in
`DJANGO_CSRF_TRUSTED_ORIGINS`. Add the frontend origin, including the port you
use, to the root `.env` (Docker) or `backend/.env` (local), then restart the
backend. The default is `http://localhost:5173,http://127.0.0.1:5173`, and
Compose adjusts it to `FRONTEND_PORT`.

```dotenv
DJANGO_CSRF_TRUSTED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### The frontend shows network errors

Confirm that the backend health endpoint responds. In the local workflow, the
Vite proxy defaults to `http://localhost:8000`; if Django runs elsewhere, set
`VITE_API_PROXY_TARGET` in `frontend/.env`. In the Docker workflow, Compose
sets the proxy target to `http://backend:8000` automatically.

### Changes to dependencies are not reflected in Docker

Rebuild the images:

```sh
make up-build
```

The named frontend `node_modules` volume is kept across rebuilds; if it is stale
after a lock-file change, remove it with `make down-volumes` and rebuild. That
also deletes the PostgreSQL data.

### An unknown target was requested

The `Makefile` prints a short error and exits with a non-zero status. Run
`make help` to see the available targets and their descriptions.

## Related documentation

- [`README.md`](README.md) — repository overview, stack, and quality checks.
- [`backend/README.md`](backend/README.md) — backend structure, API, and
  environment variables.
- [`frontend/README.md`](frontend/README.md) — frontend structure, API client,
  and frontend checks.
- [`docs/ai/conventions.md`](docs/ai/conventions.md) — repository conventions.
