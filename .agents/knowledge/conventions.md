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
- Device/hybrid support implies `includeKeys` presence in destination definition config (`src/validator/index.ts:60`).

## Change Workflow Norms
<!-- RUD-2776 -->

- Pre-commit flow expects preprocessing and tests before staged-linting (`package.json:30`).
- Schema lifecycle is CLI-driven with separate check/update scripts for sources and destinations (`package.json:33`, `package.json:37`, `scripts/schemaGenerator.py`).
- Display-name integrity is guarded by dedicated scripts, including staged-only mode (`package.json:45`, `package.json:46`).

## RUD-2776 — Knowledge Bootstrap Invariants

- Initial knowledge bootstrap for this repository is expected to create exactly seven files under `.agents/knowledge`: `architecture.md`, `patterns.md`, `conventions.md`, `stack.md`, `entry-points.md`, `concerns.md`, and `mistakes.md`.
- During first bootstrap, `mistakes.md` remains template-only and should not receive synthetic incident entries.

## RUD-2776 — Generated UI Config Edit Discipline

- For destinations using custom mappings, `ui-config.json` is a generated artifact derived from `ui-config.jt` and `ui-default.json` through pre-process flow.
- To avoid regeneration drift, behavior changes should be made in the template/default inputs when applicable, not only in generated `ui-config.json`.
