# Patterns

> Recurring idioms specific to this repo (error handling, state management,
> retries, logging, DI, request lifecycle).
> Append-only. Agent-authored sections may optionally carry an HTML-comment tag
> (e.g., `<!-- pr:<id> -->`) identifying the writer/PR/run; human-authored
> sections are conventionally left untouched by automated runs.
> Where possible, include a `file:line` reference (or `file::symbol`) for each observed idiom.

## Validation and Error Surfacing

<!-- RUD-2776 -->

- Validation failures are normalized into JSON-stringified error arrays so callers/tests can assert deterministic messages (`src/validator/index.ts::validateConfig`, `src/validator/index.ts::validateDestinationDefinitions`).
- Generic config validation and definition-policy validation are layered: schema-first via AJV, then custom rule pass for destination safety constraints (`src/validator/index.ts:222`, `src/validator/index.ts:232`).
- Missing validator behavior is configurable through `throwErrorOnMissingValidations`, letting strict consumers fail fast while permissive flows continue (`src/validator/index.ts:177`).

## Script Orchestration Pattern

<!-- RUD-2776 -->

- Node scripts favor directory scans + per-item processing for mass integration operations (`scripts/preProcess.js::getDestinationNames`, `scripts/generateConstants.js::prepareDestinations`).
- Python deploy scripts use argument/environment fallback and produce summary-first reports, with optional verbose request logging (`scripts/deployToDB.py::get_command_line_arguments`, `scripts/deployAccountsToDB.py::print_summary`, `scripts/utils.py::log_api_request`).
- Schema generation intentionally excludes noisy diff paths to keep reviewable schema updates focused (`scripts/schemaGenerator.py::DIFF_EXCLUDE_PATHS`).

## State Management

<!-- RUD-2776 -->

- Validator state is cached in-process as a module-level `validators` map populated once by `init`, then reused for per-config validation calls (`src/validator/index.ts:21`, `src/validator/index.ts::initAjvValidators`).
- Deploy/update scripts compute in-memory diff reports (`jsondiff`) before deciding whether to call remote update/create APIs (`scripts/deployToDB.py::update_diff_db`, `scripts/deployAccountsToDB.py::update_account_db`).

## RUD-2776 — Documentation-Only Validation Scope

- No repo-local CI optimization currently skips tests for documentation-only changes; pull requests still run the standard `Tests` and `Code quality checks` workflows (`.github/workflows/test.yml`, `.github/workflows/verify.yml`).
- If a docs-only validation workflow is introduced later, document the criteria and workflow path here.

## INT-6529 — Versioned Destination Field Sync Pattern

- For destination fields exposed as UI selects and enforced in schema (for example Klaviyo `apiVersion`), changes should be made atomically across UI options and schema enum/defaults; treating these as a single change unit avoids publishing a UI option that backend schema validation rejects.
- When product requirements are explicitly unresolved (for example conditional non-empty consent rules for a specific API version), keep existing schema validation behavior unchanged and defer stricter conditional rules until approved, while preserving current safe defaults.

## INT-6540 — Resolve Ref by Trigger Context in Reusable Workflows

- In reusable workflow chains, add an explicit `deployment_ref` input for `workflow_call` paths because pull request context is not guaranteed.
- Resolve the effective ref once (caller-supplied for `workflow_call`; PR head SHA for merged release PR paths) and reuse that value consistently for checkout, version extraction, and downstream deploy inputs.

## INT-6502 — Import-Safe Python CLI Pattern

- For Python deploy tooling, keep argument parsing and runtime config initialization behind a `__main__`-only path so module imports remain side-effect free (importable without triggering CLI parsing).
- `scripts/deployToDB.py` follows this by delaying CLI/runtime initialization to `initialize_runtime_config()` at execution time, which preserves command-line behavior while keeping the module safe to import.

## INT-6593 — Deployment Slack Notification Gates

- In `.github/workflows/deploy.yml`, release-channel success Slack messages remain opt-in: they are gated by `inputs.notify == true && inputs.dry_run == false`.
- Deployment failure alerts are intentionally broader: the failure alert gate is `failure() && inputs.dry_run == false` and does not include `inputs.notify`, so internal responders are notified for every real deployment failure.
- Dry runs should suppress both success and failure Slack notifications; real deployment failures should notify internal channels even when optional release notifications are disabled.

## SDK-5013 — Amplitude Browser SDK Version Gating

- Amplitude `ui-config.json` gates the legacy "Save Referrer, URL Params, GCLID only once per session" field with a `conditions.expression` built from an `operator` (`AND`/`OR`) plus an `operands` array — each operand is `{ type: "configuration", key, value }`. There is no top-level `expression.type`; the `type: "configuration"` lives on the operands. This field ANDs `connectionMode.web == "device"` with `sdkVersion.web == 1`.
- Reuse that operand pattern (wrapped in the required `AND`/`OR` expression structure) for other Amplitude Browser SDK settings that need SDK-version-specific visibility.
- When extending an existing Amplitude config object to web, prefer adding a `web` boolean property to the existing object in `schema.json` and adding the same key to `db-config.json` `config.destConfig.web`, rather than introducing a parallel key.

## INT-7070 — OpenAI Ads Declarative Validation Pattern

- OpenAI Ads destination config stays within the repository's declarative JSON validation model: `src/configurations/destinations/openai_ads/schema.json` enforces flat destination-wide event-filtering fields, duplicate event mappings with `uniqueItemProperties: ["from"]`, and `customEventName` only when an event mapping's `to` value is `custom`.
- The OpenAI Ads `eventMapping.from` uniqueness rule only catches exact duplicate values. AJV keywords used in this repo do not provide trim/lowercase uniqueness for array item properties, so normalized lookup semantics should be handled outside the destination schema unless a broader custom validator path is introduced.
- OpenAI Ads is account-backed, but account option/secret fields are mirrored in destination metadata for generic account validation; avoid destination-specific validator exemptions and keep non-device account plumbing out of `config.includeKeys`.

## INT-7144 — Form Builder V2 Conditional Required Schema Pattern

- For Google Ads Offline Conversions, keep the `subAccount` to `loginCustomerId` requiredness rule scoped to the destination schema. Do not add a shared `scripts/schemaGenerator.py` workaround for this migration unless a broader Form Builder V2 generator change is explicitly requested.
- Form Builder V2 schema generation intentionally avoids adding Initial setup fields that have `preRequisites` to the top-level schema `required` array; conditional requiredness for hidden/gated fields should stay in destination-specific conditional schema branches instead of becoming unconditional required fields.

## ANA-134 — Destination Definition Guardrails

- Destination-definition custom rules in `src/validator/index.ts` are the right layer for cross-key `db-config.json` constraints that the JSON Schema cannot express through `destConfig` pattern properties, such as forbidding event-filtering fields in non-`defaultConfig` source sections.
- `test/validator/validator.test.ts` should cover these custom rules with minimal destination definitions passed to `validateDestinationDefinitions()`, including positive cases for absent optional structures and negative cases that assert the offending field names and `destConfig.<section>` path in the error.

## ACT2-855 — Source Account Conditional Authentication

<!-- session: 2026-09-24 -->

- In account `combinedSchema` conditionals such as `src/configurations/sources/bigquery/accounts/SOURCE_BIGQUERY/schema.json`, put `required: ["authMethod"]` inside the `if.properties.options` branch. Without that nested requirement, JSON Schema treats a missing discriminator as a match and can route legacy accounts into the new authentication branch.
- Keep authentication-specific requiredness in `combinedSchema`, not the standalone `secretSchema`: keyed accounts require `secret.credentials`, while keyless WIF accounts require their non-secret federation identifiers under `options`.
- `combinedSchema` runs on config-backend account API Merge edits, not the webapp's initial account-save route. Because the webapp retains hidden values, let the WIF branch accept absent credentials or `credentials: ""`, while rejecting a non-empty service-account key when combined validation runs.
- BigQuery source UI uses two fields bound to the same `project` value. The service-account-key field preserves the legacy read-only `credentials.project_id` autofill, while the feature-gated WIF field is editable and accepts domain-scoped project IDs. Enabling WIF depends on rudder-webapp ACT2-870 so `WarehouseAccountForm.onChange` autofills only visible fields; otherwise the hidden key field can overwrite the typed WIF project with `''`.
- Gate the derived `serviceAccount` summary field to the service-account-key path so keyless WIF accounts are not blocked by a credential-derived display field.
- Keep `combinedSchema.options` open to additional properties because the BigQuery source UI can round-trip the derived, display-only `serviceAccount` value even though it is not an authored runtime account option.
- Keep authentication-specific regex constraints in the active `combinedSchema` branch rather than the standalone options schema, because legacy account paths may validate the standalone schema without regard to the selected authentication method.
- WIF setup copy must instruct customers to scope GCP trust to `assumed-role/data-plane-service-account/<workspaceID>`, not to the entire RudderStack AWS role.
