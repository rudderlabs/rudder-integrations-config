## Runtime Languages
<!-- RUD-2749 -->
- TypeScript for validator library and tests (`src/**/*.ts`, `test/**/*.ts`).
- Node.js JavaScript for repo scripts like `scripts/preProcess.js`.
- Python for schema/deploy utilities (`scripts/schemaGenerator.py`, `scripts/deployToDB.py`, `scripts/deployAccountsToDB.py`).

## Core Libraries
<!-- RUD-2749 -->
- `ajv` (`^8.18.0`) for config and definition schema validation (`src/validator/index.ts`).
- `glob` for schema discovery during validator initialization.
- `@rudderstack/json-template-engine` for generating `ui-config.json` from templated sources.
- `commander` in `test/validation.test.ts` to scope destination/source test execution.

## Tooling and Test Stack
<!-- RUD-2749 -->
- `jest` + `@swc/jest` for unit/integration tests (`npm test`, `npm run test:ci`).
- `eslint` + `prettier` via `npm run lint` and formatting scripts.
- `black` for Python formatting via `npm run format:py`.
