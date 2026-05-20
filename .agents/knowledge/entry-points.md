## Programmatic Entry Points
<!-- RUD-2749 -->
- `src/index.ts` is the public surface that re-exports validator APIs from `src/validator/index.ts`.
- Primary methods: `init()`, `validateConfig()`, `validateDestinationDefinitions()`, `validateSourceDefinitions()`, `validateAccountDefinitions()`.

## Script Entry Points (NPM)
<!-- RUD-2749 -->
- `npm run pre-process` -> `node scripts/preProcess.js` (template-driven UI config generation).
- `npm test` / `npm run test:ci` -> Jest validation suites including fixture-based destination tests.
- Schema workflows: `check:schema:*` and `update:schema:*` scripts call `scripts/schemaGenerator.py` for source/destination schema maintenance.

## Validation Harness Entry Points
<!-- RUD-2749 -->
- `test/validation.test.ts` supports CLI filters through `--destinations` and `--sources`.
- It dynamically reads `src/configurations/{destinations|sources}` and `test/data/validation/{destinations|sources}` to build test matrices.
- Definition checks import live `db-config.json` files, ensuring tests validate current repository state.

## Operational Entry Points
<!-- RUD-2749 -->
- Deployment utilities begin at `scripts/deployToDB.py` and `scripts/deployAccountsToDB.py`.
- Local convenience scripts `deploy:db:local` and `deploy:accounts:local` in `package.json` wire preprocess + deploy flows.
