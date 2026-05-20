## Naming Conventions
<!-- RUD-2749 -->
- Destination directory keys are lowercase identifiers under `src/configurations/destinations/` and are used as validator lookup keys.
- Account definition `name` must be uppercase snake case (`^[A-Z0-9_]+$`) per `src/schemas/account/account-db-config-schema.json`.
- Account `type` is expected to match integration key semantics (lowercase destination/source key).

## Validation Error Conventions
<!-- RUD-2749 -->
- Runtime config errors are flattened to `"<instancePath> <message>"` in `src/validator/index.ts` (`validateConfig`).
- Multiple validation issues are thrown as `JSON.stringify(errorMessages)`; tests should assert exact array-string payloads.
- Unknown definitions are only hard-fail when `throwErrorOnMissingValidations=true`.

## Schema Strictness Conventions
<!-- RUD-2749 -->
- Runtime per-integration validators are built with permissive Ajv flags (`strict: false`) in `src/validator/index.ts`.
- Definition validators (`validateDestinationDefinitions`, `validateSourceDefinitions`, `validateAccountDefinitions`) run with strict Ajv flags.
- Destination definitions also enforce custom non-schema rules (`destinationDefinitionRules`) around `secretKeys`, `includeKeys`, and connection modes.

## Fixture Conventions
<!-- RUD-2749 -->
- Destination fixture filenames in `test/data/validation/destinations/` should match destination folder names in `src/configurations/destinations/`.
- Positive cases set `"result": true`; negative cases include deterministic `err` arrays aligned with current Ajv output.
