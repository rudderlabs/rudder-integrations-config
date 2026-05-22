# Entry points

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
