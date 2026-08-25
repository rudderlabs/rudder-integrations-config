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
- Keep ClickHouse `jsonPaths` UI terminology path-oriented for the field label and label note (`JSON paths`, `JSON paths in dot notation`); reserve `native JSON columns` wording for describing ClickHouse storage behavior.
