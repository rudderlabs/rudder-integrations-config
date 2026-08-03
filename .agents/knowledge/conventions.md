# Conventions

> Coding conventions and naming schemes — things a linter can't catch.
> Append-only. Agent-authored sections may optionally carry an HTML-comment tag
> (e.g., `<!-- pr:<id> -->`) identifying the writer/PR/run; human-authored
> sections are conventionally left untouched by automated runs.

## Directory and Naming Shape

<!-- RUD-2776 -->

- Integration folder naming is typically snake_case under `src/configurations/{destinations|sources}/`, with some legacy exceptions (e.g., `src/configurations/destinations/ga4_v2/`, `src/configurations/destinations/spotifyPixel/`); each folder carries canonical config filenames (`db-config.json`, `ui-config.json`, `schema.json`).
- Generated SDK constants are language-suffixed files under `generated/` and must align with templates under `templates/*.template` (`scripts/generateConstants.js:9`, `templates/`).
- Repo-local automation skills live under `.claude/skills/` and are discovery artifacts, not normal edit targets for integration changes (`.claude/skills/migrate-to-accounts-framework/SKILL.md`).

## Validation Contract Conventions

<!-- RUD-2776 -->

- Destination/source/account definition validations are expected to resolve `true` on valid configs and throw on invalid configs; tests use this contract consistently (`test/validation.test.ts:200`, `test/validation.test.ts:341`, `test/validation.test.ts:401`).
- Secret handling convention is explicit: if a key appears in `includeKeys`, it must also appear in `excludeKeys` when the key is secret (`src/validator/index.ts:30`, `test/validator/validator.test.ts:895`).
- Device/hybrid support implies `includeKeys` presence in destination definition config (`src/validator/index.ts:65`).

## Change Workflow Norms

<!-- RUD-2776 -->

- Pre-commit flow expects preprocessing and tests before staged-linting (`package.json:30`).
- Commit messages must follow Conventional Commits (`commitlint.config.js` extends `@commitlint/config-conventional`); the `commitlint` CI check lints the latest commit (`commitDepth: 1` in `.github/workflows/commitlint.yml`), so any auto-generated commit (e.g. Copilot Autofix `Potential fix for pull request finding`) must be reworded to `type: subject` before push. Record future occurrences in `mistakes.md`.
- Schema lifecycle is CLI-driven with separate check/update scripts for sources and destinations (`package.json:33`, `package.json:37`, `scripts/schemaGenerator.py`).
- Display-name integrity is guarded by dedicated scripts, including staged-only mode (`package.json:45`, `package.json:46`).

## RUD-2776 — Knowledge Bootstrap Invariants

- Initial knowledge bootstrap for this repository is expected to create exactly seven files under `.agents/knowledge`: `architecture.md`, `patterns.md`, `conventions.md`, `stack.md`, `entry-points.md`, `concerns.md`, and `mistakes.md`.
- During first bootstrap, `mistakes.md` remains template-only and should not receive synthetic incident entries.

## RUD-2776 — Generated UI Config Edit Discipline

- For destinations using custom mappings, `ui-config.json` is a generated artifact derived from `ui-config.jt` and `ui-default.json` through pre-process flow.
- To avoid regeneration drift, behavior changes should be made in the template/default inputs when applicable, not only in generated `ui-config.json`.

## INT-6524 — Feature-Flag Rename Scope

- Destination visibility gating for Custom Audience is configured in `src/configurations/destinations/custom_audience/db-config.json` at `options.hidden.gate.flags[].name`; when renaming that key, keep the repo change localized to the definition file if repo-wide search confirms no other in-repo references.
- For this class of definition-key rename, validate scope with targeted string search across `src/`, `generated/`, and `test/` before expanding into generator or test changes.

## INT-6529 — Klaviyo Definition Edit Scope

- Klaviyo destination config is maintained as a hand-authored JSON triplet under `src/configurations/destinations/klaviyo/` (`db-config.json`, `ui-config.json`, `schema.json`) rather than the template-driven `ui-config.jt` + `ui-default.json` flow used by some other destinations.
- For Klaviyo changes, treat `ui-config.json` and `schema.json` as a synchronized pair for `apiVersion` enum/default behavior; updating only one side creates control-plane/UI-vs-schema drift and downstream validation failures.
- Klaviyo destination validation fixtures are maintained in `test/data/validation/destinations/klaviyo.json`; any new version-path support should add or update fixture coverage there.

## INT-6594 — Hidden-Only GA Rollback Semantics

- For Facebook Lead Ads native GA rollback work, restoring hidden-only behavior means re-adding the feature-flagged `options.hidden` object in `src/configurations/sources/facebook_lead_ads_native/db-config.json` while leaving `options.isBeta` absent.
- Do not conflate `facebook_lead_ads_native` with the separate `facebook_lead_ads` source; the latter can remain hidden and beta while native visibility is controlled independently.

## INT-6604 — Destination Config Flag Schema Gate

- Destination definition metadata flags under the `config` object in `src/configurations/destinations/<name>/db-config.json` are schema-gated by `src/schemas/destinations/db-config-schema.json`, where `config.additionalProperties` is false. When adding a new destination `config` flag such as `supportsVisualMapperV2`, add the matching schema property too, otherwise broad destination validation rejects the edited definitions.

## INT-6644 — Braze Prerequisite Coverage Alignment

- For Braze fields matching broad connection-mode coverage, keep `preRequisites.condition` as `or` and normalize `preRequisites.fields` to the 18 unique source/mode pairs: cloud for `cloud`, `web`, `android`, `androidKotlin`, `ios`, `iosSwift`, `flutter`, `reactnative`, `unity`, `amp`, `cordova`, `shopify`, and `warehouse`; hybrid for `web`, `android`, `androidKotlin`, `ios`, and `iosSwift`.
- During INT-6644, `enableSubscriptionGroupInGroupCall`, `enableNestedArrayOperations`, and `sendPurchaseEventWithExtraProperties` were aligned to that 18-pair coverage without adding `useEcommerceRecommendedEvents` when it was absent from the local checkout.

## INT-6696 — Destination Audience Support Schema Coupling

- Destination `config.isAudienceSupported` is authored in each destination's `src/configurations/destinations/<name>/db-config.json` and is schema-gated by `src/schemas/destinations/db-config-schema.json`; restoring or changing that flag requires keeping the destination configs and destination meta-schema aligned.
- Treat `config.isAudienceSupported` and `config.supportsVisualMapperV2` as a guarded combination: PR #2555 added a destination schema exclusion that rejects audience support when Visual Mapper V2 support is present/enabled, so reintroducing legacy audience support may require an intentional schema change, not only per-destination JSON edits.

## INT-6150 — Delta Lake Azure Blob Naming

- The Databricks Delta Lake Azure storage provider value is exactly `AZURE_BLOB`; do not use `AZUREBLOB` when wiring UI conditions, schema branches, or persisted config behavior.
- The Azure Blob hierarchical namespace toggle is named `enableHierarchicalNamespace`, defaults false in UI config, and is shown only when `bucketProvider` is `AZURE_BLOB` and `useRudderStorage` is false.

## AI-1226 — Heap Legacy UI Config Shape

- Heap `ui-config.json` uses the legacy array field shape, so new fields should follow that local style (`value`, option `name`, and `defaultOption`) instead of newer destinations' `configKey`/`label`/`default` shape.
- `scripts/schemaGenerator.py` recognizes old-format destination fields through `value` plus `defaultOption`; copying newer Mixpanel-style field keys literally into Heap can make generation/validation tooling miss the setting.

## SDK-5126 — Amplitude Browser SDK Default Sync

- Amplitude Browser SDK default changes must keep `src/configurations/destinations/am/schema.json` `configSchema.properties.sdkVersion.properties.web.default` and the `ui-config.json` SDK Version singleSelect default synchronized; after SDK-5126 both default to `2` while enum/options still allow both `1` and `2`.
- Treat Amplitude `sdkVersion.web` condition blocks as behavior gates, not automatic migration targets: SDK-5126 intentionally changed only new-destination defaults and stale UI copy, leaving existing conditional UI blocks keyed on `sdkVersion.web` unchanged so explicit stored values and v1 selection remain supported.

## INT-6916 — Warehouse Sync Granularity Flag

- Warehouse destination UI sync-frequency options for high-granularity intervals should use the existing Flagsmith flag `AMP_enable-high-granularity-wh-syncs`; the 10-minute option follows the same flag convention as the existing 5-minute and 15-minute options across the warehouse destination `ui-config.json` files unless product explicitly supplies a different flag.
- Warehouse destination schema/UI option changes such as `syncFrequency` should add validation fixture cases under `test/data/validation/destinations/<destination>.json` for each affected warehouse integration, so broad fixture-driven validation covers every destination directly rather than relying only on focused validator coverage.

## AI-1266 — S3 Datalake Time Window Layout Field Contract

- S3 Datalake `timeWindowLayout` is exposed as an immutable legacy-shape optional `singleSelect` in `src/configurations/destinations/s3_datalake/ui-config.json`; keep `required: false` even though the field has a `defaultOption`.
- The S3 Datalake "Default (YYYY/MM/DD/HH)" option and `defaultOption.value` should both use the empty string, and the field should be gated with `preRequisiteField: { "name": "useGlue", "selectedValue": true }` so it is shown only when AWS Glue registration is enabled.
- For S3 Datalake, `src/configurations/destinations/s3_datalake/schema.json` keeps `timeWindowLayout` as a loose string with `rs-immutable: true`; schema generation may warn that it would add enum/default details from the UI field, but AI-1266 intentionally avoided making the schema stricter than the requested contract.
- S3 Datalake destination UI/config additions such as `timeWindowLayout` should include focused coverage: add persisted config cases to `test/data/validation/destinations/s3_datalake.json` and assert the UI field contract in `test/validation.test.ts` when the UI shape is part of the change.
