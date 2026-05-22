# Stack

> Dependencies, frameworks, tooling.
> Append-only. Agent-authored sections may optionally carry an HTML-comment tag
> (e.g., `<!-- pr:<id> -->`) identifying the writer/PR/run; human-authored
> sections are conventionally left untouched by automated runs.

## Languages and Runtime
<!-- RUD-2776 -->

- Node/TypeScript package (`package.json` main `src/index.ts`) with strict TS compiler settings and CommonJS output (`package.json`, `tsconfig.json`).
- Python 3 scripting layer for schema generation, deployment, and validation utilities (`scripts/schemaGenerator.py`, `scripts/deployToDB.py`, `scripts/deployAccountsToDB.py`).

## Core Libraries
<!-- RUD-2776 -->

- Validation/runtime deps: `ajv@^8.18.0` and `glob@^9.3.2` (`package.json` dependencies).
- Template processing for UI-config generation: `@rudderstack/json-template-engine@^0.13.3` (`package.json` devDependencies, `scripts/preProcess.js`).
- Test/build toolchain: `jest@^29.5.0`, `@swc/jest@^0.2.24`, `typescript@^5.0.2`, `eslint@^8.37.0`, `prettier@^2.8.7` (`package.json`).

## Tooling and Automation
<!-- RUD-2776 -->

- Jest runs with 100% global coverage thresholds and SWC transform for TS/JS tests (`jest.config.js:43`, `jest.config.js:172`).
- Husky + lint-staged enforce formatting and Python black on commit paths (`package.json:30`, `package.json` `lint-staged`).
- Schema/definition lifecycle tooling is script-heavy (`scripts/schemaGenerator.py`, `scripts/validate_account_definitions.py`, `scripts/run-schema-validation.sh`).

## Generated Assets
<!-- RUD-2776 -->

- Language-specific destination constants are generated into `generated/` from template files in `templates/` via `npm run generate:constants` (`package.json:44`, `scripts/generateConstants.js::generateFiles`).
