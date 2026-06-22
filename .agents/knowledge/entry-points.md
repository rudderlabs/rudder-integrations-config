# Entry Points

> Key entry-point files: read these first to orient in this repo.
> Append-only. Agent-authored sections may optionally carry an HTML-comment tag
> (e.g., `<!-- pr:<id> -->`) identifying the writer/PR/run; human-authored
> sections are conventionally left untouched by automated runs.

## Primary Orientation Files

<!-- RUD-2776 -->

- `README.md`: repository purpose, config model, and deploy/dry-run behavior overview.
- `src/index.ts`: stable export surface for validation APIs (`validateConfig`, `init`, definition validators).
- `src/validator/index.ts`: core validation engine and destination-specific rule enforcement.

## Operational Script Entrypoints

<!-- RUD-2776 -->

- `scripts/preProcess.js`: template-driven `ui-config.json` materialization from `ui-config.jt` + `ui-default.json` (`scripts/preProcess.js::main`).
- `scripts/schemaGenerator.py`: source/destination schema generation and diff/update flow.
- `scripts/deployToDB.py` and `scripts/deployAccountsToDB.py`: control-plane deployment tooling with dry-run defaults and explicit `--no-dry-run` activation.

## Test Entrypoints

<!-- RUD-2776 -->

- `test/validation.test.ts`: broad integration validation across destinations/sources/accounts.
- `test/validator/validator.test.ts`: unit-level behavior and edge-case tests for validator internals.

## INT-6594 — Facebook Lead Ads Source Definitions

- The legacy FBLA source definition is `src/configurations/sources/facebook_lead_ads/db-config.json`; for INT-6594 it already had `options.isBeta: true` and `options.hidden: true`, so hidden-only rollback work should not be applied there by mistake.
- The Facebook Lead Ads native source definition is `src/configurations/sources/facebook_lead_ads_native/db-config.json`; PR #2477 made this source GA by removing `options.isBeta: true` and a feature-flagged `options.hidden` object from that definition.
