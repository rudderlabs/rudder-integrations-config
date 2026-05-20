## Definition Triplet Pattern
<!-- RUD-2749 -->
- Destination folders follow a repeatable triplet: `db-config.json` + `schema.json` + `ui-config.json`.
- Example anchors: `src/configurations/destinations/ga/`, `src/configurations/destinations/google_cloud_function/`.
- `db-config.json` drives metadata and routing behavior, while `schema.json` provides Ajv `configSchema` validation.

## Account Subtree Pattern
<!-- RUD-2749 -->
- Account definitions are nested and self-contained: `accounts/<account>/db-config.json`, `schema.json`, `ui-config.json`.
- Validation contract is centralized in `src/schemas/account/account-db-config-schema.json`, `account-schema-schema.json`, `account-ui-config-schema.json`.
- Naming convention is enforced in schema (`name` pattern `^[A-Z0-9_]+$`).

## Fixture-Driven Validation Pattern
<!-- RUD-2749 -->
- Test fixtures in `test/data/validation/destinations/*.json` are arrays of `{ config, result, err?, testTitle? }`.
- `test/validation.test.ts` loops fixture arrays and maps failing cases to exact expected Ajv error strings.
- This keeps behavioral checks decoupled from individual schema internals while still validating real integration keys.

## Template-to-Generated UI Pattern
<!-- RUD-2749 -->
- For destinations with heavy defaults, source of truth is `ui-config.jt` + `ui-default.json`.
- `scripts/preProcess.js` renders final `ui-config.json` via `JsonTemplateEngine.create(...).evaluate(...)`.
- `ga4_v2` contains all three template artifacts (`ui-config.jt`, `ui-default.json`, `ui-config.json`) and is the canonical example.
