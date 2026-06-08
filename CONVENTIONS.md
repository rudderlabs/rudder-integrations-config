# Conventions

This document captures naming and structural conventions used across this repository. Following them keeps account definitions, sources, and destinations consistent and machine-validatable.

## Table of contents

- [**AccountDefinition naming (`accountDefinitionName`)**](#accountdefinition-naming-accountdefinitionname)

## AccountDefinition naming (`accountDefinitionName`)

Every account definition is identified by a unique `name` (the `accountDefinitionName`). It MUST be written in `SCREAMING_SNAKE_CASE` and follow this pattern:

```text
{CATEGORY}_{TYPE}[_{AUTH_QUALIFIER}]
```

The `[_{AUTH_QUALIFIER}]` segment is optional — include it only when it is needed to disambiguate authentication variants of the same integration.

### Segments

| Segment            | Required | Description                                                                                                                                                             |
| ------------------ | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `CATEGORY`         | Yes      | The kind of integration the account belongs to. One of `SOURCE` or `DESTINATION`.                                                                                       |
| `TYPE`             | Yes      | The integration key in `SCREAMING_SNAKE_CASE` (the uppercase form of the integration `type`), e.g. `BIGQUERY`, `HUBSPOT`, `SALESFORCE`, `FACEBOOK_LEAD_ADS_NATIVE`.     |
| `AUTH_QUALIFIER`   | No       | A qualifier describing the authentication / credential variant, e.g. `OAUTH`, `NATIVE_OAUTH`. Use it to distinguish multiple account definitions for the same integration. |

### Examples

| `accountDefinitionName`                  | Category    | Type                       | Auth qualifier  |
| ---------------------------------------- | ----------- | -------------------------- | --------------- |
| `SOURCE_BIGQUERY`                        | SOURCE      | `bigquery`                 | _(none)_        |
| `SOURCE_FACEBOOK_LEAD_ADS_NATIVE_OAUTH`  | SOURCE      | `facebook_lead_ads_native` | `OAUTH`         |
| `DESTINATION_HUBSPOT_OAUTH`              | DESTINATION | `hubspot`                  | `OAUTH`         |
| `DESTINATION_SALESFORCE_OAUTH`           | DESTINATION | `salesforce`               | `OAUTH`         |

### Enforcement

The `name` field is validated against the pattern `^[A-Z0-9_]+$` defined in [`src/schemas/account/account-db-config-schema.json`](src/schemas/account/account-db-config-schema.json). This pattern restricts names to uppercase letters, digits, and underscores, but does not by itself enforce full `SCREAMING_SNAKE_CASE` (for example, it does not prevent leading, trailing, or doubled underscores). The `{CATEGORY}_{TYPE}[_{AUTH_QUALIFIER}]` segment structure above is a convention contributors are expected to follow, not something the regex enforces.
