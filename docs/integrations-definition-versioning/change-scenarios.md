# Change Scenario Taxonomy

## Classification Key

- **Safe** = No version bump needed. Backward compatible.
- **BREAKING** = Requires major version bump + version directory for old version + migration file.
- **Conditional** = Breaking in some contexts, safe in others. Must check existing production data.

---

## schema.json Changes

| #   | Change                                                | Example                                                           | Classification  | Why                                                                                                           |
| --- | ----------------------------------------------------- | ----------------------------------------------------------------- | --------------- | ------------------------------------------------------------------------------------------------------------- |
| S1  | Add optional field                                    | Add `"region": { "type": "string" }`                              | Safe            | Old configs don't have it, new ones can. No validation failure.                                               |
| S2  | Add required field                                    | Add `"region"` to `required` array                                | **BREAKING**    | Old configs missing this field fail validation.                                                               |
| S3  | Remove field from properties                          | Remove `"legacyEndpoint"`                                         | **BREAKING**    | If `additionalProperties: false`, old configs with this field fail. Even with `true`, field loses validation. |
| S4  | Rename field                                          | `restApiKey` → `apiKey`                                           | **BREAKING**    | Old configs have wrong field name. Data plane reads wrong name.                                               |
| S5  | Change field type                                     | `"type": "string"` → `"type": "array"`                            | **BREAKING**    | Old configs have wrong type. Validation fails.                                                                |
| S6  | Add enum value                                        | Add `"AU-01"` to dataCenter enum                                  | Safe            | Old configs still valid. New option available.                                                                |
| S7  | Remove enum value                                     | Remove `"US-01"` from dataCenter enum                             | **Conditional** | Breaking only if existing configs use the removed value. Safe if no configs have it.                          |
| S8  | Tighten regex                                         | `.*` → `^[a-z0-9]+$`                                              | **Conditional** | Breaking only if existing configs have values matching old regex but not new one.                             |
| S9  | Loosen regex                                          | `^[a-z]+$` → `^[a-z0-9]+$`                                        | Safe            | All old values still match. New values also accepted.                                                         |
| S10 | Add if-then condition                                 | If `roleBasedAuth=true`, require `iamRoleARN`                     | **Conditional** | Breaking if existing configs have `roleBasedAuth=true` without `iamRoleARN`.                                  |
| S11 | Change default value                                  | `"default": "US-01"` → `"default": "US-03"`                       | Safe            | Only affects NEW configs. Existing configs already have explicit values.                                      |
| S12 | Add minimum/maximum                                   | Add `"minLength": 1` to a string field                            | **Conditional** | Breaking if existing configs have empty strings for this field.                                               |
| S13 | Change from optional to required                      | Move field into `required` array                                  | **BREAKING**    | Old configs without this field fail validation.                                                               |
| S14 | Change from required to optional                      | Remove field from `required` array                                | Safe            | Old configs still valid. New configs can omit.                                                                |
| S15 | Add allOf/oneOf constraint                            | Add conditional schema requiring field B when A=true              | **Conditional** | Breaking if existing configs violate the new constraint.                                                      |
| S16 | Add `format` keyword                                  | Add `"format": "uri"` to a string field                           | **Conditional** | Breaking if existing values don't match format.                                                               |
| S17 | Add `pattern` to array items                          | Add `"items": { "pattern": "^[A-Z]" }`                            | **Conditional** | Breaking if existing array items violate the pattern.                                                         |
| S18 | Set `additionalProperties: false`                     | Was `true` or absent → set to `false`                             | **BREAKING**    | Old configs with extra/unknown fields fail validation.                                                        |
| S19 | Add `minItems`/`maxItems` to array                    | Add `"minItems": 1` to an array field                             | **Conditional** | Breaking if existing configs have empty arrays for this field.                                                |
| S20 | Change `additionalProperties` on nested object        | Nested object goes from open to closed                            | **BREAKING**    | Old configs with extra nested keys fail validation.                                                           |
| S21 | Add `uniqueItems: true` to array                      | Array items now must be unique                                    | **Conditional** | Breaking if existing configs have duplicate items.                                                            |
| S22 | Change `oneOf`/`anyOf` branches                       | Remove a valid branch or tighten a branch                         | **BREAKING**    | Old configs matching the removed/tightened branch fail.                                                       |
| S23 | Restructure flat properties into nested `$ref`        | Refactor schema to use `$ref` / `definitions`                     | Safe\*          | \*Safe if the resolved schema is equivalent. Breaking if it changes validation behavior.                      |
| S24 | Add `dependencies` / `dependentRequired`              | Field B required when field A is present                          | **Conditional** | Breaking if existing configs have A without B.                                                                |
| S25 | Change array items type                               | `"items": { "type": "string" }` → `"items": { "type": "object" }` | **BREAKING**    | Old configs have wrong item type.                                                                             |
| S26 | Add `not` constraint                                  | Add `"not": { "required": ["legacyField"] }`                      | **BREAKING**    | Old configs with legacyField explicitly fail.                                                                 |
| S27 | Change property from flat to `$ref` shared definition | Inline schema → `"$ref": "#/definitions/authConfig"`              | Safe\*          | \*Safe if resolved schema is identical. Tooling that doesn't resolve `$ref` may break.                        |

---

## db-config.json Changes

db-config.json changes that affect stored config data (destConfig, includeKeys, secretKeys) will typically have corresponding schema.json changes. The entries below focus on db-config-specific behavior that isn't already covered by the schema table.

| #   | Change                                 | Example                                    | Classification  | Why                                                                                               |
| --- | -------------------------------------- | ------------------------------------------ | --------------- | ------------------------------------------------------------------------------------------------- |
| D1  | Add field to destConfig                | Add `"newField"` to defaultConfig array    | Safe            | New field available. No existing config affected.                                                 |
| D2  | Move field between destConfig sections | Move from `defaultConfig` to `web` only    | **BREAKING**    | Non-web configs lose access to this field.                                                        |
| D3  | Add/remove includeKeys or excludeKeys  | Remove `"trackingId"` from includeKeys     | **BREAKING**    | Client SDKs lose access. Device-mode integrations break.                                          |
| D4  | Add field to secretKeys                | Add `"apiToken"` to secretKeys             | **Conditional** | If field is in includeKeys without excludeKeys → breaks. Otherwise safe.                          |
| D5  | Add field to immutableKeys             | Add `"accountId"` to immutableKeys         | **BREAKING**    | Users can no longer edit this field on existing configs.                                          |
| D6  | Add/remove source type                 | Remove `"unity"` from supportedSourceTypes | **BREAKING**    | Existing Unity source connections break. (Adding is safe.)                                        |
| D7  | Add/remove connection mode             | Remove `"device"` for web                  | **BREAKING**    | Existing device-mode connections break. (Adding is safe.)                                         |
| D8  | Change auth config                     | Add OAuth requirement                      | **BREAKING**    | Existing configs without OAuth credentials can't re-authenticate.                                 |
| D9  | Change supportedMessageTypes           | Remove `"track"` from cloud mode           | **BREAKING**    | Existing configs expecting track events break.                                                    |
| D10 | Change displayName                     | "Google Analytics" → "GA (Legacy)"         | **BREAKING**    | Immutable property. Requires coordinated update across all references.                            |
| D11 | Add/change options.deprecated          | Set `deprecated: true`                     | Safe            | Informational. Existing configs continue working.                                                 |
| D12 | Change transformAtV1 / cdkV2Enabled    | "processor" → "router"                     | Safe            | Backend internal. No config data affected.                                                        |
| D13 | Add `hybridModeCloudEventsFilter`      | Add event filtering for hybrid mode        | **Conditional** | Safe if hybrid mode is newly added. Breaking if existing hybrid configs now have events filtered. |
| D14 | Add/change `configFilters`             | Add field filtering rules                  | **Conditional** | Depends on what gets filtered. Could hide fields from certain clients.                            |

---

## ui-config.json Changes

**Key principle: ui-config.json is purely a rendering layer. It NEVER directly triggers a version bump. Only the corresponding schema.json or db-config.json changes trigger versioning.**

| #   | Change                                 | Example                                       | Triggers version bump? | Why                                                                                                          |
| --- | -------------------------------------- | --------------------------------------------- | ---------------------- | ------------------------------------------------------------------------------------------------------------ |
| U1  | Add/remove field in form               | New textInput with configKey `"newField"`     | No                     | Rendering-only. Version depends on schema.json/db-config.json changes.                                       |
| U2  | Change field widget type               | `textInput` → `singleSelect`                  | No                     | Rendering-only. If this requires a schema type change → the schema change triggers versioning.               |
| U3  | Change label, placeholder, description | "API Key" → "REST API Key"                    | No                     | Cosmetic.                                                                                                    |
| U4  | Change preRequisites / conditions      | Show field only when connectionMode=cloud     | No                     | Rendering-only. API/Terraform can still send the field regardless.                                           |
| U5  | Reorganize sections/groups/tabs        | Move field from "Setup" tab to "Advanced" tab | No                     | Rendering-only.                                                                                              |
| U6  | Add/change regex validation            | Add `regex` to textInput field                | No                     | UI-only validation. API/Terraform use schema.json. If schema also changes → S8 triggers versioning.          |
| U7  | Change default value                   | `"default": false` → `"default": true`        | No                     | Rendering-only default. Schema default is what matters for API/Terraform.                                    |
| U8  | Change configKey                       | `"oldKey"` → `"newKey"`                       | **Indirectly**         | Field rename — the BREAKING trigger is the corresponding schema.json rename (S4) and db-config.json changes. |
| U9  | Change widget to `dynamicForm`         | `textInput` → `dynamicForm`                   | **Indirectly**         | The BREAKING trigger is the schema type change (S5: string → array).                                         |
| U10 | Change `singleSelect` → `multiSelect`  | Single value → multi value                    | **Indirectly**         | The BREAKING trigger is the schema type change (S5: string → array).                                         |

---

## Compound Scenarios

These illustrate real-world changes that combine multiple atomic changes from above. Only scenarios that add nuance beyond the individual tables are included.

> **Convention:** Version triggers are S-codes (schema) and D-codes (db-config) only. UI changes accompany but never trigger version bumps.

### "Add a new required field with default"

**Triggers:** S2 + S1 + D1 | **BREAKING**
`migrate()` adds field with default value. Could be made safe by adding as optional first, then requiring in the next major.

### "Change authentication from API key to OAuth"

**Triggers:** D8 + S4 + D3 | **BREAKING**
Complex — requires OAuth flow for existing users. `migrate()` renames credential fields; user must complete OAuth separately.

### "Deprecate a field and add replacement"

**Triggers:** S1 + D1 | **Safe** (if old field kept)
No migration needed immediately. Old field continues working. Follow-up version removes old field → BREAKING (S3).

### "Restructure flat fields into nested object"

**Triggers:** S4 + S5 + D2 | **BREAKING**
`migrate()` merges `host`, `port`, `path` into `endpoint: { url: host, port, path }`.

### "Convert single-value field to multi-value"

**Triggers:** S5 | **BREAKING**
`migrate()` wraps string in array: `migrated.eventType = [config.eventType]`.

### "Consolidate boolean flags into single enum"

**Triggers:** S3 + S1 + S5 | **BREAKING**
`migrate()`: `if (config.useSSL) → "ssl"`, `if (config.useProxy) → "proxy"`, else `"direct"`. Deletes old fields.

### "Add conditional required field (if-then)"

**Triggers:** S10 + S15 | **Conditional**
Breaking only if existing configs have `useProxy=true` without `proxyUrl`. Check production data first.

### "Move fields between destConfig source types"

**Triggers:** D2 | **BREAKING**
`trackingId` moves from `defaultConfig` (all platforms) to `web` + `android` only → iOS configs lose this field.

---

## Summary

**Only schema.json and db-config.json changes trigger version bumps. ui-config.json never directly triggers versioning.**

| Classification        | Changes                                                                                                                                                                                                                                                                                                                                |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Always Breaking**   | Remove field, rename field, change type, make optional→required, remove enum value, remove connection mode/source type, change auth, set `additionalProperties: false`, change array items type, remove `oneOf`/`anyOf` branches, add `not` constraint, change `displayName`                                                           |
| **Never Breaking**    | Add optional field, add enum value, loosen regex, add source type/connection mode/sync behaviour, cosmetic changes (labels, placeholders, sections), change defaults, mark deprecated, change backend-internal settings, make required→optional, `$ref` refactoring                                                                    |
| **Context-Dependent** | Tighten regex (S8), remove enum value (S7), add `format` (S16), add `pattern` to items (S17), add if-then/allOf (S10/S15), add min/max constraints (S12/S19), add `uniqueItems` (S21), add `dependencies` (S24), add to secretKeys (D4), add to immutableKeys (D5), add `hybridModeCloudEventsFilter` (D13), add `configFilters` (D14) |

**Best practice for conditional changes:** Always query production configs before making the change. If any existing configs violate the new constraint, it's a major version bump.
