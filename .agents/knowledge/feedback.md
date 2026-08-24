# Feedback

> Human direction, preferences, corrections, or review guidance.
> Append-only. Agent-authored sections may optionally carry an HTML-comment tag
> (e.g., `<!-- pr:<id> -->`) identifying the writer/PR/run; human-authored
> sections are conventionally left untouched by automated runs.

## INT-6707 — HubSpot Auth UI Simplification

- Product clarified that HubSpot authorization deprecation should remove the auth-type selector entirely when Private Apps is the only supported option; the UI should not show a one-option `authorizationType` singleSelect.
- Supported HubSpot configs should rely on the `accessToken` credential field only, and legacy API-key config should not remain as a visible UI field.
