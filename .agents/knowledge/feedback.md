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
- OpenAI Ads `eventMapping[].deduplicationKey` is optional and must allow an empty string when cleared; keep the UI regex and generated schema pattern as `^$|^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*$`, while still rejecting JSONPath, brackets, wildcards, filters, numeric index segments, and malformed dot paths.

## AI-1394 — GCS Datalake JSON Paths Review Guidance

- For GCS Datalake `jsonPaths`, use a plain catch-all regex/schema pattern (`^(.*)$`) for literal JSON path strings; do not copy Snowflake's explicit dynamic-config `{{...||...}}` or `env.*` alternatives unless a reviewer asks for that support.
- Reviewer guidance for the GCS Datalake `jsonPaths` UI field: label it `JSON columns`, use label note `Specify required JSON paths in dot notation separated by commas`, and use placeholder `e.g: testMap.nestedMap,testMap.testProperties`.

## INT-7102 — OpenAI Ads Event Filtering Review Guidance

- Reviewer clarified that OpenAI Ads event-filtering config should be destination-wide for delivery, but the dashboard event-filtering UI group should remain client-side/web-device-only and use `eventFilteringOption` without a `.web` prerequisite key.
- Do not expose the OpenAI Ads dashboard event-filtering controls for cloud-mode connections unless product explicitly changes the UI scope.
- For OpenAI Ads event-filtering schema/config changes, rely on existing `test/data/validation/destinations/openai_ads.json` fixture cases for accepted/rejected config shape coverage; do not add duplicate one-off assertions in `test/validation.test.ts` for the same behavior.

## INT-7144 — Google Ads Offline Conversions Mapping Layout

- Reviewer guidance for `src/configurations/destinations/google_adwords_offline_conversions/ui-config.json`: keep the three mapping fields behind a single Form Builder V2 `redirect` screen using tabs.
- Put `eventsToConversionsNamesMapping` and `eventsToOfflineConversionsTypeMapping` in the first tab, put `customVariables` in the second tab, and preserve the existing persisted mapping config keys.
- Latest reviewer direction for `loginCustomerId` supersedes the earlier optional-only note: enforce `loginCustomerId` through conditional schema validation when `subAccount` is true, while avoiding unconditional top-level required validation.
- Reviewer clarified the preferred `schema.json` shape: do not keep `loginCustomerId` in top-level `configSchema.properties`; define and validate it only inside the conditional `allOf` branch where `subAccount` is true.
- Reviewer clarified that the shared `scripts/schemaGenerator.py` required-field change is not needed for this migration; keep the `loginCustomerId` rule in the destination schema instead.

## INT-7150 — OpenAI Ads Conditional UI Cleanup Guidance

- Reviewer guidance confirmed `includeWhenConditional` should not be preserved or reintroduced in `scripts/schemaGenerator.py` unless a new ui-config field actually needs it; after INT-7150, conditionally visible dynamic custom form fields are emitted only inside conditional `if`/`then` schema and omitted from unconditional item properties.

## INT-7154 — Salesforce OAuth Account Naming Guidance

- Reviewer clarified the customer-facing Salesforce OAuth account card names: v2 External Client App should be named `OAuth (External Client App)` and legacy Connected App should be named `OAuth (Connected App - Legacy)`.
- The legacy Salesforce OAuth account `displayOptions.deprecationLabel` should use the exact spaced option wording: `Create a new account using the 'OAuth (ECA)' option.`
- The Salesforce OAuth v2 account `uiConfig.description` should use the exact wording `Grant access using the latest Salesforce External Client App (ECA)`.
