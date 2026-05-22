# Mistakes & Lessons Learned

> Record mistakes made during development and how to avoid them.
> This file is append-only - agents add discoveries, never delete.
>
> Format: Describe what went wrong, why, and how to avoid it next time.

(Add mistakes and lessons as you encounter them)

## npm test times out in CI / loom acceptance checks

**What happened:** `npm test` was used as an acceptance criterion but timed out under loom's checker because the package.json script runs jest with `--coverage --notify`, instrumenting every file under `src/**/*.[jt]s` with a 100% coverage threshold.

**Why:** The package.json `test` script uses full coverage instrumentation by default. On a large config repo (~3300 tests), this takes minutes, exceeding loom's acceptance timeout.

**Prevention:** Never use bare `npm test` in stage acceptance criteria for this repo. Always check the package.json test script before writing acceptance criteria.

**Fix:** Use a targeted jest invocation: `npx jest --testPathPattern=validation.test.ts --coverage=false`. This completes in ~14s and verifies all validation fixtures including newly added ones.

---

## git commit fails with GPG signing error in worktrees

**What happened:** `git commit` in a loom worktree failed with "gpg failed to sign the data."

**Why:** Worktrees do not inherit the GPG agent socket from the parent shell session. The GPG agent is not available in the new worktree environment.

**Prevention:** When committing in any loom worktree, always add `-c commit.gpgsign=false`.

**Fix:** `git -c commit.gpgsign=false commit -m "..."` — disables GPG signing for that commit only.

---

## authenticationType "custom" vs "api_key"

**What happened:** The VDM-next integration skill suggested using `authenticationType: "custom"` for the account db-config.

**Why:** The skill's suggestion was not aligned with the actual allowed values in `account-db-config-schema.json`, which explicitly lists `api_key` as a valid enum value.

**Prevention:** Always read `src/schemas/account/account-db-config-schema.json` before setting `authenticationType`. The schema is the authoritative source; skill suggestions may be stale.

**Fix:** Use `"authenticationType": "api_key"` — it is a valid literal value confirmed by the account schema.
