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
- **Account-framework auth** → `migrate-to-accounts-framework`

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

- `warehouse` → set top-level `"category": "warehouse"`; every source type is `cloud` mode, so **skip Forms 3–4**. Example: `postgres`/`bq` — copy wholesale (distinct shape, excluded from schema generation).
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
    to `processWarehouseMessage` — there is no `routerTransform` for the router path to call. Copying
    `postgres`/`bq` per the warehouse step below gives you this; just don't carry the template's `router`
    over it.
- `saveDestinationResponse` stays `true` (template default) — 222 of 247 destinations are `true`. It controls
  one thing: rudder-server blanks the destination's response body on **successful** deliveries when it is
  `false` (`router/worker.go`, `prepareRouterJobResponses`); failure bodies are always kept either way. So
  `true` costs a stored body per delivered event and buys being able to debug a "we got a 200 but the data
  never landed" report. Set it to `false` only when the success response is worthless or unbounded — a
  tracking pixel (`ga`, `gtm`, `firebase`, `pinterest_tag` are all `false` for this reason; the flag was
  introduced in 2021 precisely because GA's GIF response broke the DB write), or an arbitrary customer
  endpoint (`webhook`).
- If category (Form 2) = `warehouse`: add top-level `"category": "warehouse"` (sibling of `name`), set `transformAtV1` to `processor` (above), and copy `postgres`/`bq` wholesale.
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
- `sdkTemplate` (ui-config): **always present.** Populate `fields` for `device`/`hybrid`; for cloud-only keep the object with `fields: []` — see step 2.

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
  "options": { "isBeta": true }
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

#### Don't invent sections — and don't strip the consent surface to tidy up

A destination whose whole configuration is a linked account and two connection fields ends up with
very little on page 2. Two opposite mistakes follow, and the second is much more expensive:

- **Don't add sections the template doesn't ship.** The template's `baseTemplate` is exactly two
  blocks — "Initial setup" (groups "Connection settings" and "Connection mode") and "Configuration
  settings" (section "Destination settings" → group "Configure settings"). An extra "Other settings"
  or similar, carrying an empty `groups` array, renders as a heading with nothing under it. Add a
  section when you have fields for it, not in anticipation.
- **Don't delete the consent surface.** `consentSettingsTemplate` in the ui-config, the
  `consentManagement` property in `schema.json`, and a `destConfig.<sourceType>` entry containing
  `consentManagement` for **every** supported source type are required of an ordinary destination
  even when it has no product settings at all. This is test-enforced, not stylistic:
  `test/consentManagementFieldsIntegrity.test.ts` asserts that the `destConfig` source-type keys
  **exactly equal** `supportedSourceTypes` (`:116-118`) and that each one includes
  `consentManagement` (`:101-108`). Drop a source type's entry and the test doesn't just fail, it
  throws on `undefined.includes` — which reads like a broken test rather than a missing key.

The two settle a question that looks the same from the outside. "This section has no fields" is a
reason to remove a section **you added**; it is never a reason to remove the standard consent
blocks, and an empty "Configuration settings" block is the normal shape for an account-backed
cloud-only destination rather than something to clean up.

**Event mapping is not one of these fields.** If the destination maps RudderStack event names onto the partner's own event vocabulary, it goes in its own top-level block holding a single `redirect`, with the mapping declared under `redirectGroups` as `type: "mapping"` — not as a `dynamicCustomForm` in the settings groups above. Copy the shape from [CONVENTIONS.md](../../../CONVENTIONS.md#event-name-mapping).

> The trap is that the wrong answer looks like it works. The base-template field switch has a `dynamicCustomForm` case and no `mapping` case, so an inline `dynamicCustomForm` renders while an inline `mapping` renders **nothing**. Reaching for `dynamicCustomForm` because "the other one didn't show up" is how `openai_ads` shipped the only inline event mapping in the tree. Keep `dynamicCustomForm` for genuinely nested row config such as `consentManagement`.

- **`sdkTemplate` — keep the object, whatever the connection mode.** Device/hybrid: populate `sdkTemplate.fields` with the web SDK settings from the example destination. Cloud-only: leave the object exactly as the template ships it, with `fields: []`. Deleting it is a shipped-destination outage — see below.
- Keep `regex` **plain**, exactly as in the placeholder field above, and give **every** string field one — `scripts/template-ui-config.json` ships no fields, so there is nothing to copy. Omitting `regex` never gives you a permissive pattern: on `textInput` / `textareaInput` it generates no `pattern` at all, so the value goes unvalidated on save, and on `dynamicForm` / `dynamicCustomForm` / `tagInput` it generates the deprecated prefix. Don't carry that prefix over from an existing destination either. Both rules and the reasoning: [CONVENTIONS.md](../../../CONVENTIONS.md#string-pattern-and-regex).
- An **optional** field's `regex` must match `""`, or the customer can fill it but never clear it — the `^(.{0,100})$` form above allows it, a constrained shape needs an explicit empty branch. [CONVENTIONS.md](../../../CONVENTIONS.md#optional-fields-must-accept-the-empty-string) covers `dynamicForm` rows and `singleSelect`.
- Do not add any `oneTrustCookieCategories` / `ketchConsentPurposes` fields.

#### Never delete `sdkTemplate` because the destination is cloud-only

It reads like dead weight on a cloud-only destination — no device-mode fields to put in it, and the
`note` the template ships literally says "not visible in the ui". Deleting it produces a destination
that **is created and connected without complaint and then crashes its own Configuration page** the
first time anyone reopens it.

In rudder-webapp, `configurationV2/formComponents/types.ts` declares `sdkTemplate` as a **required**
member of `DestUIConfigV2` — note that `consentSettingsTemplate?` right beside it is optional, so
this is a deliberate contract, not an oversight. `configurationV2/formComponents/util.ts` destructures
it and passes it straight into `getConfigTemplateFields` and
`getFormGroupsFromSdkTemplateSubGroups`, which dereferences `sdkTemplate.groups` with no guard. The
create/connect path is the one that optional-chains it (`workflows/steps/destinationSettings/util.ts`
uses `sdkTemplate?.fields`), which is exactly why the failure shows up after creation rather than
during it.

Nothing in this repo catches it — `npx jest test/validation.test.ts` stays green, because
`sdkTemplate` is not what the destination meta-schema validates. All 84 form-builder-v2 destinations
carry the object, 70 of them with `fields: []`, so there is no precedent to copy in the other
direction. To confirm (a plain `grep -L` is no good here — it would also list every legacy non-v2
ui-config, which has no `sdkTemplate` by design):

```bash
python3 -c "
import json, glob
bad = [f for f in glob.glob('src/configurations/destinations/*/ui-config.json')
       if 'baseTemplate' in json.load(open(f))['uiConfig']
       and 'sdkTemplate' not in json.load(open(f))['uiConfig']]
print(bad or 'all form-builder-v2 destinations carry sdkTemplate')"
```

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

### 4. Test data — `test/data/validation/destinations/<dir>.json`

A JSON array of cases run against `schema.json`. The placeholder scaffold (no required fields) just needs `[{ "config": {}, "result": true }]`. As real fields are added, cover a valid config, a missing-required case, and an invalid-pattern case. `err` strings must match AJV output **exactly**.

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
- [ ] `uiConfig.sdkTemplate` is **present** — with `fields: []` if cloud-only. Deleting it ships a destination that crashes its own Configuration page after create, and no test here catches it.
- [ ] `consentSettingsTemplate`, the schema `consentManagement` property, and a `destConfig.<sourceType>` entry containing `consentManagement` exist for **every** `supportedSourceTypes` entry; no `baseTemplate` section was added beyond the template's two blocks.
- [ ] Every string field has an explicit `regex`; no `regex`/`pattern` carries the deprecated prefix or a redundant lookahead.
- [ ] No `pattern` has a sibling `maxLength`/`minLength` — the length bound lives in the expression.
- [ ] Any event mapping is a `type: "mapping"` under `redirectGroups`, reached from its own `hideEditIcon: true` block holding only a `redirect` — no `dynamicCustomForm` mapping in the settings groups, and its `schema.json` property is written by hand.
- [ ] Every `"required": false` field matches `""` — in both the ui-config `regex` and the schema `pattern`.
- [ ] `supportedSourceTypes` claims only what this destination genuinely accepts — `warehouse` only if it is rETL-capable.
- [ ] No file under `scripts/` was modified to get this destination through a check.
- [ ] No `oneTrustCookieCategories` / `ketchConsentPurposes` anywhere.
- [ ] `npx jest test/validation.test.ts` is green.

## Next steps

The scaffold is a starting point, not a finished destination. Then:

1. Add the destination's real config fields — to ui-config `fields`, schema `properties`, and `destConfig.defaultConfig` (replacing `placeholderKey`); mark secrets in `secretKeys` + `secret: true`.
2. Flesh out the test-data cases for those fields and re-run `npx jest test/validation.test.ts`.
3. Open a **draft** PR with a Conventional Commit (e.g. `feat(<dir>): add <Display Name> destination definition`).
