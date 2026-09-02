# Feedback

> Human direction, preferences, corrections, or review guidance.
> Append-only. Agent-authored sections may optionally carry an HTML-comment tag
> (e.g., `<!-- pr:<id> -->`) identifying the writer/PR/run; human-authored
> sections are conventionally left untouched by automated runs.

## INT-6707 — HubSpot Auth UI Simplification

- Product clarified that HubSpot authorization deprecation should remove the auth-type selector entirely when Private Apps is the only supported option; the UI should not show a one-option `authorizationType` singleSelect.
- Supported HubSpot configs should rely on the `accessToken` credential field only, and legacy API-key config should not remain as a visible UI field.

## INT-7040 — Braze Schema Drift Review Guidance

- Reviewer guidance for Braze schema-generator baseline drift: do not describe `usePlatformSpecificApiKeys`, `appKey`, `androidApiKey`, `iOSApiKey`, or `webApiKey` as missing from `src/configurations/destinations/braze/schema.json`; those fields are already present under conditional `allOf` branches.
- Treat generator warnings about those API-key fields as generator/root-schema expectation drift, not absent schema fields, when separating baseline noise from scoped Braze UI-only cleanup.

## INT-7017 — ClickHouse JSON Paths Review Guidance

- Reviewer guidance for the ClickHouse `jsonPaths` UI field: use the concise footer note `Stored as native JSON columns, which require ClickHouse 25.3 or newer.` instead of longer linked help text.
- Final reviewer guidance for ClickHouse `jsonPaths` UI copy: label the field `JSON columns` without `(Optional)`, keep the helper text path-oriented because the input value is paths, and reserve `native JSON columns` wording for ClickHouse storage behavior.
- Use a CSV-style placeholder such as `e.g: testMap.nestedMap,testMap.testProperties` for the ClickHouse `jsonPaths` UI field.

## INT-7014 — CustomerIO User Mapping UI Copy

- CustomerIO `userIdIdentifierType` UI copy should describe the setting generically as how RudderStack `userId` is sent to Customer.io when API Version is v2.
- Do not mention internal implementation terms such as record event or VDM v2, and do not imply this setting affects record-event API behavior.
- CustomerIO `apiVersion` and `userIdIdentifierType` dashboard copy should scope these settings to cloud-mode delivery and avoid implying they affect Customer.io SDK/device-mode behavior.
- For the newer `userIdMapping` field name, keep the same customer-facing copy rule: describe how RudderStack `userId` is sent to Customer.io when API Version is v2, avoid internal terms such as record event or VDM v2, and scope both `apiVersion` and `userIdMapping` to cloud-mode delivery rather than SDK/device-mode behavior.

## INT-7070 — OpenAI Ads Account Metadata Review Guidance

- Reviewer guidance corrected the OpenAI Ads account-backed credential approach: do not add a destination-specific exemption in `scripts/validate_account_definitions.py`; satisfy the generic account coverage validator through destination metadata instead.
- For OpenAI Ads, account option/secret fields should be represented in destination `config.destConfig.defaultConfig`, and secret account fields such as `apiKey` should also be listed in `config.secretKeys`.
- Do not add non-device fields such as `rudderAccountId` to destination `config.includeKeys`; optional account UI credential fields should explicitly set `optional: true`.
- For OpenAI Ads web device mode, include the linked-account `pixelId` in destination `config.includeKeys` so it passes both workspace-config filtering and the device-mode allowlist for browser SDK initialization.
- Reviewer guidance clarified that OpenAI Ads should not support `warehouse`; keep it absent from supported source types, supported connection modes, destination config source entries, and generated schema branches.
- Optional OpenAI Ads text fields that can be cleared in the UI must accept the empty string in both `ui-config.json` regexes and generated `schema.json` patterns; for `defaultCurrency`, use `^$|^[A-Z]{3}$` rather than a non-empty-only currency regex.
