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

## DEX-518 — Qualtrics CLI Onboarding Scope

- User direction for Qualtrics onboarding was to make no changes in `rudder-integrations-config` or Terraform; the destination metadata in this repository should be treated as read-only source/reference material for this task.
- Actual Qualtrics onboarding work belongs in the CLI implementation repository using its `onboard-destination` workflow/skill, not in the integrations-config repository.
