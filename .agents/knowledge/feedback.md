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

## INT-7014 — CustomerIO User Mapping UI Copy

- CustomerIO `userIdIdentifierType` UI copy should describe the setting generically as how RudderStack `userId` is sent to Customer.io when API Version is v2.
- Do not mention internal implementation terms such as record event or VDM v2, and do not imply this setting affects record-event API behavior.
- CustomerIO `apiVersion` and `userIdIdentifierType` dashboard copy should scope these settings to cloud-mode delivery and avoid implying they affect Customer.io SDK/device-mode behavior.
