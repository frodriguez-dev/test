# Frontend

React single-page application. It is **not initialized yet**; issue #18 will add
the toolchain (React, TypeScript, Vite, and pnpm). This file defines the intended
structure so code lands in a predictable place from the first commit.

## Intended structure

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
code belongs, not a checklist of empty folders.

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

- TypeScript strict mode is expected; avoid `any` without a documented reason.
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
