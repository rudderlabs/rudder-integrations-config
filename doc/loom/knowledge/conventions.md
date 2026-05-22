# Coding Conventions

> Discovered coding conventions in the codebase.
> This file is append-only - agents add discoveries, never delete.

(Add conventions as you discover them)

## AJV validation fixture format

File: `test/data/validation/destinations/<name>.json`

Structure:

```json
[
  {
    "config": {
      /* valid config object */
    },
    "result": true
  },
  {
    "config": {
      /* invalid config — omit required field */
    },
    "result": false,
    "err": ["<expected AJV error message>"]
  }
]
```

Rules:

- Positive cases: include all required fields, set `"result": true`
- Negative cases: omit a required field or pass wrong type, set `"result": false` and include `"err"` array
- `rudderAccountId` omission is always a good negative test case for account-bound destinations
- `listId` numeric type (not string) must be validated as a negative case if string is passed
- The test runner auto-discovers this file from the destination directory — no registration needed

## migrate-to-accounts-framework adaptations (net-new destination)

When creating a brand-new destination (not migrating an existing one), the standard migrate-to-accounts-framework skill steps apply with these adaptations:

1. **No migration step** — skip the "remove legacy apiKey from destination db-config" step; the destination starts account-bound from day one
2. **Suppression callout** — the LLD §4.1 suppression callout is deferred to M2; M1 only includes the hybrid mapping note in the ui-config.json inline note

## Naming conventions

- Destination directory: `snake_case` (e.g., `iterable_audience`)
- Destination `name`: `SCREAMING_SNAKE_CASE` (e.g., `ITERABLE_AUDIENCE`)
- Account directory: `<destination_dir>_<auth_type>` (e.g., `iterable_audience_api_key`)
- Account `name`: `DESTINATION_<DEST_NAME>_<AUTH_TYPE>` (e.g., `DESTINATION_ITERABLE_AUDIENCE_API_KEY`)
- Account `type`: matches destination directory name exactly (e.g., `iterable_audience`)

## JSON Schema conventions

- `rudderAccountId` pattern: `"^.{1,100}$"` (1–100 chars, any content)
- `apiKey` pattern: `"(^\\{\\{.*\\|\\|(.*)\\}\\}$)|^(.{1,200})$"` — accepts template syntax OR literal 1–200 chars
- Consent/cookie fields use standard platform pattern: `"(^\\{\\{.*\\|\\|(.*)\\}\\}$)|(^env[.].+)|^(.{0,100})$"`
- Copy boilerplate from `fb_custom_audience/schema.json` for `oneTrustCookieCategories`, `consentManagement`, `connectionMode`, `ketchConsentPurposes`

## schemaGenerator.py advisories (soft, not errors)

When running `python3 scripts/schemaGenerator.py`, two advisory messages are expected and harmless:

1. **additionalProperties recommendation** — the script recommends adding `additionalProperties: false`; this is a style suggestion, not a schema error
2. **identifierMappings.N.warehouseColumn ui-vs-schema path quirk** — the UI uses dot-notation paths like `identifierMappings.0.warehouseColumn` as configKeys; the script flags a path mismatch with the AJV schema array syntax. This is an artifact of conditional UI rendering and is not a bug.
