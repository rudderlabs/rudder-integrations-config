# Stack & Dependencies

> Project technology stack, frameworks, and key dependencies.
> This file is append-only - agents add discoveries, never delete.

(Add stack information as you discover it)

## Runtime / test tools

- **Node.js / TypeScript** — config repo tooling
- **Jest** — test runner (`npx jest --testPathPattern=validation.test.ts --coverage=false` for fast targeted runs)
- **AJV** — JSON Schema validation (draft-07); used by `validation.test.ts`
- **ESLint** — lint (`npm run lint`; reports written to `reports/eslint.json`)
- **Python 3** — schema generator (`scripts/schemaGenerator.py`) and deploy scripts (`scripts/deployToDB.py`, `scripts/deployAccountsToDB.py`)

## Schema validators

- `src/schemas/destination/db-config-schema.json` — validates destination db-config.json
- `src/schemas/account/account-db-config-schema.json` — validates account db-config.json

## Deploy tooling

- `python3 scripts/deployToDB.py` — deploys destination definitions to control-plane DB
- `python3 scripts/deployAccountsToDB.py` — deploys account configurations to control-plane DB
- Both accept positional args or env vars: `CONTROL_PLANE_URL`, `API_USER`, `API_PASSWORD`
- `--dry-run` and `--verbose` flags available on both scripts
