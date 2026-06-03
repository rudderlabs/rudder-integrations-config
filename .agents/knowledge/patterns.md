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
- Generic config validation and definition-policy validation are layered: schema-first via AJV, then custom rule pass for destination safety constraints (`src/validator/index.ts:198`, `src/validator/index.ts:232`).
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
