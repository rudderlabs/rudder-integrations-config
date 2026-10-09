---
name: bootstrap-new-destination
description: Scaffold a new RudderStack destination definition from a display name — asks for source types, category, connection modes, and message types via interactive forms, then creates db-config.json, ui-config.json, schema.json (from the canonical templates) plus the validation test-data file under src/configurations/destinations/<dir>/. Works for cloud, device, hybrid, or warehouse destinations. For Visual Data Mapper destinations use vdm-next-integration; to move an existing destination onto the accounts framework use migrate-to-accounts-framework.
argument-hint: '<Display Name>'
---

# Bootstrap a New Destination Definition

**Objective:** Create a new destination _definition_ — the three config files plus its validation test data — by filling in the canonical templates.

## Scope

Bootstraps the configuration definition from `scripts/template-db-config.json` and `scripts/template-ui-config.json`. Handles **strictly cloud, strictly device, hybrid, or warehouse** destinations. Not for:

- **Visual Data Mapper destination** → `vdm-next-integration`
- **Moving an existing destination's auth onto the accounts framework** → `migrate-to-accounts-framework`

A **net-new account-backed destination** starts here. Scaffold it with this skill, then follow `migrate-to-accounts-framework` Steps 1–6 for the account definition, taking the net-new branch wherever that skill offers one. Its Step 1 is where the account's credential fields are collected, since this skill deliberately gathers none. Two things are easy to miss. The destination `schema.json` declares `rudderAccountId` with `"pattern": "^.{1,100}$"` (not just `required`), so an empty linked-account id is rejected. It has no `oneOf`, because there are no legacy auth fields to stay mutually exclusive with.

## Inputs

Argument: **display name** (`$ARGUMENTS[0]`, e.g. `Acme CRM`). Derive — do not ask:

- **Directory** = display name lowercased, non-alphanumerics → single underscores: `acme_crm`.
- **Definition name** (`name` field) = display name uppercased, same underscoring: `ACME_CRM`.

Gather everything else with explicit **`AskUserQuestion` forms, in this order**. Possible values come from the db-config template and meta-schema (`src/schemas/destinations/db-config-schema.json`). The form tool caps each question at **4 options** (and 4 questions per call), so longer lists are split into the groups shown.

**Form 1 — Source types** (multi-select) → `supportedSourceTypes`. First ask one yes/no — **support all standard source types?** "All" = the template's full list (14, including `warehouse` and `cloudSource`). Pick "no" to choose a subset via four grouped questions in one call:

- Web & server: `web`, `amp`, `cloud`, `warehouse`
- Mobile native: `android`, `androidKotlin`, `ios`, `iosSwift`
- Cross-platform: `reactnative`, `flutter`, `cordova`, `unity`
- Other: `shopify`, `cloudSource`

**Form 2 — Category** (single-select): `warehouse` | `other`.

- `warehouse` → set top-level `"category": "warehouse"`; every source type is `cloud` mode, so **skip Forms 3–4**. Example: `microsoft_fabric` for the form structure, `postgres`/`bq` for the shared warehouse settings — **not** a wholesale copy; see [Warehouse destinations](#warehouse-destinations).
- `other` → no `category` field. Example: `active_campaign`.

**Form 3 — Connection topology** (single-select, pre-emptive shortcut): **pure cloud** (every source type is cloud mode) or **heterogeneous** (connection mode varies by source type). Auto-set to pure cloud when category = `warehouse` — skip this form.

- pure cloud → `supportedConnectionModes` = `{ <src>: ["cloud"] }` for every source type; **skip Form 4**.
- heterogeneous → continue to Form 4.

**Form 4 — Connection mode per source type** (only when heterogeneous; one multi-select per source type from Form 1; options `cloud`, `device`, `hybrid`; ≤4 source types per call) → `supportedConnectionModes` = `{ <src>: [...modes] }`.

**Form 5 — Supported message types** (multi-select) → `supportedMessageTypes`. Event types as two grouped questions: `track`, `identify`, `page`, `screen` and `group`, `alias`, `audiencelist`, `record`. Assemble:

- pure cloud → `{ "cloud": [<events>] }` (one event-type selection).
- heterogeneous → ask per connection mode, then per source type for device/hybrid: `{ "cloud": [<events>], "device": { "<src>": [<events>] }, "hybrid": { "<src>": [<events>] } }` (cloud stays a flat array).

**Do not ask for connection or auth field details.** Seed a single neutral `placeholderKey` field, mirrored across `destConfig.defaultConfig`, the ui-config `fields`, and the schema `properties` — so the scaffold validates and stays internally consistent (`secretKeys` stays `[]`). Replace `placeholderKey` with real config fields afterward.

Copy field shapes, the `schema.json` consent / `connectionMode` blocks, and `sdkTemplate` content from the **example destination** (Form 2).

## Sources of truth — read before writing

- `scripts/template-db-config.json`, `scripts/template-ui-config.json` — the canonical starting templates. **Copy these as your base**; they already carry `version: "1.0"`, the standard structure, and the consent block.
- `src/schemas/destinations/db-config-schema.json` — authoritative meta-schema for `db-config.json`. `config.additionalProperties` is `false`; an unknown key fails validation.

- [`CONVENTIONS.md`](../../../CONVENTIONS.md) — naming and structural conventions that apply across the repo (`accountDefinitionName`, string `pattern`s, event-filtering fields, `deduplicationKey`, event mapping, mode-conditional validation). **Where an existing destination and CONVENTIONS.md disagree, CONVENTIONS.md is current** — most files predate it.

The templates do **not** produce `schema.json` — author it by hand (step 3).

## File layout

```
src/configurations/destinations/<dir>/
├── db-config.json
├── ui-config.json
└── schema.json
test/data/validation/destinations/<dir>.json   ← validation test cases
```

## Confirm before writing

Before creating any files:

1. **Guard** — abort if `src/configurations/destinations/<dir>/` already exists, and check the `displayName` isn't already taken (`npm run validate:displayname`).
2. **Summary & confirm** — show the derived `dir`, `name`, `displayName` and every form answer (source types, category, connection modes, message types). Ask the user to confirm or correct — especially brand casing in `name`/`displayName` (e.g. `GA4`, `ActiveCampaign`) that the derivation may get wrong. Don't write until confirmed.

## Steps

### 1. `db-config.json` — from `scripts/template-db-config.json`

Copy the template, then:

- Set `name` = `<DEFINITION_NAME>`, `displayName` = `<Display Name>`. Keep `version` = `"1.0"`.
- `transformAtV1` depends on category (Form 2). The template default is `router`, which is right for
  everything except warehouse:
  - **Non-warehouse** (cloud / device / hybrid) — keep `router`. Every destination added since 2025 is
    `router`, and a new cloud destination's transform lives in `routerTransform.ts` on the transformer's
    batching framework, which only runs on the router path. `processor` is a legacy setting — 121
    non-warehouse destinations carry it, none of them new. Don't pick it for a net-new destination.
  - **Warehouse** — change it to `processor`. All 11 `category: "warehouse"` destinations are `processor`
    with no exceptions, and it isn't a style choice: a warehouse destination's transformer entry point
    (`src/v0/destinations/<dir>/transform.js` in rudder-transformer) exports only `process()` and delegates
    to `processWarehouseMessage` — there is no `routerTransform` for the router path to call. Don't carry
    the template's `router` over it.
- `saveDestinationResponse` stays `true` (template default) — 222 of 247 destinations are `true`. It controls
  one thing: rudder-server blanks the destination's response body on **successful** deliveries when it is
  `false` (`router/worker.go`, `prepareRouterJobResponses`); failure bodies are always kept either way. So
  `true` costs a stored body per delivered event and buys being able to debug a "we got a 200 but the data
  never landed" report. Set it to `false` only when the success response is worthless or unbounded — a
  tracking pixel (`ga`, `gtm`, `firebase`, `pinterest_tag` are all `false` for this reason; the flag was
  introduced in 2021 precisely because GA's GIF response broke the DB write), or an arbitrary customer
  endpoint (`webhook`).
- If category (Form 2) = `warehouse`: add top-level `"category": "warehouse"` (sibling of `name`), set `transformAtV1` to `processor` (above), and follow [Warehouse destinations](#warehouse-destinations).
- `options.icon` — set it to the destination's kebab-case icon name from the RudderStack Integration Icons Figma library (published as `@rudderlabs/icons`). The template's `options` carries only `isBeta`, so this is easy to miss — and every definition but `test_destination` has one. The icon must already exist upstream: rudder-icons' check fails on a definition with no `options.icon` and on one naming a missing icon. If it doesn't exist yet, say so and get the artwork added — don't borrow a neighbouring brand's icon or invent a name.
- `supportedSourceTypes` ← Form 1.
- `destConfig.defaultConfig` = `["placeholderKey"]` — a neutral placeholder field (also added to ui-config and schema, below) so the scaffold validates (`defaultConfig` can't be empty per the meta-schema). Replace it with the real config keys as fields are added.
- For **each** source type in `supportedSourceTypes`, add a `destConfig.<sourceType>` array containing at least `["connectionMode", "consentManagement"]`.
- Client-side event filtering keys (`eventFilteringOption`, `whitelistedEvents`, `blacklistedEvents`) belong in `destConfig.defaultConfig`, never in a source-type array — see [client-side event filtering keys](../../../CONVENTIONS.md#client-side-event-filtering-keys); the validator rejects the source-scoped placement.
- `secretKeys` — secret config keys (mirrors `secret: true` in ui-config); the scaffold leaves this `[]`.
- Never define `oneTrustCookieCategories` / `ketchConsentPurposes` anywhere (db-config, schema, ui-config) — they are deprecated and only carried by pre-existing destinations.

Then fill the rest from the form answers:

- `supportedConnectionModes` ← Form 3/4; `supportedMessageTypes` ← Form 5.
- `includeKeys` / `excludeKeys`: if **any** source type has `device` or `hybrid`, define `includeKeys` (must include `consentManagement` and `connectionMode`); if every source type is cloud-only, **delete both**.
- `hybridModeCloudEventsFilter`: required if any source type includes `hybrid`.
- `sdkTemplate` (ui-config): **always present** — `fields` populated for `device`/`hybrid`, `[]` for cloud-only. See step 2.

> A present-but-empty `includeKeys: []` is read as device mode and fails the consent-integrity test — for an all-cloud destination, delete it (don't leave the template's empty array).
>
> `sdkTemplate` is the opposite case, and the two are easy to conflate: `includeKeys` must be **deleted** when empty, `sdkTemplate` must be **kept** when empty.

Strictly-cloud skeleton (all source types in cloud mode):

```json
{
  "name": "ACME_CRM",
  "displayName": "Acme CRM",
  "version": "1.0",
  "config": {
    "transformAtV1": "router",
    "saveDestinationResponse": true,
    "supportedSourceTypes": ["android", "ios", "web", "cloud", "warehouse", "..."],
    "supportedMessageTypes": { "cloud": ["identify", "track", "page", "screen", "group", "alias"] },
    "supportedConnectionModes": {
      "android": ["cloud"],
      "web": ["cloud"],
      "cloud": ["cloud"],
      "...": ["cloud"]
    },
    "destConfig": {
      "defaultConfig": ["placeholderKey"],
      "android": ["connectionMode", "consentManagement"],
      "web": ["connectionMode", "consentManagement"],
      "cloud": ["connectionMode", "consentManagement"],
      "...": ["connectionMode", "consentManagement"]
    },
    "secretKeys": []
  },
  "options": { "isBeta": true, "icon": "acme-crm" }
}
```

### 2. `ui-config.json` — from `scripts/template-ui-config.json`

Copy the template as-is — it already includes the standard consent block. Add the single `placeholderKey` field to the "Configure settings" group (page 2) so ui-config, schema, and `destConfig` stay in sync:

```json
{
  "type": "textInput",
  "label": "Placeholder",
  "configKey": "placeholderKey",
  "regex": "^(.{0,100})$",
  "regexErrorMessage": "Invalid value",
  "placeholder": "replace this placeholder field",
  "required": false
}
```

When real fields are introduced, replace it — add each to the "Connection settings" group (page 1) if required, else "Configure settings" (page 2), using the same shape. `type` ∈ `textInput | checkbox | singleSelect | multiSelect | tagInput`; omit `required` to make a field required, set `"required": false` for optional, and mark secrets with `"secret": true`.

A destination whose whole configuration is a linked account and two connection fields ends up with very little on page 2. Two opposite mistakes follow:

- **Don't add sections the template doesn't ship.** Its `baseTemplate` is exactly two blocks — "Initial setup" (groups "Connection settings" and "Connection mode") and "Configuration settings" (section "Destination settings" → group "Configure settings"). An extra section carrying an empty `groups` array renders as a heading with nothing under it. Add one when you have fields for it, not in anticipation. The one section you **must** add when it has a field: an `immutable` field goes in a third "Initial setup" section, `baseTemplate[0].sections[2].groups[0]` — the create wizard renders immutable fields from nowhere else, so placed in any other group the field is skipped on create and locked read-only on edit, and the customer can never set it.
- **Don't delete the consent surface to tidy up.** An empty "Configuration settings" block is the normal shape for an account-backed cloud-only destination. `consentSettingsTemplate`, the schema `consentManagement` property, and a `destConfig.<sourceType>` entry per supported source type stay regardless — test-enforced, and it throws rather than failing cleanly: [CONVENTIONS.md](../../../CONVENTIONS.md#where-a-field-goes-in-destconfig-defaultconfig-vs-a-source-type).

**Event mapping is not one of these fields.** If the destination maps RudderStack event names onto the partner's own event vocabulary, it goes in its own top-level block holding a single `redirect`, with the mapping declared under `redirectGroups` as `type: "mapping"` — not as a `dynamicCustomForm` in the settings groups above. Copy the shape from [CONVENTIONS.md](../../../CONVENTIONS.md#event-name-mapping).

> The trap is that the wrong answer looks like it works. The base-template field switch has a `dynamicCustomForm` case and no `mapping` case, so an inline `dynamicCustomForm` renders while an inline `mapping` renders **nothing**. Reaching for `dynamicCustomForm` because "the other one didn't show up" is how `openai_ads` shipped the only inline event mapping in the tree. Keep `dynamicCustomForm` for genuinely nested row config such as `consentManagement`.

- **`sdkTemplate`** — device/hybrid: populate `fields` with the web SDK settings from the example destination; cloud-only: leave the object exactly as the template ships it. **Never delete it.** Doing so ships a destination that connects fine and then crashes its own Configuration page, and nothing here catches it: [CONVENTIONS.md](../../../CONVENTIONS.md#sdktemplate-is-required-even-on-a-cloud-only-destination).
- Keep `regex` **plain**, exactly as in the placeholder field above, and give **every** string field one — `scripts/template-ui-config.json` ships no fields, so there is nothing to copy. Omitting `regex` never gives you a permissive pattern: on `textInput` / `textareaInput` it generates no `pattern` at all, so the value goes unvalidated on save, and on `dynamicForm` / `dynamicCustomForm` / `tagInput` it generates the deprecated prefix. Don't carry that prefix over from an existing destination either. Both rules and the reasoning: [CONVENTIONS.md](../../../CONVENTIONS.md#string-pattern-and-regex).
- An **optional** field's `regex` must match `""`, or the customer can fill it but never clear it — the `^(.{0,100})$` form above allows it, a constrained shape needs an explicit empty branch. [CONVENTIONS.md](../../../CONVENTIONS.md#optional-fields-must-accept-the-empty-string) covers `dynamicForm` rows and `singleSelect`.
- Do not add any `oneTrustCookieCategories` / `ketchConsentPurposes` fields.

### 3. `schema.json` (author by hand — no template)

A `configSchema` (JSON Schema draft-07) whose `required`/`properties` mirror the ui-config fields. The scaffold has `required: []` and, in `properties`, the `placeholderKey` field plus the copied consent/`connectionMode` blocks; replace `placeholderKey` (and add `required` entries) as real fields are introduced:

```json
{
  "configSchema": {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": [],
    "properties": {
      "placeholderKey": {
        "type": "string",
        "pattern": "^(.{0,100})$"
      }
    },
    "additionalProperties": true
  }
}
```

- Use a **plain** string `pattern` — just the field's own regex, copied verbatim from that field's ui-config `regex` so the two files agree: `"^.{1,100}$"` for a required field, `"^(.{0,100})$"` as in the block above for an optional one. **Do not prefix it with the deprecated `(^\\{\\{.*\\|\\|(.*)\\}\\}$)|(^env[.].+)|`,** which nearly every existing schema carries, and don't add lookaheads restating what the expression already rejects. Keep length bounds inside the expression too — a sibling `maxLength` is drift the generator neither emits nor preserves ([CONVENTIONS.md](../../../CONVENTIONS.md#keep-the-expression-to-what-the-value-is)). Which schemas are clean to copy from: [CONVENTIONS.md](../../../CONVENTIONS.md#string-pattern-and-regex).
- Copy the `consentManagement` and `connectionMode` property blocks from the example destination. The `consentManagement.properties` keys must **exactly equal** `supportedSourceTypes`; each is an array with `uniqueItemProperties: ["provider"]` and the standard `errorMessage`. Replicate the per-source-type pattern for any source type the example lacks (e.g. `cloudSource`).
- Do **not** add `oneTrustCookieCategories` / `ketchConsentPurposes` properties.
- **A value valid in one connection mode but not another** (e.g. the partner's browser SDK supports fewer events than its server API) goes in `schema.json` as an `allOf` / `if` / `then` block keyed on `connectionMode.<sourceType>`, with `ajv-errors` `errorMessage`s on **both** the `then` and the `if` so the customer sees a readable reason and no raw schema failure. Don't add a second mode-specific config field for it, and don't push the rule into the transformer or the SDK. Full shape: [CONVENTIONS.md](../../../CONVENTIONS.md#restricting-a-field-by-connection-mode).
- **A customer-chosen dedupe/event-id field** is named `deduplicationKey` — see [CONVENTIONS.md](../../../CONVENTIONS.md#deduplication--event-id-config-key-deduplicationkey).
- **An event mapping's property is hand-written.** `scripts/schemaGenerator.py` never walks `redirectGroups`, so the mapping you declared in step 2 generates no schema at all — author the array property yourself and keep it in step with the columns. Nothing warns you if the two drift, and `update:schema:destination:force` deletes the block outright. [CONVENTIONS.md](../../../CONVENTIONS.md#the-schema-entry-is-hand-maintained).
- **If regenerating drops a constraint the UI enforces, fix the generator — don't accept the weaker schema.** When a field's ui-config `regex` produces no schema `pattern` (a field type whose generator branch ignores `regex`), the value goes unvalidated on any API save. Don't loosen the fixtures to match and don't hand-patch `schema.json` past the drift check: fix the generator branch in `scripts/schemaGenerator.py`, add generator test coverage, and regenerate. That is the opposite of editing `scripts/` to get a destination _past_ a check — it makes the check stricter for every destination of that field type.

### Warehouse destinations

`category: "warehouse"` definitions don't follow the steps above field by field, and none of the existing ones is a clean copy source:

- **Structure: copy from `microsoft_fabric`.** It is the only warehouse on Form Builder V2 (`baseTemplate`), which is what `scripts/template-ui-config.json` produces. The other warehouses (`postgres`, `bq`, `snowflake`, …) are legacy array-shaped ui-configs, and `postgres`/`bq` are in the schema generator's `EXCLUDED_DEST`, so their `schema.json` is hand-maintained — don't copy either property onto a new destination. Translate their fields with the `migrate-destination-to-form-builder-v2` skill's field-mapping reference.
- **Settings: take the shared warehouse settings (sync schedule, object-storage options, …) from `postgres`/`bq`, not their whole `defaultConfig`.** Leave out the legacy `underscoreDivideNumbers` and `allowUsersContextTraits` keys — they exist only for backward compatibility on existing warehouses and a new definition must not accept them. Equally, don't copy a connection field just because another warehouse exposes it: a value the provider fixes (a port, a host suffix) is a constraint in `regex`/`pattern`, or not a customer setting at all.
- **Sync frequency:** the 5-, 10- and 15-minute options each carry `"featureFlag": "AMP_enable-high-granularity-wh-syncs"` on the option itself. The v2 `singleSelect` filters options on it; don't drop it, and don't move it to `preRequisites.featureFlags` (that hides the whole selector).
- **`namespace` and any other `immutable` field** goes in `baseTemplate[0].sections[2].groups[0]` — see step 2.
- **Tests:** add the destination to the shared `warehouseDestinationNames` list in `test/validation.test.ts` (that is the parameterised warehouse coverage) and put everything destination-specific in its fixture file (step 4).

### 4. Test data — `test/data/validation/destinations/<dir>.json`

A JSON array of cases run against `schema.json`. The placeholder scaffold (no required fields) just needs `[{ "config": {}, "result": true }]`. As real fields are added, cover a valid config, a missing-required case, and an invalid-pattern case. `err` strings must match AJV output **exactly**. Every destination-specific case goes in this file. Don't add the destination's own `describe` / `it` blocks to `test/validation.test.ts`, which is the generic harness that runs these fixtures — this holds even when a review bot asks for "UI assertions" on the destination's ui-config. Registering the destination in an existing shared, parameterised list there (e.g. `warehouseDestinationNames`) is fine.

```json
[
  { "config": { "<configKey>": "<valid value>" }, "result": true },
  { "config": {}, "result": false, "err": [" must have required property '<configKey>'"] }
]
```

### 5. Format & validate

```bash
npx prettier --write "src/configurations/destinations/<dir>/*.json" "test/data/validation/destinations/<dir>.json"
npx jest test/validation.test.ts
```

Prettier matches repo style (lint-staged runs it on commit). Jest runs the definition check (your `db-config.json` against the meta-schema) and every case in your test-data file — it should be **green** for the placeholder scaffold. The `-d <dir>` flag does **not** filter under jest — the whole suite runs (~10s); that's expected. Fix any failures before finishing.

## Checklist before done

- [ ] Directory = lowercased display name; `name` = uppercased; `displayName` verbatim (brand casing confirmed); `version` = `"1.0"`.
- [ ] `transformAtV1` matches the category — `router` for non-warehouse (template default), `processor` for `category: "warehouse"`; `saveDestinationResponse` is `true` (template default). Departing from either needs a stated reason.
- [ ] `placeholderKey` present in `destConfig.defaultConfig`, ui-config `fields`, and schema `properties` (until real fields replace it).
- [ ] Every connection field appears in: ui-config `fields`, schema `properties`, and `destConfig.defaultConfig`.
- [ ] Event-filtering keys, if present, are in `destConfig.defaultConfig` and not in any `destConfig.<sourceType>` array.
- [ ] Every secret field is in `secretKeys` **and** has `secret: true` in ui-config.
- [ ] Mode wired consistently across `supportedConnectionModes`, `supportedMessageTypes`, `includeKeys`, `sdkTemplate` (cloud-only: `includeKeys`/`excludeKeys` deleted).
- [ ] `uiConfig.sdkTemplate` is **present** (never deleted), with `fields: []` if cloud-only.
- [ ] `consentSettingsTemplate`, the schema `consentManagement` property, and a `destConfig.<sourceType>` entry containing `consentManagement` exist for **every** `supportedSourceTypes` entry; no `baseTemplate` section was added beyond the template's two blocks, other than the Initial setup immutable-fields section when the destination has an immutable field.
- [ ] Every string field has an explicit `regex`; no `regex`/`pattern` carries the deprecated prefix or a redundant lookahead.
- [ ] No `pattern` has a sibling `maxLength`/`minLength` — the length bound lives in the expression.
- [ ] Any event mapping is a `type: "mapping"` under `redirectGroups`, reached from its own `hideEditIcon: true` block holding only a `redirect` — no `dynamicCustomForm` mapping in the settings groups, and its `schema.json` property is written by hand.
- [ ] Every `"required": false` field matches `""` — in both the ui-config `regex` and the schema `pattern`.
- [ ] `supportedSourceTypes` claims only what this destination genuinely accepts — `warehouse` only if it is rETL-capable.
- [ ] `options.icon` names an icon that exists in `@rudderlabs/icons` — not borrowed from another brand, not invented.
- [ ] Every `immutable` field sits in `baseTemplate[0].sections[2].groups[0]`.
- [ ] Warehouse only: Form Builder V2 structure (not a copied legacy ui-config); no `underscoreDivideNumbers` / `allowUsersContextTraits`; the 5/10/15-minute sync options keep their per-option `featureFlag`; listed in `warehouseDestinationNames`.
- [ ] No file under `scripts/` was modified to get this destination _past_ a check. A generator fix that restores a dropped constraint is the exception, and ships with generator tests.
- [ ] No `oneTrustCookieCategories` / `ketchConsentPurposes` anywhere.
- [ ] `npx jest test/validation.test.ts` is green.

## Next steps

The scaffold is a starting point, not a finished destination. Then:

1. Add the destination's real config fields — to ui-config `fields`, schema `properties`, and `destConfig.defaultConfig` (replacing `placeholderKey`); mark secrets in `secretKeys` + `secret: true`.
2. Flesh out the test-data cases for those fields and re-run `npx jest test/validation.test.ts`.
3. Open a **draft** PR with a Conventional Commit (e.g. `feat(<dir>): add <Display Name> destination definition`).
