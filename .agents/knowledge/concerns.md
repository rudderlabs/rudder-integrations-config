# Concerns

> Technical debt, TODOs, FIXMEs, security concerns, architectural issues.
> Append-only. Agent-authored sections may optionally carry an HTML-comment tag
> (e.g., `<!-- pr:<id> -->`) identifying the writer/PR/run; human-authored
> sections are conventionally left untouched by automated runs.
> Top-5–8 highest-signal items per category, not exhaustive.

## TODO/FIXME/XXX/HACK Density

<!-- RUD-2776 -->

- Destination-definition validation still contains deferred TODO rule blocks for cloud-only include/exclude key constraints; this can allow inconsistent configs until cleanup is complete (`src/validator/index.ts` TODO blocks near `destinationDefinitionRules`).
- `schemaGenerator.py` includes TODO-noted special-casing around regex behavior, indicating known design debt in field-level pattern handling (`scripts/schemaGenerator.py::generalize_regex_pattern`).
- Test fixtures include TODO-marked expected limitations (e.g., missing empty-string validation behavior), signaling known gaps in current rules (`test/data/validation/destinations/custify.json:17`).

## Security Concerns

<!-- RUD-2776 -->

- Deploy scripts can mutate remote control-plane data; safety depends on honoring dry-run defaults and avoiding `--no-dry-run` unless intended (`scripts/deployToDB.py::get_command_line_arguments`, `scripts/deployAccountsToDB.py::get_command_line_arguments`).
- When verbose deploy logging is enabled, `log_api_request` writes the full request body and an equivalent curl command verbatim to `deploy-debug.log`; in local runs `generate_curl_command` also emits the basic-auth credential in full (`--user "user:password"`) and only the `Auth:` line masks the password, while CI mode masks the credential entirely. So locally both request-payload secrets and the auth credential are persisted to that file in cleartext (`scripts/utils.py::log_api_request`, `scripts/utils.py::generate_curl_command`).
- Dynamic template evaluation in `generateConstants.js` uses `new Function`, which is acceptable for trusted local templates but is a code-execution boundary if template inputs become untrusted (`scripts/generateConstants.js::processTemplate`).

## Architectural Smells

<!-- RUD-2776 -->

- High operational coupling to filesystem conventions: many scripts assume canonical directory/file names, making structural refactors expensive (`scripts/preProcess.js`, `scripts/schemaGenerator.py`, `scripts/deployToDB.py`).
- Large monolithic Python scripts (`schemaGenerator.py`) mix CLI, diffing, and schema transformation logic, raising maintenance cost and increasing regression blast radius.
- Mixed-language toolchain (TS + JS + Python) increases onboarding and CI complexity, especially for contributors touching validation plus deployment utilities (`package.json`, `scripts/requirements.txt`).

## Stale Dependencies / Commented-Out Code Signals

<!-- RUD-2776 -->

- Commented-out validation rules in `src/validator/index.ts` indicate intentionally disabled guardrails; track re-enablement to prevent drift.
- The Babel config (`.babelrc`) actively uses proposal-form plugins (`@babel/plugin-proposal-class-properties` and siblings, `loose: true`), so they are referenced rather than leftover even though tests transform via SWC (`jest.config.js::transform`); the proposal-style names are superseded by the `transform-*` equivalents in modern Babel and could be modernized later (`.babelrc`, `package.json` devDependencies).
- Repository metadata still references legacy `rudder-config-schema` naming in package fields while repo is `rudder-integrations-config`; mismatch can create confusion in external tooling/docs (`package.json` name/homepage/repository).

## INT-6502 — Versioned Destination Schema and Backend Coupling Risk

- Destination-definition validation is rooted in `src/schemas/destinations/db-config-schema.json`, and broad tests (`test/validation.test.ts`) validate every root destination `db-config.json`. Only the authored top-level key `version` is added to that schema; `fallbackVersion` is no longer authored on disk (it is computed on the fly downstream), and the `versions` archive is deploy-payload-only and must NOT be added to it, since the validated on-disk file never carries it.
- The broad validation path covers root destination definitions, not nested `versions/<major>/` artifacts. Their shape is enforced at deploy time by `build_versions_archive`, which raises on an invalid `version`/`status` or a missing config/configSchema/uiConfig slice rather than emitting a partial entry; a JSON-schema validation path for nested on-disk files is still absent and should land when the first real `versions/<major>/` tree is authored.
- New destination archive fields emitted by this repository have a dependency boundary with `rudder-config-backend`; the `destination_definitions` columns (`version`/`versions`) must exist there before this deploy change runs against an environment, since the payload now always carries them. `fallbackVersion` is computed on the fly by `rudder-config-backend` and is no longer authored on disk or emitted in the deploy payload. Deploy ordering is CBE-columns-first, then these versioned definitions.

## INT-6593 — Dev Deployment Slack Secret Mapping Risk

- `.github/workflows/deploy-to-dev.yml` has been observed mapping `SLACK_BOT_TOKEN` as `$$ {{ secrets.SLACK_BOT_TOKEN }}` with an extra `$` and a space inside the expression.
- That malformed expression can prevent the dev deployment path from receiving the intended Slack token, which makes dev an unreliable signal when validating deployment Slack notification changes.

## SDK-5013 — Amplitude Shared SDK Template Condition Risk

- Reusing an Amplitude `sdkTemplate.fields` field for a newly added web `destConfig` key can also apply that field's conditions to mobile copies of the same config key, because SDK template fields are copied into per-source SDK groups based on `db-config.json` `config.destConfig.<sourceType>`.
- Source-specific web-only behavior may require a renderer-supported source filter or a separate UI field shape instead of relying only on a field-level condition.

## INT-6598 — Hidden Gate Billing Feature Confirmation

- During INT-6598, beta hidden definitions with unknown billing feature names were migrated to single-flag `hidden.gate` entries that preserve the existing Flagsmith flag and boolean value instead of inventing billing feature names.
- Only two migrated definitions had confirmed two-flag gates at the time of the change: `src/configurations/destinations/snowpipe_streaming/db-config.json` uses `AMP_snowpipe_streaming` with `SNOWFLAKE_STREAMING`, and `src/configurations/sources/facebook_lead_ads_native/db-config.json` uses `AMP_enable-fbla-source` with `FBLA_SOURCE`.
- Remaining migrated beta gates still need confirmed billing feature additions before the GA no-release behavior is fully complete.

## AI-1226 — Heap Schema Generator Baseline Drift

- Running `scripts/schemaGenerator.py destination -name heap` during AI-1226 succeeded but reported pre-existing Heap schema drift around `consentManagement`: the generator expected each source's consent-management item schema to include `required: ["provider"]` and also printed the generic `additionalProperties: false` recommendation.
- The AI-1226 `dataResidency` field was not part of that generator diff, so future Heap schema maintenance should distinguish this baseline `consentManagement` drift from new field changes.
