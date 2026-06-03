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
