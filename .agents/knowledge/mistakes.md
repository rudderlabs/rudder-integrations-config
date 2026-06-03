# Mistakes

> Post-mortem entries from observed failures: CI failures, reverts on prior PRs,
> prod incidents. Accrues over time — bootstrap leaves this empty.
> Append-only. Agent-authored sections may optionally carry an HTML-comment tag
> (e.g., `<!-- pr:<id> -->`) identifying the writer/PR/run; human-authored
> sections are conventionally left untouched by automated runs.

## `commitlint` CI fails on non-conventional commit messages
<!-- pr:2492 -->

- **Symptom:** The `commitlint` GitHub Action check fails with `subject may not be empty [subject-empty]` / `type may not be empty [type-empty]` while every other check passes.
- **Root cause:** `commitlint.config.js` extends `@commitlint/config-conventional`, and the CI action runs with `commitDepth: 1`, so the **latest commit on the PR branch** must be a valid Conventional Commit (`type: subject`). Copilot Autofix commits land with the message `Potential fix for pull request finding`, which has no type or subject and fails the lint.
- **Fix:** Reword the offending commit(s) to Conventional Commit format, e.g. `git commit --amend --no-verify -m "docs: <subject>"`, then `git push --force-with-lease`. Only the HEAD commit is linted (`commitDepth: 1`), so at minimum HEAD must conform.
- **Gotcha — `--no-verify` is required locally:** The husky `pre-commit` hook is broken in fresh checkouts (`.husky/_/husky.sh: No such file or directory`), so a plain `git commit --amend` aborts with exit status 1. Pass `--no-verify` to bypass the local hook (CI re-runs the real checks anyway).
- **Prevention:** When applying Copilot Autofix suggestions or any auto-generated commits, reword them to Conventional Commit format before pushing. Prefer rewording the HEAD commit at minimum; squash/reword the whole autofix series if the branch has several `Potential fix for pull request finding` commits.
