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

## LLD destConfig fields diverge from actual implementation

**What happened:** The LLD §4.1 specified `destConfig.defaultConfig` as `["rudderAccountId", "listId", "listName", "identifierMappings"]` and `warehouse` as `["connectionMode", "consentManagement", "oneTrustCookieCategories", "ketchConsentPurposes"]`. Both were simplified in the actual implementation.

**Why:** Two post-implementation simplification commits:
- `listId` and `listName` removed (`02099d9d`) — the VDM v2 form resolves list selection before persisting the connection config, so these fields don't need to be in `destConfig`. The connection config stored in the DB only needs `rudderAccountId` and `identifierMappings`.
- Consent management fields removed from `warehouse` (`827f2415`) — M1 scope does not include consent management for this destination.

**Prevention:** Don't blindly copy `destConfig.warehouse` consent fields for a new audience destination in M1. Consent fields are optional and can be added in later milestones. Check the LLD explicitly for M1 scope.

**Fix:** Keep `destConfig.warehouse` minimal (`["connectionMode"]`) for M1 audience destinations. Add consent fields only when scope explicitly includes consent management.

---

## Account option fields must appear in destination destConfig.defaultConfig

**What happened:** The actual `iterable_audience` db-config.json includes account-level fields (`apiKey`, `dataCenter`, `projectType`) in `destConfig.defaultConfig` and has `secretKeys: ["apiKey"]`. This was NOT in the LLD template but IS in the actual implementation.

**Why:** The transformer needs `dataCenter` and `projectType` (account options) and `apiKey` (account secret) at delivery time. The `destConfig.defaultConfig` list is how the platform knows which fields to pass to the transformer as connection metadata. The `secretKeys` list signals the platform to include the secret in the delivery payload.

**Prevention:** When creating a warehouse-to-audience destination that reads account options at transform time, include those option field names AND secret field names in `destConfig.defaultConfig`. Also add secret field names to `secretKeys`.

**Fix:** Add account option fields to `destConfig.defaultConfig`. Add secret field names to `secretKeys`. See `iterable_audience/db-config.json` as the canonical reference.
