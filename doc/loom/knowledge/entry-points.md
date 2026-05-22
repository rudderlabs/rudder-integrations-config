# Entry Points

> Key files agents should read first to understand the codebase.
> This file is append-only - agents add discoveries, never delete.

(Add entry points as you discover them)

## Key files to read first

When exploring this repo:

1. `src/schemas/destination/db-config-schema.json` — authoritative validator for all destination db-config.json files. Check here for allowed field names and enum values before adding new config fields.
2. `src/schemas/account/account-db-config-schema.json` — authoritative validator for account db-config.json files. Lists valid `authenticationType` values (includes `api_key`).
3. `src/configurations/destinations/fb_custom_audience/` — canonical audience destination triad template. Read all three JSON files before creating a new audience destination.
4. `src/configurations/destinations/fb_custom_audience/accounts/fb_custom_audience_access_token/` — canonical account triad template.
5. `test/data/validation/destinations/fb_custom_audience.json` — canonical AJV fixture example.
6. `package.json` — test scripts. Note: `npm test` runs jest with `--coverage --notify`, which is slow. Use `npx jest --testPathPattern=<name> --coverage=false` for fast targeted runs.

## Iterable Audience M1 files (added 2026-05-22)

- `src/configurations/destinations/iterable_audience/db-config.json`
- `src/configurations/destinations/iterable_audience/schema.json`
- `src/configurations/destinations/iterable_audience/ui-config.json`
- `src/configurations/destinations/iterable_audience/accounts/iterable_audience_api_key/db-config.json`
- `src/configurations/destinations/iterable_audience/accounts/iterable_audience_api_key/schema.json`
- `src/configurations/destinations/iterable_audience/accounts/iterable_audience_api_key/ui-config.json`
- `test/data/validation/destinations/iterable_audience.json`
