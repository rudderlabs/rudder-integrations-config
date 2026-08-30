# Integrations Versioning

## Summary

This document defines how we evolve integration definitions (destinations and sources) over time without breaking existing configurations. Today, any breaking change to an integration's config requires careful release coordination and forces all consumers (Web UI, Terraform, Public API) to update simultaneously.

This design introduces per-integration versioning so breaking changes can be rolled out easily, with each client migrating on its own schedule.

### Goals

- Introduce breaking changes to integration definitions without disrupting live configurations
- Let public API/Terraform users stay on older integration versions until they're ready to migrate
- Provide self-service, user-controlled migration
- Replace ad-hoc compatibility workarounds with a formal versioning contract

### Scope

**Destination definitions first.** Source definitions can adopt the same pattern once the destination rollout is proven.

Connection configurations (rETL) and other config types are out of scope for now.

---

## Current State

### Integration Definitions

Each integration (source or destination) in the `rudder-integrations-config` repository is defined using a standardized three-file pattern called a **RudderStack Resource Definition**. There are currently **239 destinations** and **116 sources** under `src/configurations/`.

The three files have distinct, non-overlapping responsibilities:

| File             | Concern              | What it contains                                                                                                                                                                                                                                          | Consumed by                                       |
| ---------------- | -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| `db-config.json` | **Service behavior** | Metadata and capability declarations — auth config, supported source types, connection modes, message types. Lists field **names** in `destConfig` arrays, `includeKeys`, `secretKeys`, etc.                                                              | All services (web app, control plane, data plane) |
| `schema.json`    | **Input validation** | JSON Schema Draft-07 that validates config payloads at the API layer. Defines field **types**, defaults, enum values, regex patterns, and conditional validation (`allOf`/`if-then`). Auto-generated from ui-config + db-config via `schemaGenerator.py`. | Config backend (AJV at runtime)                   |
| `ui-config.json` | **UI rendering**     | Drives the web app's form rendering — field widget types, labels, sections, groups, ordering, conditional visibility (`preRequisites`/`conditions`). Not used by any backend service.                                                                     | Web app only                                      |

A single configuration field (e.g., `restApiKey`) is described across all three files: its **name** appears in db-config's `destConfig` arrays, its **type and validation rules** in schema.json, and its **UI presentation** in ui-config.json. The `configKey` in ui-config maps 1:1 to property names in schema.json and field names in db-config lists.

### Clients

Multiple clients produce and consume integration configurations:

- **Web UI** — reads definition records (loaded from `db-config.json` and `ui-config.json`) to render config forms
- **Public API** (`rudder-api`) — thin API layer that accepts config payloads, forwards to config backend
- **Terraform provider** — transforms HCL to API payloads via a `ConfigProperty` pipeline (snake_case → camelCase, array flattening, discriminators), calls the public API
- **CLI** — reads/writes YAML specs, calls the public API

The **config backend** (`rudder-config-backend`) is the service that validates configs against definition schemas (AJV), extracts secrets to an external secrets service, and persists to the `destinations` table. It loads all definition schemas into memory at startup and compiles them with AJV.

The **data plane** (rudder-transformer) consumes stored config instances by directly accessing field names (e.g., `config.restApiKey`). It does not read the definition files — it receives config data from the config backend.

### Deployment Sequence

1. Transformer code (data plane) — deployed first so it can handle new field names
2. Integration definitions (this repo) — deployed to `destination_definitions` table via deploy script
3. Existing stored configs — migrated via ad-hoc scripts when fields change

---

## Problem Statement

Integration configurations are an **implicit contract** shared across the web app, public API, Terraform provider, control plane, and data plane — with no formal mechanism for evolving that contract.

When the team needs to make a breaking change (add a required field, rename a key, restructure config) in the definition, every consumer must update simultaneously.

In practice, this means:

### 1. Coordination Overhead

A single field change can require synchronized releases across 3+ repositories (integrations-config, transformer, control plane) and 4+ client surfaces (web app, API, Terraform).

### 2. Breaking Existing Configs

Stored configs in the database were created against an older definition. When the definition changes — say a field is renamed or a new required field is added — those stored configs become invalid against the new schema. There's no mechanism to keep old configs working while new configs use the updated definition.

### 3. Migration Burden

Every structural change requires a one-off migration script to update stored configs in the database. These scripts are created on ad-hoc basis.

### 4. Client Drift

The web app can be updated in lockstep with definition changes — it's deployed by the same team. But external clients can't:

- **Terraform** users have `.tf` files checked into their repos with hardcoded field names. A field rename causes `terraform plan` to show unexpected diffs or fail entirely. State drift is a production infrastructure risk.
- **Public API** consumers have integrations built against specific field names. Breaking changes without warning erode customer trust.

| Client         | Challenge                            | Impact                             |
| -------------- | ------------------------------------ | ---------------------------------- |
| **Web UI**     | Can be migrated during releases      | Low — automatic migration possible |
| **Terraform**  | State drift and plan failures        | High — breaks existing pipelines   |
| **Public API** | Integration breakage without warning | High — customer trust impact       |

### 5. Ad-Hoc Workarounds Create Tech Debt

Without versioning, the team resorts to compatibility hacks: keeping both old and new field names, creating resources behind the scenes for legacy configs, writing ambiguous validation logic that accepts both formats. These workarounds accumulate as technical debt.

### Concrete Example: Account Support

Adding account support to integrations (e.g., `rudderAccountId` as required field) forces existing API/Terraform users to update immediately. The current backwards-compatibility attempt illustrates all of the above pain points:

- Users updating via Terraform may inadvertently create duplicate accounts
- No clear way to identify which account corresponds to which configuration
- Validation becomes complex with mixed old/new integration definitions
- Creating accounts behind the scenes for legacy integrations leads to orphaned resources
- Applies to ANY integration (not just warehouses) — Iterable, Braze have similar org/project structures

### Change Categories

| Change Type             | Example                                                 | Severity             | Versioning Required |
| ----------------------- | ------------------------------------------------------- | -------------------- | ------------------- |
| Optional field addition | `deleteStagingFiles` (default: true)                    | Non-breaking         | No                  |
| Required field addition | `rudderAccountId` now mandatory                         | Breaking             | Yes                 |
| Field removal           | Deprecated `apiKey` removed                             | Breaking             | Yes                 |
| Field restructuring     | `oneTrustCookieCategories` becomes source type specific | Breaking             | Yes                 |
| Validation change       | Regex pattern update                                    | Potentially breaking | Conditional         |

See [change-scenarios.md](./change-scenarios.md) for the full taxonomy of 65+ change scenarios across schema.json, db-config.json, and ui-config.json.

---

## Solution

The core idea is to **assign a version to each integration definition change** and let multiple versions coexist.

When a breaking change is needed, a new major version is created. Existing configs continue to work against the old version's schema. Users migrate to the new version on their own schedule — through the web UI, CLI, or API.

This means:

- **No big-bang releases.** The definition, data plane, and user migration are decoupled steps.
- **No broken configs.** Stored configs are always valid against the version they were created with.
- **No forced client updates.** Terraform and CLI users stay on the old version until they choose to upgrade.
- **No ad-hoc scripts.** Migration logic is code that ships with the definition, testable in CI.

### How It Works

```
Client submits v1.0 config
       ↓
Validate against v1.0 schema
       ↓
Store v1.0 as-is (tagged with version)
       ↓
Serve v1.0 back to client unchanged
       ↓
User triggers v1.0 → v2.0 migration when ready
```

### Why This Approach

We evaluated two strategies for handling multiple versions:

| Criteria                  | Translate-on-Write (rejected)    | Version-Aware Storage (adopted)  |
| ------------------------- | -------------------------------- | -------------------------------- |
| Implementation complexity | High (bidirectional mapping)     | Medium                           |
| Data integrity risk       | High (translation bugs)          | Low (original preserved)         |
| Supports field removal    | No (can't reverse a deletion)    | Yes                              |
| Supports restructuring    | Difficult                        | Yes                              |
| Client flexibility        | Limited (all clients see latest) | High (each client picks version) |
| Storage overhead          | Low                              | Slightly higher                  |

**Translate-on-write** converts old configs to the latest format before storing, and reverse-translates on read. This sounds simpler but breaks down for destructive changes (field removal, type changes) where reverse translation is impossible. It also means you can never serve the original config back to a client that expects the old format.

**Version-aware storage** preserves configs exactly as submitted, tagged with their version. Each version has its own schema for validation. Migration is explicit and user-controlled. This is the approach we adopt.

---

## Architecture

### Version Identifier

Each integration definition is versioned independently using `major.minor` semantics:

- **Major version:** Breaking changes requiring explicit migration
- **Minor version:** Non-breaking additions or corrections with backward compatibility

**Clients send only the major version** (e.g., `"configVersion": 2`). The config backend resolves it to the latest minor of that major (e.g., `2.1`) and stores the full `major.minor` in the database. This means:

- Clients never need to track minor versions
- Schema defaults from the latest minor are always applied (via AJV `useDefaults: true`)
- The stored value reflects exactly which schema was used for validation

For human-readable references (docs, changelogs), the convention is `{integration_type}@{major}.{minor}` (e.g., `BRAZE@2.0`, `AM@1.3`).

### File Structure

```
src/configurations/destinations/braze/
├── db-config.json        # Always latest version (2.0), includes configVersion
├── ui-config.json        # Always latest version
├── schema.json           # Always latest version
├── CHANGELOG.md          # Documents what changed in each version
├── migrations/
│   └── 1-to-2.json      # Migration declaration (metadata only; code lives in config backend)
└── versions/
    └── 1/
        ├── db-config.json   # v1's own metadata (status, deprecation dates) + config
        ├── schema.json      # v1's validation schema (editable for minor fixes)
        └── ui-config.json   # v1's UI rendering config
```

### Version Changelog

Each versioned integration includes a `CHANGELOG.md` that documents what changed in each version. This serves as the user-facing reference for understanding version differences — what fields were added, removed, renamed, or restructured.

```markdown
# Braze Changelog

## 2.0 (2026-04-01)

- **BREAKING**: `restApiKey` renamed to `apiKey`
- **BREAKING**: `accountId` is now required
- `region` field added (defaults to "US")
- `legacyEndpoint` removed

## 1.1 (2026-03-15)

- Tightened regex validation for `restApiKey`

## 1.0 (2025-01-01)

- Initial version
```

The changelog is:

- **Maintained by the developer** making the version change (alongside the migration file and definition updates)
- **Surfaced in the web app** migration banner so users understand what's changing before they upgrade
- **Included in API deprecation notices** and documentation
- **Enforced by CI** — a PR that bumps a major version must include a changelog entry

The version directories are not frozen snapshots — they are living major version tracks.

When a non-breaking fix needs to go to older versions, the files in `versions/1/` are edited directly and the minor version in that directory's `db-config.json` is bumped (1.0 → 1.1). Breaking changes are never applied to older versions — users must migrate to the latest version.

Only major versions get their own directory; minor versions are edits within the same directory.

### Version Metadata

#### Version Metadata Schema

Every `db-config.json` — whether root or inside a version directory — uses the same `configVersion` object to describe itself:

| Field             | Type     | Required | Description                                             |
| ----------------- | -------- | -------- | ------------------------------------------------------- |
| `version`         | `string` | Yes      | Semantic version (`major.minor`)                        |
| `status`          | `string` | Yes      | One of: `current`, `supported`, `deprecated`, `retired` |
| `deprecationDate` | `string` | No       | ISO date when deprecation begins                        |
| `retirementDate`  | `string` | No       | ISO date when version is retired                        |
| `message`         | `string` | No       | Human-readable migration guidance                       |

**Root `db-config.json`** (always the latest version):

```json
{
  "name": "BRAZE",
  "displayName": "Braze",
  "configVersion": {
    "version": "2.0",
    "status": "current"
  },
  "config": { ... }
}
```

**Version directory `db-config.json`** (e.g., `versions/1/db-config.json`):

```json
{
  "name": "BRAZE",
  "displayName": "Braze",
  "configVersion": {
    "version": "1.0",
    "status": "deprecated",
    "deprecationDate": "2026-06-01",
    "retirementDate": "2026-12-01",
    "message": "Please migrate to 2.0."
  },
  "config": { ... }
}
```

The same `configVersion` object shape is used in every db-config.json — root and version directories. No separate catalog array needed; the deploy script assembles the full picture by scanning all version directories.

#### How Definitions Are Stored in the Database

The deployment script (`scripts/deployToDB.py`) merges all three files into a single flat JSON object and stores it as one record per integration in the `destination_definitions` table. The database doesn't know about the three-file split.

**Current** (no versioning) — flat merged blob:

```json
{
  "name": "BRAZE",
  "displayName": "Braze",
  "config": {
    "destConfig": { "defaultConfig": ["restApiKey", "dataCenter"], "web": ["enableBrazeLogging"] },
    "secretKeys": ["restApiKey"],
    "includeKeys": ["appKey", "dataCenter"],
    "supportedSourceTypes": ["android", "ios", "web", "cloud"],
    ...
  },
  "configSchema": {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["restApiKey", "dataCenter"],
    "properties": { "restApiKey": { "type": "string" }, ... }
  },
  "uiConfig": { "baseTemplate": [ ... ] },
  ...
}
```

**With versioning** — same record, top-level = latest version, older versions nested under `versions`:

```json
{
  "name": "BRAZE",
  "displayName": "Braze",
  "configVersion": { "version": "2.0", "status": "current" },
  "config": {
    "destConfig": { "defaultConfig": ["apiKey", "accountId", "dataCenter"], "web": ["enableBrazeLogging"] },
    "secretKeys": ["apiKey"],
    ...
  },
  "configSchema": {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "required": ["apiKey", "accountId", "dataCenter"],
    "properties": { "apiKey": { "type": "string" }, "accountId": { "type": "string" }, ... }
  },
  "uiConfig": { "baseTemplate": [ ... ] },

  "versions": {
    "1": {
      "configVersion": { "version": "1.0", "status": "deprecated", "deprecationDate": "2026-06-01" },
      "config": {
        "destConfig": { "defaultConfig": ["restApiKey", "dataCenter"], "web": ["enableBrazeLogging"] },
        "secretKeys": ["restApiKey"],
        ...
      },
      "configSchema": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "required": ["restApiKey", "dataCenter"],
        "properties": { "restApiKey": { "type": "string" }, ... }
      },
      "uiConfig": { "baseTemplate": [ ... ] }
    }
  }
}
```

**Why single record with nested versions:**

- **Backward compatible** — top-level fields remain the latest version, exactly as today. Existing consumers that don't know about versions keep working.
- **Atomic** — all versions of an integration are one record. No cross-row consistency concerns during deploys.
- **Minimal deploy change** — merge root files as today, then for each `versions/{major}/`, merge its three files and nest under `versions.{major}`.

**How consumers read it:**

- **Version-unaware consumers** (existing) — read top-level fields as before. Nothing changes.
- **Config backend** (version-aware) — at startup, compiles AJV schemas for each version: top-level `configSchema` for the current version, `versions.{major}.configSchema` for older versions. When processing a request, it selects the version-matched schema **and** the version-matched `config` metadata (`secretKeys`, `includeKeys`, `destConfig`, etc.) — not just the schema. This is critical because these lists change between versions (e.g., v1's `secretKeys: ["restApiKey"]` vs v2's `secretKeys: ["apiKey"]`).
- **Web app** (version-aware) — reads `versions.{major}.uiConfig` when rendering forms for an older version's config. Shows migration banner.
- **Data plane** — does not read the definition record. It receives the config instance from the config backend, which includes `configVersion` in the destination config payload. The data plane dispatches to the appropriate version-tagged handler based on `configVersion`.

For integrations that haven't been versioned yet, `configVersion` and `versions` are absent — they implicitly operate as `1.0`.

### How It Fits Together

```
┌─────────────┐              ┌─────────────┐  ┌─────────────┐
│   Web UI    │              │  Terraform  │  │    CLI      │
└──────┬──────┘              └──────┬──────┘  └──────┬──────┘
       │                            │                │
       │                            └────────────────┘
       │                                     │
       │                           configVersion in body
       │                                     │
       │                                     ▼
       │                           ┌──────────────────┐
       │                           │   Public API     │
       │                           │   (rudder-api)   │
       │                           └────────┬─────────┘
       │                                    │
       │    configVersion in body           │
       │                                    │
       └──────────────┬─────────────────────┘
                      │
                      ▼
             ┌──────────────────┐
             │  Config Backend  │  (rudder-config-backend)
             │  ┌────────────┐  │
             │  │ Version    │  │  - Resolves configVersion
             │  │ Resolution │  │  - Selects AJV schema per version
             │  │ + AJV      │  │  - Extracts secrets
             │  │ Validation │  │  - Migrate endpoint (read-only)
             │  │ + Migrate  │  │  - Persists to DB
             │  └────────────┘  │
             └────────┬─────────┘
                      │
         stores config as-is with configVersion
                      │
             ┌────────┴─────────┐
             ▼                  ▼
┌──────────────────┐  ┌──────────────────┐
│   destinations   │  │  destination_    │
│   table          │  │  definitions     │
│  (config +       │  │  table           │
│   configVersion) │  │  (versions.1     │
│                  │  │   nested blob)   │
└──────────────────┘  └────────┬─────────┘
                               │
                   data plane fetches config
                   (includes configVersion)
                               │
                               ▼
                  ┌──────────────────────┐
                  │     Data Plane       │
                  │  (rudder-transformer)│
                  │  dispatches to       │
                  │  version-tagged      │
                  │  handler             │
                  └──────────────────────┘
```

### How `configVersion` Flows Through the System

#### Current State (no versioning)

Today, a destination instance is stored in the `destinations` table with `config` as a JSON column. The entity has `id`, `name`, `config`, `enabled`, `destinationDefinitionId`, `workspaceId`, `revisionId`, `secretVersion`, etc. — but no version field.

The public API (`POST /v2/destinations`) accepts:

```json
{
  "name": "my-braze",
  "type": "BRAZE",
  "config": { "restApiKey": "xxx", "dataCenter": "US-01" },
  "enabled": true
}
```

The Terraform provider transforms HCL → API payload via a `ConfigProperty` pipeline (snake_case → camelCase, array flattening, discriminators) and sends:

```json
{
  "Type": "BRAZE",
  "Name": "my-braze",
  "Config": { "restApiKey": "xxx", "dataCenter": "US-01" },
  "IsEnabled": true
}
```

Both go to the config backend, which validates `config` against the definition's `configSchema` using AJV, extracts secrets, and persists to DB.

#### With Versioning

`configVersion` is a **request body field** — not a header. It travels with the payload, is easy to log/validate/store, and maps naturally to Terraform resource attributes.

**Public API** (`POST /v2/destinations`):

```json
{
  "name": "my-braze",
  "type": "BRAZE",
  "configVersion": 1,
  "config": { "restApiKey": "xxx", "dataCenter": "US-01" },
  "enabled": true
}
```

**Config backend** stores `configVersion` alongside the config in the `destinations` table — a new column on the destination entity:

```
destinations table
──────────────────
id                      KSUID
name                    string
config                  JSON (pruned, no secrets)
configVersion           string (nullable, default null → implicit 1)
                        Stores resolved major.minor (e.g., "2.1")
                        Client sends major only; config backend resolves to latest minor
destinationDefinitionId FK
workspaceId             FK
revisionId              KSUID
secretVersion           number
enabled                 boolean
...
```

The config backend's AJV validation selects the right compiled schema based on `configVersion`:

- If `configVersion` matches a version in `versions.{major}` → validate against that version's `configSchema`
- If `configVersion` matches the current version (or is resolved via defaulting) → validate against the top-level `configSchema`

**Response** includes the resolved `configVersion` (full `major.minor`) so clients know exactly which schema was used:

```json
{
  "id": "abc-123",
  "name": "my-braze",
  "type": "BRAZE",
  "configVersion": "1.0",
  "config": { "restApiKey": "****", "dataCenter": "US-01" },
  "enabled": true
}
```

#### Per-Client Behavior

Terraform and CLI go through the public API (`rudder-api`), which forwards to the config backend. The web UI calls the config backend directly. All paths converge at the config backend for version resolution and validation.

| Client         | Route                           | How it sends `configVersion`                                                                                                                                                                                                                                                            | Behavior                                                                                                                                                                  |
| -------------- | ------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Web UI**     | Direct → config backend         | Includes `configVersion` in request body automatically (from the definition's current version or the config's existing version)                                                                                                                                                         | Always shows latest for new configs; renders version-matched form for existing configs with migration banner                                                              |
| **Terraform**  | Via public API → config backend | Provider includes `configVersion` in the API payload. Each destination's `ConfigMeta` registration declares which definition version it targets. The provider's `Destination` struct gains a `ConfigVersion` field, and `populateDestinationFromState()` sets it from the `ConfigMeta`. | Users don't set `configVersion` in HCL directly — it's baked into the provider version. Upgrading the provider and running `terraform plan` surfaces new required fields. |
| **CLI**        | Via public API → config backend | Includes `configVersion` in YAML spec, sent as body field                                                                                                                                                                                                                               | Warns on deprecated versions. `rudder-cli migrate` command for interactive migration.                                                                                     |
| **Direct API** | Via public API → config backend | Explicit `configVersion` in request body                                                                                                                                                                                                                                                | Full control. Omitting defaults to current version for new configs.                                                                                                       |

#### Version Resolution

When a request includes `configVersion`:

- Config backend resolves the major version to the latest minor (e.g., `2` → `2.1`)
- Validates against that version's schema
- Stores the resolved `major.minor` in the database

When `configVersion` is omitted:

For **new configs** (create):

- Config backend defaults to the definition's current major version (latest). Safe because there are no pre-existing field expectations.

For **existing configs** (update):

- Config backend preserves the stored `configVersion`. No implicit upgrade.

For **existing configs with no stored `configVersion`** (pre-versioning):

- All configs created before versioning was introduced have `configVersion = null` in the database. The config backend treats `null` as major version `1`. These configs continue to validate against the v1 schema until the user explicitly migrates.

#### Transition Strategy

When versioning is first introduced, no existing clients send `configVersion`. The rollout happens in phases:

1. **Phase 1 (launch):** `configVersion` is optional. Omitting it defaults to the current version for new configs, and preserves stored version for updates. All pre-existing configs are implicitly v1. This is fully backward compatible — no client changes needed.

2. **Phase 2 (adoption):** New Terraform provider and CLI versions start sending `configVersion`. Public API docs recommend including it. Web UI always sends it.

3. **Phase 3 (enforcement):** After sufficient adoption, `configVersion` becomes required for the public API. Requests without it receive a deprecation warning, then eventually a validation error. This pushes remaining clients to be version-aware.

The key invariant: **existing stored configs with `null` version are always treated as v1**, regardless of what the latest version is. A client that never updates its code continues to work against v1 until they explicitly migrate.

---

## Migration Service

Migration runs as part of the existing config backend service — no new microservice needed. Migration is split across two repos:

- **Declarations** (metadata) live in this repo alongside the definition
- **Implementations** (code) live in the config backend where they execute

### Migration Declaration (this repo)

Each breaking change includes a JSON declaration that describes the migration without containing the transformation code:

```json
// migrations/1-to-2.json
{
  "from": 1,
  "to": 2,
  "description": "Added account support, consolidated API key fields"
}
```

This declaration serves CI validation — the break detection guardrail checks that every breaking change has a corresponding declaration. The actual migration logic is not here.

### Migration Implementation (config backend)

The transformation code lives in the config backend repo, following a mirrored directory structure:

```
rudder-config-backend/
└── src/migrations/destinations/
    ├── braze/
    │   ├── 1-to-2.ts          # Migration implementation
    │   └── 1-to-2.test.ts     # Tests with sample configs
    ├── am/
    │   └── 1-to-2.ts
    └── registry.ts             # Auto-discovers and registers migrations
```

```typescript
// src/migrations/destinations/braze/1-to-2.ts
export const migration = {
  version: { from: 1, to: 2 },

  migrate(config: Record<string, unknown>) {
    const migrated = { ...config };

    // Rename
    migrated.apiKey = migrated.restApiKey;
    delete migrated.restApiKey;

    // Add field with default
    migrated.region = migrated.region || 'US';

    // Remove deprecated field
    delete migrated.legacyEndpoint;

    return migrated;
  },
};
```

**Deployment ordering:** Config backend (with migration code) deploys first, then definitions deploy to the database. This mirrors the existing pattern — transformer deploys version-tagged handlers before definitions land.

**Coordination:** A breaking change requires PRs in both repos on the same ticket. CI in this repo validates migration declarations exist; CI in config backend validates implementations exist and pass smoke tests against sample configs.

### Why Migration Code Lives in Config Backend (not this repo)

Migration functions are imperative code that executes in the config backend. Keeping them where they run gives us:

- **Standard TypeScript** — type-safe, debuggable, testable with the config backend's existing test framework
- **No stored code execution** — no `vm` module, no `eval`, no sandboxing
- **Access to utilities** — lodash, shared helpers, etc.
- **This repo stays declarative** — schemas, metadata, and UI config are all data, not code

**Rejected alternatives:**

- **Store migration JS in the definition record** — deploy script serializes code as a string, config backend executes via Node.js `vm` module. Rejected: stored code execution is a security surface; debugging serialized strings is painful; no TypeScript support; can't use utility libraries.
- **Config backend depends on this repo as npm package** — import migration functions directly. Rejected: tight deployment coupling; config backend must redeploy for every new migration, partially defeating the decoupling this design provides.
- **Migration files deployed to shared storage (S3)** — deploy script uploads JS to S3, config backend loads at runtime. Rejected: extra infrastructure; cache invalidation complexity; another failure point.

### How Migration Works

Migration has two parts: a **read-only migrate endpoint** (used by all clients to get the migrated config) and the **normal update path** (used by all clients to persist the final config). The config backend never implicitly runs `migrate()` during a normal update — it only validates.

#### Migrate Endpoint (read-only)

The config backend exposes a migrate endpoint that runs `migrate()` and returns the result without persisting:

```
POST /destinations/<id>/migrate
{ "targetVersion": 2 }
```

```javascript
// Config backend pseudocode
const stored = getDestination(id);
const migration = loadMigration(stored.configVersion, targetVersion);
const migrated = migration.migrate(cloneDeep(stored.config));
const validation = ajv.validate(targetSchema, migrated);
return {
  config: migrated, // transformed config
  validationErrors: validation.errors, // missing required fields, type mismatches
};
```

All clients can use this endpoint to bootstrap the migrated config. The web app uses it to pre-fill the v2 form; CLI/API clients use it to get a starting point before submitting the final update.

#### Update Path (persist)

The normal destination update API (`PUT /destinations/<id>`) does not run `migrate()`. It simply validates the submitted config against the requested version's schema and persists:

```javascript
// Config backend pseudocode — normal update
const schema = resolveSchema(request.configVersion); // v1 or v2 schema
const valid = ajv.validate(schema, request.config);
if (!valid) return { errors: ajv.errors };
persist(id, request.config, request.configVersion);
```

The client is responsible for sending a complete, valid config for the target version. The config backend just validates and stores.

### How Users Trigger Migration

#### Web UI

The dashboard shows a migration banner on the destination settings page when a newer version is available.

1. User clicks "Upgrade to v2.0"
2. Web app calls the **migrate endpoint** — config backend runs `migrate()` on the stored config and returns the transformed result with any validation errors
3. Web app renders the **v2 form** (from v2 definition's `uiConfig`), pre-filled with the migrated values
4. Fields that failed validation (e.g., missing `accountId`) are highlighted for user input
5. User fills in the missing fields
6. Web app submits a **normal update** with `configVersion: 2` and the full v2 config
7. Config backend validates against v2 schema and persists

#### CLI / Direct API

Clients can call the migrate endpoint first to get the migrated config, then fill in any missing fields and submit a normal update:

```
# Step 1: Call migrate endpoint — returns migrated config + validation errors
POST /v2/destinations/<id>/migrate
{ "targetVersion": 2 }

# Response:
{
  "config": { "apiKey": "xxx", "region": "US", "dataCenter": "US-01" },
  "validationErrors": [{ "keyword": "required", "params": { "missingProperty": "accountId" } }]
}

# Step 2: Normal update with the full v2 config (migrated + user-supplied fields)
PUT /v2/destinations/<id>
{ "configVersion": 2, "config": { "apiKey": "xxx", "accountId": "abc", "region": "US", "dataCenter": "US-01" } }
```

If the client already knows the v2 schema, they can skip the migrate endpoint and send the full v2 config directly.

#### Terraform

The provider constructs the full v2 config from HCL — no migrate endpoint needed:

1. User upgrades the Terraform provider version (which targets the new definition version)
2. `terraform plan` shows the diff — new required fields appear as missing, removed fields show as deleted
3. User updates their `.tf` file to match the new schema (adds `account_id`, renames `rest_api_key` → `api_key`, etc.)
4. `terraform apply` sends a normal update with the new `configVersion` (set by the provider) and the full v2 config
5. Config backend validates against v2 schema and persists

This is the standard Terraform workflow — provider upgrades surface schema changes through `plan`/`apply`, and users adapt their configuration files accordingly.

### Migration Constraints

- **Forward-only** — no rollback. Users should test migrations in staging first.
- **Chainable** — migrating from v1 to v3 runs `1-to-2.js` then `2-to-3.js` sequentially. The migrate endpoint handles this automatically.
- **May require user input** — fields required in the target version that `migrate()` can't auto-produce are detected via schema validation and prompted to the user.
- **Atomic** — either the full migration succeeds or nothing changes. No partial state.

Note: Migration audit is not a separate concern — the existing `destinations_history` table already captures every update with `revisionId` and action type. A version change is just a normal update.

---

## Version Lifecycle

Each definition version progresses through these states:

| State          | What it means                          | What clients see                              |
| -------------- | -------------------------------------- | --------------------------------------------- |
| **Current**    | The recommended version for production | Default for newly created integrations.       |
| **Supported**  | Still works, but superseded            | Fully functional. Dashboard suggests upgrade. |
| **Deprecated** | End-of-life date announced             | Warning headers/banners on every operation.   |
| **Retired**    | Removed from service                   | Requests rejected. Migration required.        |

### Policies

- At most **2 major versions** coexist at any time
- Minimum **6 months** between deprecation announcement and retirement
- Non-breaking bug fixes and improvements go to **all supported versions** (minor bumps)
- **Breaking changes only go to the current version** (major bump). Older versions do not receive breaking changes — users on older versions must migrate to the latest to get the fix.
- Deprecation is communicated through **all channels**: API `Deprecation`/`Sunset` headers per RFC 8594, dashboard banners, email to workspace admins, and changelog entries

### What Triggers a Version Bump?

| Change Type                        | Where it goes          | Version Impact |
| ---------------------------------- | ---------------------- | -------------- |
| Bug fix (non-breaking)             | All supported versions | Minor bump     |
| Security fix (non-breaking)        | All supported versions | Minor bump     |
| New optional field                 | Current version only   | Minor bump     |
| New required field                 | New major version      | Major bump     |
| Field removal/restructure          | New major version      | Major bump     |
| Breaking fix (e.g., tighten regex) | Current version only   | Major bump     |

### Breaking Changes for Older Versions

If a breaking fix is needed (e.g., tightening a regex) that affects both current and older versions:

- **Current version** → major bump as normal (e.g., v2.0 → v3.0)
- **Older versions** → do **not** receive the breaking fix. Instead, users on older versions are prompted to migrate to the latest version which includes the fix.

This avoids the complexity of maintaining breaking changes across old version branches, which would defeat the purpose of versioning (stable contracts for each version). If a fix is critical enough to break configs, those users should be on the latest version.

Non-breaking fixes (bug fixes that don't change the contract) can still go to older versions as minor bumps.

### Rollout Lifecycle

#### Step 1: Introduce Breaking Change (this repo)

1. Copy current root files (`db-config.json`, `ui-config.json`, `schema.json`) to `versions/1/`
2. Add `configVersion` to `versions/1/db-config.json`: `{ "version": "1.0", "status": "supported" }`
3. Create migration declaration: `migrations/1-to-2.json` (and corresponding implementation in config backend)
4. Update root `db-config.json` with `configVersion`: `{ "version": "2.0", "status": "current" }`
5. Make breaking changes to root `db-config.json`, `ui-config.json` (and regenerate `schema.json`)
6. Deploy definitions — the deploy script merges `versions/1/` into the definition record under `versions.1`

#### Step 2: Data Plane Update (transformer team)

1. Data plane adds `2.0` field handling **alongside** existing `1.0` handling via version-tagged handlers (e.g., `brazeV1.process()`, `brazeV2.process()`)
2. Router dispatches to the right handler based on `configVersion` (which the data plane receives as part of the destination config from the config backend)
3. Deploy data plane — now handles both `1.0` and `2.0`

#### Step 3: User-Triggered Migration

1. Web UI shows migration banner on existing `1.0` destinations
2. User clicks "Upgrade to v2.0" — web app calls the migrate endpoint, gets migrated config pre-filled into the v2 form, user fills in any remaining required fields, submits a normal update with `configVersion: 2`
3. Terraform/CLI/API users construct v2 configs and submit normal updates with `configVersion: 2` at their own pace

#### Step 4: Deprecation & Retirement

1. After deprecation period → update `versions/1/db-config.json`'s `configVersion.status` to `"deprecated"` (warnings on every operation)
2. After retirement date → update status to `"retired"` (requests rejected, forced migration required)
3. Data plane drops `1.0` handling
4. Optionally clean up `versions/1/`, `migrations/1-to-2.json`, and the migration implementation in config backend

### How Validation Works Per Version

```
Client sends: { configVersion: 1, config: { restApiKey: "xxx" } }
  → Config backend resolves 1 → latest minor "1.0"
  → Looks up BRAZE definition, finds versions.1.configSchema
  → Validates against v1 compiled AJV schema ✓
  → Stores config with configVersion: "1.0" in destinations table
  → Config remains at v1 until user explicitly migrates

Client sends: { configVersion: 2, config: { apiKey: "xxx", accountId: "abc" } }
  → Config backend resolves 2 → latest minor "2.1"
  → Validates against top-level configSchema (current) ✓
  → AJV applies defaults for new optional fields added in 2.1
  → Stores config with configVersion: "2.1"

Client sends: { config: { apiKey: "xxx", accountId: "abc" } }  (no version, new config)
  → Config backend defaults to current major (2), resolves to "2.1"
  → Validates against top-level configSchema ✓
  → Stores config with configVersion: "2.1"
```

---

## CI Guardrails

The CI pipeline enforces versioning discipline automatically:

1. **Break detection** — Diffs schema.json + db-config.json against the previous version. If a breaking change is detected, the PR must include a migration declaration (`migrations/X-to-Y.json`) and a `versions/{major}/` directory for the old version. Otherwise it fails.
2. **Version directory integrity** — Changes to `versions/` directories must be accompanied by a minor version bump in that version's `db-config.json`.
3. **Migration declaration validation** — Checks that every breaking change has a corresponding migration declaration in this repo. The actual migration **smoke tests** (running `migrate()` against sample configs and validating output) run in the config backend's CI, where the implementation lives.
4. **Version bookkeeping** — Checks that every `versions/{major}/` directory has a valid `configVersion` in its `db-config.json`, and that no version directory exists without being referenced.
5. **Changelog required** — A PR that bumps a major version must include a `CHANGELOG.md` entry.
6. **Version ceiling** — Rejects PRs that would create more than 2 simultaneously supported major versions.
7. **Schema generation first** — Runs `schemaGenerator.py` before break detection, so the comparison uses the generated schema, not a stale one.

**Important:** ui-config.json changes alone never trigger a version bump. The schema auto-generation pipeline may cause a ui-config edit to produce a schema diff, but the version decision is always based on the resulting schema.json/db-config.json change — not the ui-config.json change itself.

---

## Risks

| What could go wrong            | How bad  | Prevention                                     | Recovery                        |
| ------------------------------ | -------- | ---------------------------------------------- | ------------------------------- |
| Migration corrupts config data | Critical | Atomic transactions, original config preserved | Restore from audit log          |
| Terraform state drifts         | High     | Provider pins to supported version range       | `terraform import` with version |
| Users confused by versions     | Medium   | Migration guides, dashboard prompts            | Support team playbook           |
| Schema resolution slows API    | Medium   | Cache compiled schemas per version             | Horizontal scaling              |
| Too many versions accumulate   | Low      | Hard cap of 2 major versions in CI             | Automated retirement scripts    |

---

## What This Unblocks

| Today's Problem                  | How Versioning Solves It                                                                                        |
| -------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| **Coordinated big-bang deploys** | Config, data plane, and user migration happen independently — no synchronized release needed.                   |
| **Breaking live configs**        | Configs stay in their original version until the user explicitly migrates. Nothing breaks silently.             |
| **One-off migration scripts**    | Reusable migration-as-code with `migrate()`. Testable in CI, executable in config backend via migrate endpoint. |
| **Clients fall out of sync**     | Each client (Web UI, Terraform, CLI, API) migrates on its own schedule. Version in request ensures correctness. |
| **Account support is stuck**     | `rudderAccountId` ships as a v2 required field. v1 users keep working. v2 users provide it during migration.    |

---

## All Design Decisions

### Architecture

1. **Version within same integration** — NOT creating new v2 folders
2. **Multi-version storage** — configs stored as-is in their original version, tagged with version
3. **User-triggered migration** — users explicitly migrate when ready; not batch-forced
4. **Migration via normal update API** — no implicit migration during updates. Config backend only validates and persists. All clients can use the read-only migrate endpoint to get the migrated config first, then submit a normal update with the complete v2 config.
5. **Migration split: declarations here, code in config backend** — migration metadata (JSON declarations) live in this repo for CI validation; migration implementations (TypeScript) live in the config backend where they execute. No stored code execution.
6. **Data plane handles multiple versions** — version-tagged handlers; router dispatches by configVersion
7. **Forward-only, chainable migrations** — v1→v2→v3; no downgrade
8. **Integration-level versioning** — not workspace-level; each integration instance carries its own version
9. **Semantic versioning per integration** — major.minor (clients send major only; config backend resolves to latest minor)
10. **Destinations first** — sources can follow the same pattern once proven; connection configs (RETL) are out of scope for now

### API & Client Behavior

1. **`configVersion` as request body field** — clients send major version only (e.g., `2`); config backend resolves to latest minor and stores full `major.minor`
2. **Smart defaulting** — new configs default to current version; existing configs preserve their stored version; old clients (no `configVersion`) treated as v1
3. **Three-phase transition** — `configVersion` starts optional, becomes recommended, then required for the public API
4. **Terraform provider version determines definition version support** — `configVersion` is set by the provider, not by users in HCL

### Lifecycle & Policy

1. **Max 2 major versions simultaneously**
2. **6-month minimum deprecation notice** before retirement
3. **Non-breaking fixes to old versions bump minor** — applied directly in `versions/{major}/`
4. **Breaking fixes skip old versions** — users must migrate to latest to get breaking fixes; no breaking changes to old version branches

### Versioning Scope

1. **ui-config.json never directly triggers versioning** — only schema.json and db-config.json changes trigger version bumps
2. **options.deprecated is separate** — whole-integration deprecation (GA→GA4) is orthogonal to version lifecycle states
3. **Web app: version-aware editing** — renders form matching config's version, with migration banner

### Infrastructure

1. **Migrate endpoint in config backend** — read-only `POST /destinations/<id>/migrate` that runs `migrate()` and returns transformed config + validation errors; usable by all clients to bootstrap the migrated config before submitting a normal update
2. **Terraform: provider blocks on version mismatch** — clear error guides user to migrate first, then upgrade provider
3. **Deprecation: multi-channel communication** — API headers (RFC 8594) + dashboard banners + email + changelog
4. **Definition storage: single record with nested versions** — `versions.{major}` nested in the definition record; config backend projects the right version at read time
5. **Instance storage: `configVersion` column on `destinations` table** — nullable string; `null` = implicit major version `1`
6. **Version-specific config processing** — config backend uses version-matched `config` metadata (`secretKeys`, `includeKeys`, `destConfig`) when processing requests — not just the version-matched schema
7. **Data plane `configVersion` delivery** — config backend includes `configVersion` in the destination config payload sent to the data plane, enabling version-tagged handler dispatch

### Future

1. **Schema consolidation** — merge 3 files into `definition.json` (see [schema-consolidation.md](./schema-consolidation.md))
2. **Version discovery API** — deferred until demand arises

---

## Related Documents

- [Change Scenario Taxonomy](./change-scenarios.md) — comprehensive catalog of 65+ change types across schema.json, db-config.json, and ui-config.json, classified as safe/breaking/conditional
- [Schema Consolidation Proposal](./schema-consolidation.md) — future design for merging 3 files into a single `definition.json`, with a full Braze example
- [Prior Research (Notion)](https://www.notion.so/rudderstacks/Destination-Definition-Versioning-Research-Doc-2eff2b415dd080a893e3d745c7d7b34e) — earlier exploration of versioning options and architecture
