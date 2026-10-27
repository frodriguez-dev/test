## Summary

[What changed and why.]

## Related issue

Closes #[issue number]

## Changes

- [Main change]
- [Tests or documentation updated]

## Validation

- [ ] Backend checks (`uv run --env-file .env pytest`, `uv run ruff check .`, `uv run ruff format --check .`)
- [ ] Frontend checks (`pnpm check`)
- [ ] Documentation-only change reviewed; no runtime checks apply

Commands and results:

```text
[paste the commands run and their outcome]
```

## Risks and limitations

[Known gaps, checks that could not run, or decisions that need review.]

## Review readiness

Review policy: [`REVIEW.md`](../REVIEW.md).

- [ ] The change stays within the issue scope.
- [ ] Tests and documentation were updated where needed.
- [ ] No secrets or generated runtime files are included.
- [ ] Findings follow the severity, evidence, and fingerprint contracts in `REVIEW.md`.
- [ ] A human approval names the current head SHA; no agent approved or merged this pull request.
- [ ] This pull request is ready for human review; it will not be merged by an agent.
