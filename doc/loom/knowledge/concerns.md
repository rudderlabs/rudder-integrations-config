# Concerns & Technical Debt

> Technical debt, warnings, issues, and improvements needed.
> This file is append-only - agents add discoveries, never delete.

(Add concerns as you discover them)

## npm test coverage threshold — acceptance criterion footgun

The package.json test script runs jest with `--coverage` and a 100% coverage threshold by default. This causes `npm test` to be unsuitable as a loom stage acceptance criterion (it times out). Any future stage that needs to verify tests should use the targeted invocation `npx jest --testPathPattern=validation.test.ts --coverage=false`.

If the coverage threshold is ever lowered or removed from `package.json`, this concern can be removed.

## Iterable Audience suppression callout deferred to M2

The LLD §4.1 suppression callout (described in `doc/plans/iterable-audience-m1-lld.md`) was intentionally excluded from M1 scope. Only the hybrid mapping note ("Per Iterable's API, each row is sent with either email or userId — never both...") was included. M2 should add the suppression callout to the destination ui-config.

## schemaGenerator.py advisories on identifierMappings

`scripts/schemaGenerator.py` reports a path quirk for `identifierMappings.N.warehouseColumn` because the UI uses dot-notation configKeys (`identifierMappings.0.warehouseColumn`) while the AJV schema uses array syntax. This is a known limitation of conditional UI rendering and is not blocking. If the schemaGenerator is updated to handle dot-notation paths, this advisory will disappear.

## LLD §4.1 vs actual iterable_audience implementation (resolved)

The LLD §4.1 destConfig template was simplified during implementation. Two fields from the LLD spec were removed:
- `listId` and `listName` removed from `defaultConfig` — list selection is VDM-v2-form-side, not stored in the transformer-visible destConfig
- Consent management fields (`consentManagement`, `oneTrustCookieCategories`, `ketchConsentPurposes`) removed from `warehouse` config — deferred to post-M1

Additionally, the LLD did NOT include account option fields in `destConfig.defaultConfig` or `secretKeys`, but the actual implementation adds both. This is the correct pattern for account-bound destinations that need option values at delivery time.

The LLD doc remains useful for architecture and data flow but its `db-config.json` snippet is not the canonical reference — use `src/configurations/destinations/iterable_audience/db-config.json` directly.
