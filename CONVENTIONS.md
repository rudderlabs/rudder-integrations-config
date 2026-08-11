# Conventions

This document captures naming and structural conventions used across this repository. Following them keeps account definitions, sources, and destinations consistent and machine-validatable.

## Table of contents

- [**AccountDefinition naming (`accountDefinitionName`)**](#accountdefinition-naming-accountdefinitionname)
- [**String `pattern` and `regex`**](#string-pattern-and-regex)
- [**Deduplication / event-id config key (`deduplicationKey`)**](#deduplication--event-id-config-key-deduplicationkey)
- [**Restricting a field by connection mode**](#restricting-a-field-by-connection-mode)

## AccountDefinition naming (`accountDefinitionName`)

Every account definition is identified by a unique `name` (the `accountDefinitionName`). It MUST be written in `SCREAMING_SNAKE_CASE` and follow this pattern:

```text
{CATEGORY}_{TYPE}[_{AUTH_QUALIFIER}]
```

The `[_{AUTH_QUALIFIER}]` segment is optional — include it only when it is needed to disambiguate authentication variants of the same integration.

### Segments

| Segment          | Required | Description                                                                                                                                                                  |
| ---------------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `CATEGORY`       | Yes      | The kind of integration the account belongs to. One of `SOURCE`, `DESTINATION`, or `DATA_RETENTION` (storage accounts, whose db-config `category` value is `dataRetention`). |
| `TYPE`           | Yes      | The integration key in `SCREAMING_SNAKE_CASE` (the uppercase form of the integration `type`), e.g. `BIGQUERY`, `HUBSPOT`, `SALESFORCE`, `FACEBOOK_LEAD_ADS_NATIVE`.          |
| `AUTH_QUALIFIER` | No       | A qualifier describing the authentication / credential variant, e.g. `OAUTH`, `NATIVE_OAUTH`. Use it to distinguish multiple account definitions for the same integration.   |

### Examples

| `accountDefinitionName`                 | Category         | Type                       | Auth qualifier |
| --------------------------------------- | ---------------- | -------------------------- | -------------- |
| `SOURCE_BIGQUERY`                       | `SOURCE`         | `bigquery`                 | _(none)_       |
| `SOURCE_FACEBOOK_LEAD_ADS_NATIVE_OAUTH` | `SOURCE`         | `facebook_lead_ads_native` | `OAUTH`        |
| `DESTINATION_HUBSPOT_OAUTH`             | `DESTINATION`    | `hubspot`                  | `OAUTH`        |
| `DESTINATION_SALESFORCE_OAUTH`          | `DESTINATION`    | `salesforce`               | `OAUTH`        |
| `DATA_RETENTION_S3_ACCESS_KEYS`         | `DATA_RETENTION` | `S3`                       | `ACCESS_KEYS`  |
| `DATA_RETENTION_S3_IAM_ROLE`            | `DATA_RETENTION` | `S3`                       | `IAM_ROLE`     |
| `DATA_RETENTION_GCS`                    | `DATA_RETENTION` | `GCS`                      | _(none)_       |

### Enforcement

The `name` field is validated against the pattern `^[A-Z0-9_]+$` defined in [`src/schemas/account/account-db-config-schema.json`](src/schemas/account/account-db-config-schema.json). This pattern restricts names to uppercase letters, digits, and underscores, but does not by itself enforce full `SCREAMING_SNAKE_CASE` (for example, it does not prevent leading, trailing, or doubled underscores). The `{CATEGORY}_{TYPE}[_{AUTH_QUALIFIER}]` segment structure above is a convention contributors are expected to follow, not something the regex enforces.

## String `pattern` and `regex`

This applies equally to `pattern` in `schema.json` and to the `regex` on the same field in
`ui-config.json`. Use a plain expression for the value the field actually accepts:

```json
{ "type": "string", "pattern": "^.{1,100}$" }
```

**Do not use the `(^\{\{.*\|\|(.*)\}\}$)|(^env[.].+)|…` prefix. It is deprecated** — going
forward it should not be added to a new field, in either file.

That prefix exists to let a config value be a `{{ }}` template or an `env.` reference, and it
is the single biggest copy-paste trap in this repo: **239 of 245 destination schemas still
carry it**, so whichever existing destination you open as a template will almost certainly
have it — including in the `ui-config.json` `regex` sitting next to the field. Copy the
field's own regex, not the prefix.

Size the pattern to the value the field genuinely accepts, and stop there. Don't stretch it to
keep `{{ }}` / `env.` values passing: config-backend syntax-checks those and then validates
them against this pattern unchanged, so a narrow pattern — a URL or a strict id format — will
reject them. That is fine and intended. Going forward a new field is not expected to preserve
templating support; write the pattern the field's own value needs.

Six schemas don't carry the prefix: `custom_audience` (2026-05), `iterable_audience` (2026-06),
`bqstream_all_events` (2026-06) and `braze_audience` (2026-07) use plain patterns, while
`linkedin_audience` and `tiktok_audience` declare no string patterns at all.

Existing schemas are not being rewritten; the rule applies to new fields and new
destinations.

## Deduplication / event-id config key (`deduplicationKey`)

When a destination lets the customer choose which message field carries the id the partner
dedupes on (typically because the same conversion is also sent by a browser pixel), the
config key is **`deduplicationKey`** — not `eventId`, `conversionId`, or a new spelling.

Four destinations use it today: `pinterest_tag`, `linkedIn_ads`, `snapchat_conversion`,
`snap_pixel`. Copy the UI field from
[`linkedIn_ads/ui-config.json`](src/configurations/destinations/linkedIn_ads/ui-config.json)
— a `textInput` labelled "Deduplication Key", placeholder `e.g: messageId`, with a note
explaining that a dot-path such as `properties.orderId` maps from `message.properties.orderId`
(but with a plain `regex`, per the section above — the field there still carries the
deprecated prefix).

Semantics the transformer implements: resolve the customer's path(s) against the message and
fall back to `messageId`. `pinterest_tag` and `linkedIn_ads` accept a comma-separated list and
take the first that resolves, falling back when the config is unset _or_ no path resolves
(`getOneByPaths(…) ?? .messageId`). `snapchat_conversion` takes a single path and falls back
only when the config is unset (`deduplicationKey || 'messageId'`) — a set-but-unresolvable
path yields no id rather than `messageId`. Prefer the `getOneByPaths` shape for new
destinations.

`snap_pixel` is device-mode only (`web: ["device"]`), so it has no transformer implementation;
its web SDK integration resolves the key with the same single-path shape as
`snapchat_conversion` (`get(message, deduplicationKey || 'messageId')`). A device-mode
destination therefore needs the equivalent handling in the SDK integration, not in the
transformer — the config key and UI field stay the same either way.

`snapchat_conversion` and `snap_pixel` both gate the field on a separate `enableDeduplication`
checkbox — only add that toggle if the partner's id field is genuinely optional.

## Restricting a field by connection mode

When a value is valid in one connection mode but not another — e.g. a partner's browser SDK
supports fewer events than its server API — express it as **conditional validation in
`schema.json`**, keyed on `connectionMode.<sourceType>`:

```jsonc
"allOf": [{
  "if": {
    "properties": { "connectionMode": { "properties": { "web": { "const": "device" } },
                                        "required": ["web"] } },
    "required": ["connectionMode"]
  },
  "then": {
    "properties": { "eventsMapping": { "items": { "properties": {
      "to": { "not": { "enum": ["app_installed", "app_opened"] } } } } } },
    "errorMessage": { "properties": { "eventsMapping":
      "app_installed and app_opened are not supported by the browser SDK. Map them on a cloud-mode connection instead." } }
  },
  // Required. Without this, ajv also emits a bare `must match "then" schema` alongside the
  // message above, and config-backend returns both to the customer. See below.
  "errorMessage": { "if": "This value is not valid for the selected connection mode." }
}]
```

Draft-07 `if`/`then` is available and already used by 242 destination schemas; `errorMessage`
comes from `ajv-errors`, so the customer gets a readable reason rather than a raw schema
failure (see `src/validator/index.ts`).

**Both `errorMessage`s are needed.** A failing `if`/`then` produces two ajv errors: one from
the keyword that actually failed (inside `then`) and one for the `if` keyword itself
(`must match "then" schema`, with an empty `instancePath`). The `errorMessage` inside `then`
only replaces the first. config-backend maps _every_ error into the response with no
filtering, so omitting the outer `errorMessage` gets the customer a readable sentence followed
by a raw, field-less schema failure.

### Where this is actually enforced — know what the customer sees

**Server-side, at save time. There is no inline UI validation for it.**

- **config-backend** compiles the destination's `configSchema` with ajv, configured the same
  way as here — `allErrors`, `ajv-errors`, `ajv-keywords`. Conditionals **are** enforced and
  the `errorMessage` **does** surface — every ajv error is mapped into the response, which is
  why the `if` needs its own `errorMessage` too (above).
- **rudder-webapp** renders the destination config form from `ui-config.json`, not
  `schema.json`. The destination configuration components contain no reference to
  `configSchema` or ajv at all. Its client-side validation is limited to what `ui-config.json`
  expresses: `required`, `regex` / `regexErrorMessage`, and `preRequisites`.

So the customer picks the disallowed value, fills in the rest of the form, hits **Save**, and
gets the `errorMessage` back from the API. Correctness is guaranteed; discoverability is not.

**Pair the conditional with a plain-language `note` (or `callout`) on the field** stating the
restriction, so it is visible before the save round-trip. That is the cheap half of the UX;
the conditional is what actually enforces it.

If a destination genuinely needs the value to be _unselectable_ rather than rejected, that is
today only achievable with a separate `preRequisites`-gated field per mode — with the scaling
cost described above. Weigh it per destination; for a restriction affecting a couple of enum
values, schema validation plus a note is the better trade. Inline UI support for conditional
validation would remove the trade entirely and is worth raising against rudder-webapp.

Prefer this over the two alternatives:

- **A second config field per mode**, gated with `preRequisites` — the field count then grows
  with every (mode × platform) the partner supports, and existing configs have to be reasoned
  about against several overlapping tables.
- **Duplicating the rule into the transformer or the SDK** — a second copy on a different
  release train drifts from the first, and the customer gets no feedback until runtime rather
  than at save time.

One config field, one source of truth, validated where the config is written. A new mode is
one more `if`/`then` block.
