# Architecture

> High-level component relationships, data flow, and module dependencies.
> This file is append-only - agents add discoveries, never delete.

(Add architecture diagrams and component relationships as you discover them)

## rudder-integrations-config repository structure

This repo is the central configuration store for all RudderStack source and destination integrations.

### Directory layout

- `src/configurations/destinations/<name>/` — one directory per destination
  - `db-config.json` — metadata, capabilities, account bindings
  - `schema.json` — AJV validation schema (configSchema key)
  - `ui-config.json` — dashboard UI rendering (uiConfig.baseTemplate)
  - `accounts/<account_name>/` — account credential triads (same three files, secretSchema instead of configSchema)
- `src/schemas/destination/db-config-schema.json` — authoritative JSON Schema validator for destination db-config files
- `src/schemas/account/account-db-config-schema.json` — authoritative JSON Schema validator for account db-config files
- `test/data/validation/destinations/<name>.json` — AJV test fixtures for each destination
- `scripts/deployToDB.py` — deploys destination definitions to control-plane DB
- `scripts/deployAccountsToDB.py` — deploys account configurations to control-plane DB

### Auto-discovery

`validation.test.ts` scans `src/configurations/destinations/` via `fs.readdirSync`. **No central registry exists.** Adding a new destination directory is sufficient for the test suite to pick it up. Same principle applies to account triads nested under the destination directory.

### Account binding

Destinations reference accounts through `config.supportedAccountDefinitions.rudderAccountId: [<ACCOUNT_NAME>]` in their `db-config.json`. The account's `db-config.json` `name` field must match exactly.

### Schema separation

- Destination config validated against `configSchema` key in `schema.json`
- Account secrets validated against `secretSchema` key in `schema.json`
- Per-row business constraints (e.g., Iterable project-type vs. mapping cardinality) are enforced at the transformer's Zod layer, NOT at the AJV layer — keep config schemas permissive on those constraints
