# Architecture

> Component layout, internal relationships, data flow.
> Append-only. Agent-authored sections may optionally carry an HTML-comment tag
> (e.g., `<!-- pr:<id> -->`) identifying the writer/PR/run; human-authored
> sections are conventionally left untouched by automated runs.

## Config Data Model

<!-- RUD-2776 -->

- Integration definitions are filesystem-first: each integration lives under `src/configurations/{destinations|sources}/<name>/` with a `db-config.json`, `ui-config.json`, and `schema.json` triplet used by tooling and validation (e.g., `src/configurations/destinations/ga4_v2/`).
- Public validator exports are re-exported via `src/index.ts`, keeping consumer imports stable while implementation stays in `src/validator/index.ts` (`src/index.ts`, `src/validator/index.ts::validateConfig`).
- Runtime validation is split by concern: generic config schema checks via `validateConfig`, definition-level schema checks via `validateDestinationDefinitions` / `validateSourceDefinitions`, and account-definition checks via `validateAccountDefinitions` (`src/validator/index.ts:177`, `src/validator/index.ts:202`, `src/validator/index.ts:237`, `src/validator/index.ts:268`).

## Validation Flow

<!-- RUD-2776 -->

- Validator initialization compiles all integration `schema.json` files into an in-memory map keyed as `<type>___<name>` (`src/validator/index.ts::initAjvValidators`).
- Destination definitions have an extra policy layer beyond JSON Schema through `destinationDefinitionRules` and `applyAdditionalRulesValidation`, including secret/include key safety and connection-mode consistency (`src/validator/index.ts:30`, `src/validator/index.ts:144`, `src/validator/index.ts:232`).
- Test architecture mirrors the split: `test/validation.test.ts` verifies real repository integration configs while `test/validator/validator.test.ts` unit-tests validator behavior and rule edge cases (`test/validation.test.ts:200`, `test/validator/validator.test.ts:895`).

## Generation and Deployment Boundaries

<!-- RUD-2776 -->

- Generation scripts mutate repo artifacts from source configs: `scripts/preProcess.js` materializes `ui-config.json` from `.jt` templates and defaults, while `scripts/generateConstants.js` emits multi-language destination constants into `generated/` (`scripts/preProcess.js::main`, `scripts/generateConstants.js::generateFiles`).
- Schema maintenance is separated into a Python pipeline (`scripts/schemaGenerator.py`) with selectable update/check behavior, rather than being embedded in validator runtime (`scripts/schemaGenerator.py`, `package.json:37`).
- Control-plane mutation is isolated to deploy scripts with explicit dry-run/no-dry-run modes, reducing accidental writes during local workflows (`scripts/deployToDB.py::get_command_line_arguments`, `scripts/deployAccountsToDB.py::get_command_line_arguments`).

## Cross-cutting

<!-- RUD-2776 -->

- The repository enforces a config-as-data contract: filesystem definition triplets (`db-config.json`/`ui-config.json`/`schema.json`) feed both runtime validator compilation and deployment diff tooling, so shape drift impacts validation and control-plane updates together (`src/validator/index.ts::initAjvValidators`, `scripts/deployToDB.py::update_diff_db`, `src/configurations/destinations/ga4_v2/`).
- Security posture is layered rather than centralized: validator-level secret/include-key checks prevent client exposure, while deploy tooling relies on dry-run defaults and explicit no-dry-run opt-in to avoid accidental remote writes (`src/validator/index.ts:30`, `scripts/deployToDB.py::get_command_line_arguments`, `scripts/deployAccountsToDB.py::get_command_line_arguments`).
- Generation pipelines (`pre-process`, `generate:constants`) and strict CI test thresholds tie repo hygiene to script execution order; skipped generation can desync committed artifacts from source configs and break validation/test expectations (`package.json:30`, `package.json:43`, `package.json:44`, `jest.config.js:43`).
- Known technical debt is explicit in commented-out/ TODO validation rules, and the same risk is reflected in targeted rule tests; this signals deliberate temporary gaps rather than unobserved behavior (`src/validator/index.ts` TODO blocks, `test/validator/validator.test.ts:895`).

## INT-6540 — Rollback Deployment Ref Propagation

- Production rollback execution flows through `.github/workflows/rollback.yml` -> `.github/workflows/deploy-to-prod.yml` -> `.github/workflows/deploy.yml`.
- The deploy ref must be propagated from the rollback caller (`github.ref`) into `deploy-to-prod` and then into `deploy.yml` so rollback deploys the selected tag/branch instead of implicitly defaulting to `main`.
- Version/Slack metadata and deployed code should be derived from the same resolved ref to keep release reporting and actual deployed artifact aligned.

## INT-6502 — Destination Versions Archive Contract

- Destination deploy payload assembly in `scripts/deployToDB.py::update_diff_db` now includes a top-level `versions` object built from `<definition>/versions/<major>/`.
- `build_versions_archive` reads each archived major's triplet (`db-config.json`/`schema.json`/`ui-config.json`). On disk an archived major carries a flat `version` (major.minor string) plus sibling `status`/`retirementDate?`/`migrationDocsUrl?`, mirroring the root db-config; the assembled `versions[major]` entry renames `version` to `number` and carries `config`/`configSchema`/`uiConfig`. It raises on a missing/invalid `version`, an out-of-enum `status`, or a missing config/configSchema/uiConfig slice rather than emitting a partial entry.
- `versions` is a deploy-payload contract only: it is assembled at deploy time and is NOT part of the on-disk `db-config-schema.json`, which validates authored root `db-config.json` files (these carry `version` but never `fallbackVersion` or `versions`; `fallbackVersion` is computed on the fly downstream).
- When no `versions/` directory exists, payload construction sets `versions` to `{}` to allow jsondiff-driven clearing of previously persisted archive state.
- Current deploy file-loading behavior remains root-first (`db-config.json`/`ui-config.json`/`schema.json` at destination root), so nested version assets affect deployment only through explicit archive-building logic.

## INT-6597 — Hidden Gate Schema Contract

- `options.hidden` in both destination and source `db-config-schema.json` files is a 3-state union: boolean blanket hiding, a legacy `{ featureFlagName, featureFlagValue }` single-flag object, or `{ gate: { flags, condition } }` for one or more Flagsmith flags or billing features. `hidden.gate` uses hide-when semantics: the integration is hidden when the configured flag reduction matches. Gate flag items require `name` and boolean `value`, reject unknown properties, and flag arrays with at least two items require `condition`.

## INT-6593 — Deployment Notification Workflow Boundary

- Deployment Slack notifications are implemented in GitHub Actions workflows rather than application code.
- The reusable deployment workflow `.github/workflows/deploy.yml` owns the Slack notification behavior and declares workflow-call secrets `SLACK_BOT_TOKEN` and `SLACK_RELEASE_CHANNEL_ID`.
- Caller workflows pass those Slack secrets through deployment wrappers, including `.github/workflows/deploy-to-prod.yml`, `.github/workflows/deploy-to-staging.yml`, `.github/workflows/deploy-to-dev.yml`, `.github/workflows/manual-deploy.yml`, and `.github/workflows/rollback.yml` via the production deploy wrapper.
