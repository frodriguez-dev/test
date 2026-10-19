# Agent skills

This repository uses [Agent Skills](https://agentskills.io) to hold reusable,
task-specific procedures. General rules stay in [`AGENTS.md`](../../AGENTS.md);
skills are loaded only when their description matches the current task.

## Canonical location and sharing

Installed skills live in `.agents/skills/<name>/` and are committed to Git.
This path is read natively by Codex and OpenCode.

Claude Code reads `.claude/skills/`. Each installed skill is linked there with a
**relative symlink** to the canonical copy, so there is a single source of truth
and no duplicated content:

```
.agents/skills/<name>/          canonical content (committed)
.claude/skills/<name>           -> ../../.agents/skills/<name> (committed)
skills-lock.json                installer lock file (committed)
```

The `_template/` directory is a starting point, not an installed skill.

Do not install skills globally (`-g`) for this repository. Project scope keeps
the setup reproducible and avoids depending on a developer's home directory.

## Installed catalog

Installed on 2026-10-19 with `skills` CLI 1.7.2 (project scope, agents:
Codex, OpenCode, Claude Code).

| Skill | Source | Upstream revision | License | Purpose | Validation |
| --- | --- | --- | --- | --- | --- |
| `find-skills` | [`vercel-labs/skills`](https://github.com/vercel-labs/skills) | `13e4063a1cf913f5606d57d42ab83a86f5001e04` | MIT | Find and evaluate existing skills before building new ones. | Installed; content matches upstream; discovered by Codex and OpenCode. |
| `systematic-debugging` | [`obra/superpowers`](https://github.com/obra/superpowers) v7.0.0 | `bb92a77741419a4ab5f06e711a283343f1ada0c3` | MIT | Root-cause investigation before proposing fixes. | Installed; content matches upstream; discovered by Codex and OpenCode. |
| `test-driven-development` | [`obra/superpowers`](https://github.com/obra/superpowers) v7.0.0 | `bb92a77741419a4ab5f06e711a283343f1ada0c3` | MIT | Red-green-refactor for behavior changes. | Installed; content matches upstream; discovered by Codex and OpenCode. |
| `verification-before-completion` | [`obra/superpowers`](https://github.com/obra/superpowers) v7.0.0 | `bb92a77741419a4ab5f06e711a283343f1ada0c3` | MIT | Require fresh evidence before claiming success. | Installed; content matches upstream; discovered by Codex and OpenCode. |
| `skill-creator` | [`anthropics/skills`](https://github.com/anthropics/skills) | `dbd4588f9e1033efb41dad4bef2f7947c8993d44` | Apache-2.0 | Create, edit, and evaluate skills, including bundled scripts and references. | Installed with all resources; content matches upstream; discovered by Codex and OpenCode. |

Exact upstream URLs:

- <https://skills.sh/vercel-labs/skills/find-skills>
- <https://skills.sh/obra/superpowers/systematic-debugging>
- <https://skills.sh/obra/superpowers/test-driven-development>
- <https://skills.sh/obra/superpowers/verification-before-completion>
- <https://skills.sh/anthropics/skills/skill-creator>

Third-party license notices are in
[`THIRD_PARTY_NOTICES.md`](../../THIRD_PARTY_NOTICES.md).

## When to use each skill

- `find-skills`: the task needs a capability that may already exist as a skill.
  It may *recommend* an installation, but installing requires explicit
  authorization from the user or orchestrator.
- `systematic-debugging`: any bug, failing test, build failure, or unexpected
  behavior, before proposing or applying a fix.
- `test-driven-development`: new behavior, bug fixes, refactoring, or any
  change that can be verified with tests. Do not force it on documentation-only
  or configuration-only changes.
- `verification-before-completion`: before reporting completion, committing, or
  opening a Pull Request. Especially important for autonomous runs.
- `skill-creator`: creating a new skill, improving an existing one, or
  evaluating skill output. Its evaluation scripts are optional and must be
  reviewed before use (see *Security notes*).

## Installation

The CLI is used directly through `npx`; it is not a project dependency. Install
or reinstall a single skill from its source:

```bash
npx skills add vercel-labs/skills \
  --skill find-skills \
  -a codex -a opencode -a claude-code \
  -y
```

Repeat with the source and skill name from the catalog. Installing to both
`codex` and `opencode` writes the canonical copy to `.agents/skills/`; adding
`claude-code` creates the relative symlink under `.claude/skills/`.

Keep `skills-lock.json` under version control. It records each skill's source,
path, and content hash. The lock file does not record upstream commit IDs, so
the revision column above is the authoritative provenance record.

## Updating

1. Review the upstream repository, release notes, and license.
2. Run the update for the project only:

   ```bash
   npx skills update -p
   ```

   Or update named skills:

   ```bash
   npx skills update find-skills systematic-debugging -p
   ```

3. Inspect the diff of `.agents/skills/`, `.claude/skills/`, and
   `skills-lock.json`. The symlinks must stay relative.
4. Re-run the checks in *Validation* and review any behavior change in the
   skill instructions. Do not accept an update that adds network access,
   executable scripts, secrets, or destructive instructions without review.
5. Update the revision, date, and validation status in this document.
6. Commit the skill files, symlinks, lock file, and documentation together.

Do not enable automatic updates.

## Removing a skill

```bash
npx skills remove <skill-name> -y
```

Project scope is the default; do not pass `-g`.

Verify that the canonical directory, the `.claude/skills` link, and the
`skills-lock.json` entry are gone, then remove the row from the catalog and
commit.

## Adding or evaluating a skill

Before approving a skill:

1. Confirm the original repository, maintainer, and activity.
2. Read the full `SKILL.md` and every bundled resource; list executable scripts,
   network calls, credential use, downloads, and destructive instructions.
3. Check the license and whether redistribution is allowed.
4. Check the Agent Skills front matter (`name`, `description`) and required
   files.
5. Compare its rules with `AGENTS.md`; repository rules and permissions always
   prevail.
6. Verify compatibility with the agents actually used here, including any
   dependence on subagents, hooks, human interaction, or specific Git flows.
7. Prefer original sources. Do not install a skill only because it is popular,
   and do not copy the whole catalog of a provider.

Then install it in project scope, inspect the resulting files and symlinks,
and add it to the catalog with its revision and validation status. Never
install a skill automatically as a side effect of another skill.

## Deferred and rejected skills

Stack-specific skills were evaluated against the current repository, which has
no application code, frontend, or end-to-end test suite:

| Skill | Decision | Reason |
| --- | --- | --- |
| `vercel-react-best-practices` (`vercel-labs/agent-skills`) | Deferred | No React application exists yet. Re-evaluate when React is introduced. |
| `web-design-guidelines` (`vercel-labs/agent-skills`) | Deferred | No web interface exists yet. Re-evaluate when one is introduced. |
| `playwright-best-practices` (`currents-dev/playwright-best-practices-skill`) | Deferred | Playwright is not used. Re-evaluate when end-to-end tests are added. |
| `writing-plans` (`obra/superpowers`) | Rejected | Requires interactive plan review and an execution-method choice, references companion skills that are not installed (`subagent-driven-development`, `executing-plans`, `using-git-worktrees`), and prescribes a plan location and commit flow that duplicate this repository's conventions and the orchestrator's responsibilities. |
| `requesting-code-review` (`obra/superpowers`) | Rejected | Assumes dispatching a `general-purpose` reviewer subagent and a fixed review workflow. This duplicates Orca's orchestration and the repository's review process, and the required subagent capability is not guaranteed across agents. |

## Security notes

The installed skills were reviewed as third-party content before being
committed:

- None of the installed `SKILL.md` files require secrets, install packages, or
  perform downloads. They are Markdown instructions.
- `systematic-debugging` bundles `find-polluter.sh`, which repeatedly runs
  `npm test` and inspects the working tree to find a test that creates unwanted
  files. It is not run automatically and assumes an npm-based test setup.
- `find-skills` recommends `npx skills` commands and uses `-g` (global) in one
  example. This repository overrides that: use project scope and require
  authorization before installing anything.
- `skill-creator` bundles Python scripts and an evaluation viewer. They are
  **not run automatically**. Notable behavior if used:
  - `scripts/run_eval.py`, `scripts/improve_description.py`, and
    `scripts/run_loop.py` invoke `claude -p` as a subprocess and inherit the
    session's authentication and permissions.
  - `eval-viewer/generate_review.py` starts a local HTTP server on
    `127.0.0.1`/`localhost` and can open a browser. It may call `lsof` and send
    `SIGTERM` to a process using its port.
  - Generated reports reference Google Fonts over the network.
  - `scripts/quick_validate.py` imports `PyYAML`, which is not a project
    dependency.
  - The skill writes evaluation artifacts and may create
    `.claude/commands/` entries during evaluation runs.
- No skill may broaden GitHub permissions, filesystem access, or external
  service access. `AGENTS.md` and the orchestrator's permissions take
  precedence.

Residual risk: the upstream repositories can change and the evaluation scripts
can execute an agent with the caller's credentials. Only run those scripts on
trusted machines, in a sandbox when possible, and after re-reading the version
being used.

## Validation

Performed on 2026-10-19:

- `npx skills list` reports all five skills with the expected sources.
- Every installed directory contains a valid `SKILL.md` with `name` and
  `description` front matter.
- Installed files are byte-identical to the recorded upstream revisions
  (`diff -r`), including all bundled `skill-creator` resources.
- `.claude/skills/*` links are relative and resolve; no broken symlinks.
- Codex (0.153.4) and OpenCode (2.0.32) discovered the skills and selected
  `systematic-debugging` for a reproducible bug in a read-only prompt.
- Claude Code (2.1.220) discovery test could not run because the CLI was not
  authenticated in this environment. The `.claude/skills` links were verified
  structurally.
- Full behavior tests for debugging, TDD, and verification are **pending**:
  this repository has no application code or test framework, so there is no
  meaningful change to exercise. Re-run them when the first executable code
  and test suite are added.
