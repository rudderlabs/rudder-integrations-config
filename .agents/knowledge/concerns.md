## Preprocess Async Control Flow
<!-- RUD-2749 -->
- `scripts/preProcess.js` uses `destinationFolders.forEach(async ...)`, which does not await child promises.
- This can cause partial writes/racey completion behavior in CI or chained script usage.
- Prefer `for...of` with `await` or `Promise.all` with explicit error aggregation.

## GA4_V2 Skip Semantics
<!-- RUD-2749 -->
- In `scripts/preProcess.js`, `if (destinationName === 'ga4_v2') { console.log('Skipping GA4_v2'); }` logs but does not skip.
- If `ui-default.json` exists, `ga4_v2` can still be processed despite the log message.
- Align code behavior with operator expectation (log + `return`) or update message text.

## Schema and Fixture Drift
<!-- RUD-2749 -->
- Destination schema changes under `src/configurations/destinations/*/schema.json` require synced fixture expectations in `test/data/validation/destinations/*.json`.
- Since tests assert exact serialized error arrays, even message wording/order changes can fail CI.
- Keep fixture updates coupled with schema/db-config updates in the same change set.

## Secret Exposure Guardrails
<!-- RUD-2749 -->
- Custom rules in `src/validator/index.ts` enforce that `secretKeys` cannot be exposed through `includeKeys` unless also in `excludeKeys`.
- Device/hybrid support requires non-empty `includeKeys`; definition authors can break runtime behavior if this is ignored.
- Validate destination definitions early (`validateDestinationDefinitions`) before deploy scripts.
