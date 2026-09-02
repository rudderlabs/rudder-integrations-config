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

## INT-6598 — Do Not Equate Permissive Account Objects With Strict Gates

- During INT-6598 inspection, `src/schemas/account/account-db-config-schema.json` was first read as rejecting `displayOptions.hidden.gate` because the visible legacy branch listed only `featureFlagName` and `featureFlagValue`.
- The correction was that the account hidden object branch had no `required` list and no `additionalProperties: false`, so arbitrary object keys such as `gate` could pass validation while still not enforcing the strict `hidden.gate` contract.
- When reviewing account visibility changes, distinguish permissive acceptance from schema enforcement: a passing account hidden object is not evidence that `flags[].name`, mandatory `flags[].value`, or required multi-flag `condition` are being validated.

## INT-6644 — Do Not Use Braze DB Config for Field Visibility

- During INT-6644 orientation, Braze prerequisite coverage was initially attributed to `src/configurations/destinations/braze/db-config.json`; inspection corrected that per-field source connection-mode visibility lives in `src/configurations/destinations/braze/ui-config.json`.
- Corrective rule: for Braze per-field UI visibility or prerequisite coverage changes, inspect and edit the field object's `preRequisites.fields` in `ui-config.json`; use `db-config.json` only for included config keys and supported source type metadata.

## INT-7070 — Keep Consent Management Source Coverage Complete

- CI failed in the Report Code Coverage workflow when OpenAI Ads declared `consentManagement` only for web/cloud while `supportedSourceTypes` also included mobile, warehouse, and other source types; `test/consentManagementFieldsIntegrity.test.ts` requires a `consentManagement` field for every supported source type.
- Corrective rule: when a destination supports `consentManagement`, list it under every supported source type in `db-config.json` `config.destConfig` and regenerate `schema.json` so `configSchema.properties.consentManagement.properties` has the same source keys as supported non-warehouse `supportedSourceTypes`.
- Later review clarified OpenAI Ads should not support `warehouse`; do not add warehouse just to satisfy consent-management coverage.
- For web-only source-scoped settings, use `additionalProperties: false` on the UI field and ensure schema generation preserves it for source-dependent `singleSelect` fields, rather than narrowing `consentManagement` source coverage.
- Code quality checks can fail on knowledge-only markdown formatting drift: `npm run lint` runs Prettier across repository markdown files and then checks `git diff --exit-code`, so `.agents/knowledge/*.md` updates must be Prettier-clean and end with a trailing newline before push.
