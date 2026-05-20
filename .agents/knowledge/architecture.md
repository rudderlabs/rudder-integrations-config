## Validation Runtime
<!-- RUD-2749 -->
- Public API is re-exported from `src/index.ts` (`init`, `validateConfig`, `validateSourceDefinitions`, `validateDestinationDefinitions`, `validateAccountDefinitions`).
- Validator registry is built in `src/validator/index.ts` via `initAjvValidators()` scanning `src/configurations/**/schema.json`.
- Per-integration runtime validation uses `validateConfig(definitionName, config, intgType, throwErrorOnMissingValidations)` and Ajv-compiled `configSchema`.
- Definition-level checks are split into JSON-schema validation (`src/schemas/**/db-config-schema.json`) and custom destination rules in `destinationDefinitionRules`.

## Config Asset Topology
<!-- RUD-2749 -->
- Destination definitions live under `src/configurations/destinations/<destination>/` with `db-config.json`, `schema.json`, and `ui-config.json`.
- Account definitions are nested under `src/configurations/destinations/<destination>/accounts/<account>/` and validated against `src/schemas/account/account-*.json`.
- Fixture parity is expected between destination folder names and fixture filenames in `test/data/validation/destinations/*.json`.
- Representative anchors: `src/configurations/destinations/ga4_v2/db-config.json`, `src/configurations/destinations/google_cloud_function/schema.json`.

## UI Preprocess Pipeline
<!-- RUD-2749 -->
- `scripts/preProcess.js` is the preprocess entrypoint (`main()`).
- Template source is `ui-config.jt` (`getUiConfigTemplate`) and defaults come from `ui-default.json` (`getUiDefaultData`).
- Rendering uses `@rudderstack/json-template-engine` and emits concrete `ui-config.json` files in destination folders.
- Current flow iterates destination directories from `getDestinationNames()` and only processes integrations with `ui-default.json` present.

## Test-Oriented Architecture
<!-- RUD-2749 -->
- `test/validation.test.ts` drives config validation using fixture payloads loaded by `getIntegrationData()`.
- Destination/source/account definition conformance is verified by importing live `db-config.json` files and calling the respective validator APIs.
- Command-line filtering for large runs is handled via Commander options `--destinations` and `--sources`.

## Cross-cutting
<!-- RUD-2749 -->
- Naming and key-shape coupling across destination folders, accounts, and fixtures is documented in `conventions.md` and `patterns.md`.
- Operational risks around preprocess and schema/fixture drift are tracked in `concerns.md`.
- Invocation and execution surfaces for these flows are listed in `entry-points.md` and `stack.md`.
