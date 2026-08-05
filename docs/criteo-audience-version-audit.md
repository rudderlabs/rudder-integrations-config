# Criteo Audience Version Audit (INT-6678)

## Scope

This repository owns the declarative Criteo Audience destination definition only. Runtime Criteo Marketing API paths are not defined here; the Criteo Audience route and SDK versioning are expected to be validated in `@rudderstack/integrations-lib` and the runtime service repositories.

## API version audit findings

Targeted repository searches found no runtime API-version implementation in `rudder-integrations-config`:

- No `@rudderstack/integrations-lib` dependency or Criteo Audience SDK implementation.
- No `versions.json` file.
- No `API_VERSION` constant.
- No `/2025-04/` or `contactlist` path references.
- No Criteo API-version strings for `2025.10`, `2025-10`, or `2026-07` beyond unrelated release dates in `CHANGELOG.md`.

Because this repo does not carry the runtime Criteo API path and the persisted destination config contract remains sufficient for the known audience/contactlist fields, no Criteo Audience config triplet changes are required here for the API-version audit.

## Stable destination identifier contract

Use the following identifiers when planning downstream config-backend/customer-inventory work:

| Identifier type                     | Value              | Source                                                           |
| ----------------------------------- | ------------------ | ---------------------------------------------------------------- |
| Destination definition name         | `CRITEO_AUDIENCE`  | `src/configurations/destinations/criteo_audience/db-config.json` |
| Display name                        | `Criteo Audience`  | `src/configurations/destinations/criteo_audience/db-config.json` |
| Filesystem key / destination folder | `criteo_audience`  | `src/configurations/destinations/criteo_audience/`               |
| Validation fixture key              | `criteo_audience`  | `test/data/validation/destinations/criteo_audience.json`         |
| Message type                        | `audiencelist`     | `config.supportedMessageTypes.cloud`                             |
| Supported source type               | `warehouse`        | `config.supportedSourceTypes`                                    |
| Supported connection mode           | `warehouse: cloud` | `config.supportedConnectionModes`                                |

### Aliases and nearby names

- No historical alias or migration mapping for `CRITEO_AUDIENCE` was found in `migration/`, `docs/`, generated constants, or destination configs.
- `src/configurations/destinations/criteo/` is a separate device-mode destination with `name: CRITEO` and `displayName: Criteo`; it should not be treated as the Criteo Audience inventory key.
- Generated destination constants currently include only the device-mode `CRITEO` destination. `CRITEO_AUDIENCE` is warehouse/cloud-only, so it is intentionally absent from `generated/Destinations.*` under the current generator filter.

## Current persisted config contract

Criteo Audience currently persists and validates these customer-visible/runtime fields:

- `rudderAccountId` — required account-management field.
- `adAccountId.warehouse` — required for warehouse cloud connections.
- `audienceId` — required for warehouse cloud connections.
- `audienceType` — required; enum values are `email`, `madid`, `identityLink`, and `gum`; default is `email`.
- `gumCallerId` — required when `audienceType` is `gum`.
- Consent-management fields exposed through `consentManagement`, `oneTrustCookieCategories`, and `ketchConsentPurposes`.

## Downstream inventory guidance

Customer-inventory queries should use `CRITEO_AUDIENCE` as the primary destination definition name and cross-check the folder/key value `criteo_audience` only if the target system stores definition keys separately from names. Do not query only for `CRITEO`, because that identifies the separate device-mode Criteo destination.

## Follow-up required outside this repository

- Verify the actual Criteo API version mounted by `@rudderstack/integrations-lib` and the runtime route implementation.
- Validate audience create/list/field/contactlist requests against the target Criteo API version in the runtime service tests.
- If the target Criteo API version introduces new customer-configurable fields, update this repository's `criteo_audience` `db-config.json`, `schema.json`, `ui-config.json`, and validation fixture in a synchronized follow-up.
