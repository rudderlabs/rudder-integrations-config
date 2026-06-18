# Mistakes

> Post-mortem entries from observed failures: CI failures, reverts on prior PRs,
> prod incidents. Accrues over time — bootstrap leaves this empty.
> Append-only. Agent-authored sections may optionally carry an HTML-comment tag
> (e.g., `<!-- pr:<id> -->`) identifying the writer/PR/run; human-authored
> sections are conventionally left untouched by automated runs.

## INT-6540 — Assuming PR Context Exists During Rollback

- `deploy-to-prod` previously depended on pull request context while also passing `ref: main` downstream, which caused rollback runs started from tags to risk deploying `main` instead of the intended tag.
- Corrective rule: for rollback/reusable invocations, never infer deploy ref from PR-only fields; require explicit ref propagation from the caller.

## INT-6502 — Revalidate Findings Against Current Diff

- Review findings must be re-checked against the latest PR state before escalating them; if a referenced file/test suite has been removed, the finding is stale and should be withdrawn.
- In this task cycle, prior concern about `test/test_deployToDB.py` teardown/global-state restoration became invalid once that test file was removed from the PR.
