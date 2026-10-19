# Frontend

React single-page application, initialized with React, TypeScript, Vite, and
pnpm in issue #18. This file defines the structure so code lands in a predictable
place from the first commit.

## Getting started

Requires Node.js 20.19 or higher and pnpm.

```bash
cd frontend
pnpm install
pnpm dev        # start the Vite dev server
pnpm build      # type-check and build for production
pnpm preview    # serve the production build locally
```

## Structure

```
frontend/
├── public/                 # Static assets served as-is
├── src/
│   ├── api/                # HTTP client and endpoint modules (backend boundary)
│   ├── assets/             # Imported images, fonts, and other bundled assets
│   ├── components/         # Reusable, presentation-focused UI components
│   ├── features/           # Vertical slices: components, hooks, and state per domain
│   ├── hooks/              # Shared React hooks not tied to one feature
│   ├── lib/                # Framework-agnostic helpers (formatting, validation)
│   ├── pages/              # Route-level screens that compose features
│   ├── styles/             # Global styles, design tokens, and theme setup
│   ├── types/              # Shared TypeScript types
│   ├── App.tsx             # Route composition
│   └── main.tsx            # Application entry point
├── index.html
├── package.json
├── pnpm-lock.yaml
├── tsconfig.json
└── vite.config.ts
```

Only create the directories that are actually needed. The tree describes where
code belongs, not a checklist of empty folders. The initial application only
needs `src/pages/` (the first screen) and `src/styles/` (global styles).

## Import alias

`@/*` resolves to `src/*`, configured in both `tsconfig.app.json` (`paths`) and
`vite.config.ts` (`resolve.alias`). Prefer the alias over long relative paths.

```ts
import { HomePage } from '@/pages/HomePage'
```

## Ownership and boundaries

- `src/api/` is the only place that performs HTTP calls. UI code consumes its
  functions instead of calling `fetch` directly.
- `src/pages/` composes `src/features/` and shared `src/components/`; features
  do not import pages.
- `src/features/<domain>/` owns domain-specific state and UI. Other features
  must use its public entry point rather than reaching into internal files.
- `src/lib/` and `src/components/` must not import from `src/features/` or
  `src/pages/`.
- Dependencies flow downward: `pages → features → components/lib → types`.
  Avoid circular imports.
- Backend access happens only through the versioned REST API, never through
  files shared with `backend/`.

## Conventions

- TypeScript runs in strict mode; avoid `any` without a documented reason.
- Name files by their primary export (`UserCard.tsx`, `useCurrentUser.ts`).
- Keep components small and colocate styles, tests, and hooks with their feature
  when they are not shared.
- Add a dependency only with a clear use case; prefer platform APIs and existing
  packages. Commit `pnpm-lock.yaml` with every dependency change.
- Configuration comes from environment variables exposed by Vite
  (`import.meta.env`). Never commit secrets; only public values belong in the
  frontend bundle.

See [`docs/ai/conventions.md`](../docs/ai/conventions.md) for repository-wide
rules and [`docs/decisions.md`](../docs/decisions.md) for the rationale.
