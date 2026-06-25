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
