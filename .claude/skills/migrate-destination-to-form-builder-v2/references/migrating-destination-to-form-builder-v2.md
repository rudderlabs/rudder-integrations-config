# Migrating a destination from the old form builder to form builder v2

A step-by-step runbook for converting a destination's `ui-config.json` from the
legacy array format to the v2 template format.

> **Scope.** This covers the whole migration, not just the JSON rewrite:
> `ui-config.json`, the `db-config.json` keys the v2 renderer depends on,
> `schema.json` regeneration, and how to verify the result in the webapp.

**Background reading (do this first):**

- [New Form Builder Framework](https://app.notion.com/p/rudderstacks/New-Form-Builder-Framework-a9aa1dd580b84ebabf56e693868efbe6) — terminology and structure.
- The webapp's form-component type definitions are the ultimate authority on field shapes. They live in the webapp repo; the tables in §3 and §4 below mirror them. Where a shipped `ui-config.json` and these tables disagree, prefer the shipped configs — and ask the webapp team if a field type is not covered here.

**Canonical reference configs:**

| Destination                                                                                                                                               | Read it for                                                                          |
| --------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| [`am`](https://github.com/rudderlabs/rudder-integrations-config/blob/develop/src/configurations/destinations/am/ui-config.json) (Amplitude)               | `sdkTemplate`, `sdkTemplate.groups`, device-mode gating, client-side event filtering |
| [`adobe_analytics`](https://github.com/rudderlabs/rudder-integrations-config/blob/develop/src/configurations/destinations/adobe_analytics/ui-config.json) | `redirect` fields and `redirectGroups` with `tabs`                                   |
| [`scripts/template-ui-config.json`](../../../../scripts/template-ui-config.json)                                                                          | The minimal valid v2 skeleton                                                        |

---

## 0. Understand what you are shipping

**v2 is switched on solely by `uiConfig` no longer being a JSON array.** The
webapp picks the renderer on that one test: an array gets the legacy form, an
object gets v2. You can see the split in this repo — 167 destinations still ship
an array, 80 ship an object.

There is **no feature flag and no gradual rollout**. The moment your config
reaches production, every workspace using that destination sees the new form —
in the create flow, the edit flow, and the RETL connect flow. Treat the PR
accordingly: get a design/PM sign-off on labels and grouping, not just a code
review.

Migration is also effectively one-way in practice: rolling back means reverting
the whole config.

---

## 1. Inventory the old config

Before writing any JSON, build a worksheet from the existing
`src/configurations/destinations/<dest>/ui-config.json`. One row per field:

| Column            | Where it comes from                                                    | Why you need it                                 |
| ----------------- | ---------------------------------------------------------------------- | ----------------------------------------------- |
| `configKey`       | old `value`                                                            | becomes `configKey` in v2                       |
| Label             | old `label`                                                            | v2 requires a `label` on every input field      |
| Type              | old `type`                                                             | see the type table in step 4                    |
| Required?         | old `required`                                                         | decides whether it belongs in **Initial setup** |
| Device-mode only? | is the key listed under `destConfig.<sourceType>` in `db-config.json`? | decides `baseTemplate` vs `sdkTemplate`         |
| Secret?           | old `secret`                                                           | carries over                                    |
| Conditional?      | old `preRequisiteField` / `preRequisites` / `featureFlag`              | see step 4                                      |

Cross-check the "device-mode only?" column against `db-config.json` rather than
guessing from the old section titles — the old builder's section names
("Native SDK", "Client-side Events Filtering") are not reliable indicators.

---

## 2. Lay the skeleton — the structural contract

This is the step most migrations get wrong. The v2 renderer addresses parts of
`baseTemplate` **positionally and by exact title string**. Get these wrong and
the form renders with no error — the affected section is simply missing.

Start from [`scripts/template-ui-config.json`](../../../../scripts/template-ui-config.json) and honour all of the following:

| Contract                                                                                                            | What breaks if you ignore it                             |
| ------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| `baseTemplate[0]` is the **Initial setup** collapsible — the create flow renders only this one                      | Fields you expect during creation never appear           |
| The first collapsible is titled **exactly** `Initial setup`                                                         | Fields in it never enter `schema.required` (see step 2a) |
| `baseTemplate[0].sections[0].groups[*]` = connection settings, i.e. the mandatory fields                            | —                                                        |
| `baseTemplate[0].sections[1].groups[0]` = **connection mode slot**. Leave `fields: []`; the framework overwrites it | Connection mode picker never renders                     |
| `baseTemplate[0].sections[2].groups[0]` = immutable-fields group (optional)                                         | Immutable info panel missing in create flow              |
| A collapsible titled **exactly** `Configuration settings`                                                           | `sdkTemplate` and consent fields are never injected      |
| Inside it, a section titled **exactly** `Destination settings`                                                      | `sdkTemplate` groups are never injected                  |
| For consent, a section with `"id": "consentSettings"`                                                               | Consent groups are never injected                        |
| Group titled **exactly** `Connection mode`                                                                          | The explanatory connection-mode info block is not shown  |

Every one of these holds in all 80 migrated destination configs. If a config you are copying from disagrees with this table, the config is wrong — check it against a recently migrated destination rather than an old one.

Beyond those fixed slots you are free: any number of collapsible sections after
the first, any number of sections and groups within them.

**The Initial setup rule.** `baseTemplate[0]` must contain _all and only_ the
fields a user genuinely must fill to create the destination. Everything else
belongs in a later collapsible section. This is the entire point of v2 — if you
copy the old form's full field list into Initial setup, you have not migrated
anything.

This is **not** a style rule. Placement in Initial setup silently changes
validation — see the next section, which is the single most dangerous part of
this migration.

### 2a. Initial setup placement writes `schema.required`

In v2 a field enters the schema's top-level `required` array by **placement**,
not because anyone marked it `required`. `schemaGenerator.py:1376-1385`:

```python
if (
    template.get("title", "") == "Initial setup"
    and is_field_present_in_default_config(field, dbConfig, "configKey")
    and ("preRequisites" not in field or field.get("required"))
):
    schemaObject["required"].append(field["configKey"])
```

A field becomes schema-required when **all three** hold:

1. it sits in the collapsible titled exactly `Initial setup`
2. its `configKey` is in `db-config.json` → `destConfig.defaultConfig`
3. it has **no `preRequisites`** — or it has them _and_ `required: true`

`required: true` is neither necessary nor sufficient. The **old** format's rule
is the opposite (`schemaGenerator.py:1327-1331`): `required: true` AND in
`defaultConfig`, placement irrelevant. **So migration changes the meaning of
"required".** A field that was optional in the old form becomes schema-required
simply by being placed in Initial setup — and every destination saved without
that field then fails validation.

This has already shipped once:

|            |            |                                                                                      |
| ---------- | ---------- | ------------------------------------------------------------------------------------ |
| 2023-10-30 | `f6ff024f` | facebook_pixel migrated to v2 → `required` becomes `["pixelId", "accessToken"]`      |
| 2024-02-23 | `32e1d10d` | `fix: make accessToken required only for cloud mode (#1233)` → back to `["pixelId"]` |

`accessToken` carried no `required: true` and no `preRequisites`; placement
alone did it. The bug lived for ~4 months. `mp` #1733 did the same thing with
`dataResidency` and `identityMergeApi`.

**Before you finish, compute the expected `required` set yourself** by applying
the three conditions to your new `ui-config.json` + `db-config.json`, and
compare it to the old `schema.json`. Any field the migration adds is a breaking
change for saved destinations and needs an explicit decision, not a silent
commit.

**The escape hatch**, when a field belongs in Initial setup but must stay
optional for existing configs: give it `preRequisites` and do not set
`required`. That is exactly what #1233 did — gated `accessToken` on
`connectionModes.cloud` and moved the enforcement into a schema conditional.
See [Restricting a field by connection mode](../../../../CONVENTIONS.md#restricting-a-field-by-connection-mode).

Skeleton:

```json
{
  "uiConfig": {
    "baseTemplate": [
      {
        "title": "Initial setup",
        "note": "Review how this destination is set up",
        "sections": [
          {
            "groups": [
              { "title": "Connection settings", "note": "...", "icon": "settings", "fields": [] }
            ]
          },
          {
            "groups": [
              { "title": "Connection mode", "note": "...", "icon": "sliders", "fields": [] }
            ]
          }
        ]
      },
      {
        "title": "Configuration settings",
        "note": "Manage the settings for your destination",
        "sections": [
          {
            "title": "Destination settings",
            "note": "Configure advanced destination-specific settings here",
            "icon": "settings",
            "groups": [{ "title": "Configure settings", "note": "...", "fields": [] }]
          }
        ]
      }
    ],
    "sdkTemplate": { "title": "SDK settings", "note": "not visible in the ui", "fields": [] },
    "consentSettingsTemplate": {
      "title": "Consent settings",
      "note": "not visible in the ui",
      "fields": []
    },
    "redirectGroups": {}
  }
}
```

Keep the connection-mode section even for cloud-only destinations. The
framework populates it from `db-config.json`'s `supportedConnectionModes`; the
only case where it is skipped is warehouse-category destinations and RETL
connections.

**Valid `icon` values:** `settings`, `sliders`, `file`, `magnifyingGlass`,
`rightToLine`, `otherSettings`.
The webapp's published type for `icon` is stale and omits `otherSettings`, which
is in active use — trust the shipped configs.

---

## 3. Attribute renames

These apply to every field regardless of type:

| Old                                                    | New                                                                        | Notes                                                                                                                     |
| ------------------------------------------------------ | -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `value`                                                | `configKey`                                                                | The single most common rename                                                                                             |
| `label`                                                | `label`                                                                    | unchanged, but now **required** on input fields — write a real one                                                        |
| `footerNote`                                           | `note`                                                                     |                                                                                                                           |
| `sectionNote`                                          | `note` on the enclosing section/group                                      |                                                                                                                           |
| `labelNote`                                            | `note`                                                                     | Merge into `note`; if the field had both `labelNote` and `footerNote`, combine them into one crisp sentence               |
| `footerURL: { text, link }`                            | `note` as an array                                                         | `["Some text ", { "text": "link text", "link": "https://..." }]`                                                          |
| `options: [{ name, value }]`                           | `options: [{ label, value }]`                                              | `name` → `label`                                                                                                          |
| `defaultOption: { name, value }`                       | `default: "<value>"`                                                       | Just the value string                                                                                                     |
| `preRequisiteField: [{ name, selectedValue }]`         | `preRequisites: { fields: [{ configKey, value }] }`                        | Add `"condition": "or"` when any-of semantics are wanted; default is AND                                                  |
| `featureFlag: "AMP_..."`                               | `preRequisites: { featureFlags: [{ configKey: "AMP_...", value: true }] }` |                                                                                                                           |
| `immutable: true`                                      | _(no ui-config equivalent)_                                                | Move the key into `db-config.json` → `config.immutableKeys: [...]`; v2 reads `destinationDefinition.config.immutableKeys` |
| `required`                                             | `required`                                                                 | unchanged                                                                                                                 |
| `secret`                                               | `secret`                                                                   | unchanged (`textInput` only)                                                                                              |
| `regex`, `regexErrorMessage`, `placeholder`, `default` | unchanged                                                                  |                                                                                                                           |

`preRequisites` is shared between both builders, so if the old config already uses
`preRequisites` rather than `preRequisiteField`, copy it across as-is.

---

## 4. Field type mapping

Counts are occurrences across the destinations still on the old format, so you
can gauge how often you'll hit each one.

### Direct equivalents

| Old type                 | Count | v2 type                               | Notes                                              |
| ------------------------ | ----- | ------------------------------------- | -------------------------------------------------- |
| `textInput`              | 956   | `textInput`                           |                                                    |
| `singleSelect`           | 472   | `singleSelect`                        | remap `options[].name` → `label`                   |
| `checkbox`               | 340   | `checkbox`                            | but see `useNativeSDK` below                       |
| `dynamicCustomForm`      | 512   | `dynamicCustomForm`                   | `customFields` → `rowFields`; add `addButtonLabel` |
| `timePicker`             | 11    | `timePicker`                          |                                                    |
| `timeRangePicker`        | 8     | `timeRangePicker`                     |                                                    |
| `accountManagementInput` | 9     | `accountManagementInput`              |                                                    |
| `textareaInput`          | 18    | `textInput` with `"isTextArea": true` |                                                    |

### Needs restructuring

| Old type                                         | Count | v2 target                         | What changes                                                                                     |
| ------------------------------------------------ | ----- | --------------------------------- | ------------------------------------------------------------------------------------------------ |
| `dynamicForm`                                    | 65    | `mapping` **behind a `redirect`** | See step 6                                                                                       |
| `dynamicSelectForm`                              | 27    | `mapping` **behind a `redirect`** | The two old types merged into one. The right-hand `options` list becomes a `singleSelect` column |
| `defaultCheckbox`                                | 38    | _(delete the field)_              | See below                                                                                        |
| `useNativeSDK` / `useNativeSDKToSend` checkboxes | —     | _(delete the field)_              | See below                                                                                        |

**`defaultCheckbox`** was the disabled "this is a device-mode only destination"
switch. There is no v2 field for it. Instead, ensure `db-config.json` →
`config.supportedConnectionModes` lists only `device` for the relevant source
types; the connection-mode component then renders the correct single option.
You can also pin the default via `defaultConnectionModes` on the connection-mode
group.

**`useNativeSDK` / `useNativeSDKToSend`** must never be migrated as checkboxes.
v2 derives them from the connection mode:

| Connection mode | `useNativeSDK` | `useNativeSDKToSend` |
| --------------- | -------------- | -------------------- |
| `cloud`         | `false`        | `false`              |
| `device`        | `true`         | `true`               |
| `hybrid`        | `true`         | `false`              |

The webapp writes these on save from the picked mode, for every key the
destination declares in `destConfig.<sourceType>`. It does the same in reverse
for legacy destinations, deriving `connectionMode` from a stored `useNativeSDK`
— which is what keeps both form builders writing an identical backend config.

### v2-only components (no old counterpart)

Reach for these when they fit better than a literal translation:

| v2 type                              | Use when                                                                                                                                                 |
| ------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tagInput`                           | A free-form list of short string values (consent IDs, event names). Very often the right replacement for a `dynamicCustomForm` with a single text column |
| `multiSelect`                        | Fixed option list, multiple choices                                                                                                                      |
| `dynamicMultiSelect`                 | Same, but options fetched from the destination API (`apiName`)                                                                                           |
| `dynamicDataSelect` / `nestedSelect` | Single select whose options come from the destination API; `apiDependencies` declares which other fields must be filled first                            |
| `autoComplete`                       | Type-ahead over API-provided options                                                                                                                     |
| `mappingRow`                         | A fixed pair of columns inside a `dynamicCustomForm` row                                                                                                 |
| `audienceDeliveryApiBuilder`         | Audience delivery destinations only; owns multiple top-level config keys                                                                                 |
| `customComponent`                    | Last resort; requires a matching component to exist in the webapp — coordinate with that team before using it                                            |

### No exact equivalent — substitute and flag

Use the substitution, and **call it out explicitly in the PR description** so
the reviewer can accept or reject the lost behaviour.

| Old                                              | Count                | Substitute                                | What you lose                                                                                                                               |
| ------------------------------------------------ | -------------------- | ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `textareaInputCopy`                              | 2 (`rs`, `postgres`) | `textInput` with `isTextArea: true`       | The copy-to-clipboard button. If the value is meant to be copied out (e.g. a generated key), raise it with the webapp team before migrating |
| `subType: "JSON"`                                | 3                    | `textInput` with `isTextArea: true`       | JSON-specific validation/formatting. Add a `regex` if the shape matters                                                                     |
| `readOnly: true`                                 | 2                    | `db-config.json` → `config.immutableKeys` | Field-level read-only outside the immutable mechanism                                                                                       |
| `hidden: true`                                   | 2                    | Omit the field entirely                   | The key stays in config but is no longer user-visible — confirm nothing reads it from the form                                              |
| `reverse: true`                                  | 2                    | Reorder `options` by hand                 |                                                                                                                                             |
| `inputFieldType`                                 | 4                    | Drop it                                   | Native input type hint                                                                                                                      |
| `dynamicSelect`, `customGoogleAds`, `datePicker` | 0 in current configs | —                                         | Legacy v1-only renderers. If you meet one, stop and ask the webapp team                                                                     |

---

## 5. Device-mode fields → `sdkTemplate`

All device-mode fields go in `sdkTemplate`, never in `baseTemplate`. The
framework injects them into the `Destination settings` section, once per
connected source type, gated behind `connectionMode` being `device` or `hybrid`.

**Which template a field belongs in is decided by source scoping, not by
`defaultConfig` membership.** `getConfigTemplateFields`
checks _both_ `destConfig[<sourceType>]` and `destConfig.defaultConfig` when
building sdkTemplate groups, so sdkTemplate accepts either. `baseTemplate` is
`cloneDeep`d and never source-scoped, so it can only carry flat keys:

| The `configKey` is listed in…             | Put the field in              | Why                                                                                           |
| ----------------------------------------- | ----------------------------- | --------------------------------------------------------------------------------------------- |
| `destConfig.<sourceType>` (source-scoped) | **`sdkTemplate` — mandatory** | In `baseTemplate` it never populates: `transformFromBEtoFE` writes it as `<sourceType>-<key>` |
| `destConfig.defaultConfig` (flat)         | either — judgement            | `baseTemplate` normally; `sdkTemplate` when it is device-mode-only behaviour                  |
| neither                                   | **nothing renders**           | Generator warns `defined in ui-config.json but not in db-config.json`                         |

Across the 80 v2 destinations this holds without exception: 430 baseTemplate
fields, every one of them flat, **zero** source-scoped. 64 sdkTemplate fields
are source-scoped and 14 are flat (`mp`'s browser-SDK settings), which is why
the rule is one-directional — "flat" does not imply `baseTemplate`.

**The trap:** a field placed in `sdkTemplate` renders **only if its `configKey`
is listed in `db-config.json`** under `config.destConfig.<sourceType>` or
`config.destConfig.defaultConfig`.

If the key is missing from `destConfig`, the field silently does not appear.
Check every `sdkTemplate` field against `db-config.json` before you conclude
something is broken in the JSON.

Source-specific fields are also rewritten to `<sourceType>-<configKey>` in the
form state, and read back from `config.<configKey>.<sourceType>`.
This is why `preRequisites` inside `sdkTemplate` are injected by the framework
rather than written by you.

**Sub-groups.** `sdkTemplate.groups[]` (`SdkTemplateSubGroup`) lets you split
SDK settings into titled sub-groups instead of one flat list. Each non-empty
sub-group becomes an indented group inside `Destination settings`; empty ones
are omitted per source type. See `am`'s `sdkTemplate`.

### Client-side event filtering

`eventFilteringOption` + `whitelistedEvents` / `blacklistedEvents` is the one
device-mode feature that stays in `baseTemplate`. All 26 migrated destinations
that have it use the same three fields:

| Old                                                                              | New                                                                     |
| -------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| `singleSelect` on `eventFilteringOption`                                         | `singleSelect` on `eventFilteringOption`                                |
| `dynamicCustomForm(whitelistedEvents)` with one `textInput(eventName)` row field | **`tagInput`**, `configKey: "whitelistedEvents"`, `tagKey: "eventName"` |
| `dynamicCustomForm(blacklistedEvents)` with one `textInput(eventName)` row field | **`tagInput`**, `configKey: "blacklistedEvents"`, `tagKey: "eventName"` |

The `dynamicCustomForm` → `tagInput` swap is lossless: `tagInput` stores
`[{ "eventName": "..." }]`, the identical JSON the old `dynamicCustomForm`
produced. **`tagKey` is what preserves that shape — it must equal the old row
field's `value`.** Get it wrong and existing saved filters stop loading.

Option labels were also restyled during migration: `Disable` / `Allowlist` /
`Denylist` became `Disabled` / `Filter via allowlist` / `Filter via denylist`,
and `defaultOption` became `"default": "disable"`.

**Why `baseTemplate` and not `sdkTemplate`.** 24 of 26 declare these three keys
in `db-config.json` → `destConfig.defaultConfig`, i.e. flat top-level config
keys. Putting them in `sdkTemplate` would source-scope them and rewrite the keys
to `web-whitelistedEvents`, changing the saved shape. So
device-mode visibility is done manually, with a group-level `preRequisites`.

Copy `am`'s block and adjust the source types — it goes in the `Configuration
settings` collapsible, in a section titled `Other settings` with
`"icon": "otherSettings"`:

```json
{
  "title": "Client-side event filtering",
  "note": "Decide what events are allowed (allowlisting) and blocked (denylisting)",
  "preRequisites": {
    "fields": [
      { "configKey": "connectionMode.web", "value": "device" },
      { "configKey": "connectionMode.android", "value": "device" },
      { "configKey": "connectionMode.ios", "value": "device" }
    ],
    "condition": "or"
  },
  "fields": [
    {
      "type": "singleSelect",
      "label": "Choose if you want to turn on events filtering:",
      "configKey": "eventFilteringOption",
      "note": "You must select either allowlist or denylist to enable events filtering",
      "options": [
        { "label": "Disabled", "value": "disable" },
        { "label": "Filter via allowlist", "value": "whitelistedEvents" },
        { "label": "Filter via denylist", "value": "blacklistedEvents" }
      ],
      "default": "disable"
    },
    {
      "type": "tagInput",
      "label": "Allowlisted events",
      "note": "Input separate events by pressing 'Enter'.\nInput the events you want to allowlist.",
      "configKey": "whitelistedEvents",
      "tagKey": "eventName",
      "placeholder": "e.g: Anonymous page visit",
      "default": [{ "eventName": "" }],
      "preRequisites": {
        "fields": [{ "configKey": "eventFilteringOption", "value": "whitelistedEvents" }]
      }
    },
    {
      "type": "tagInput",
      "label": "Denylisted events",
      "note": "Input separate events by pressing 'Enter'.\nInput the events you want to denylist.",
      "configKey": "blacklistedEvents",
      "tagKey": "eventName",
      "placeholder": "e.g: Anonymous page visit",
      "default": [{ "eventName": "" }],
      "preRequisites": {
        "fields": [{ "configKey": "eventFilteringOption", "value": "blacklistedEvents" }]
      }
    }
  ]
}
```

Checklist for the block:

- [ ] The three keys are in `db-config.json` → `destConfig.defaultConfig`, not under a source type.
- [ ] Group sits in `Configuration settings` → section `Other settings` (`icon: "otherSettings"`). 25 of 26 do this; `fullstory` is the lone exception, in `Destination settings`.
- [ ] Group-level `preRequisites` OR's `connectionMode.<sourceType>` = `"device"` across **exactly** the source types whose `supportedConnectionModes` include `device`.
- [ ] Each `tagInput` is gated on the matching `eventFilteringOption` value.
- [ ] `tagKey` is `eventName` on both lists.

**Do not copy the gating from an arbitrary migrated destination.** The fields are
uniform across all 26, but the gate is not — there are four idioms in the wild:

| Gate                                                  | Count | Verdict                                      |
| ----------------------------------------------------- | ----- | -------------------------------------------- |
| `connectionMode.<sourceType>` = `"device"`            | 9     | correct — use this                           |
| `connectionModes.webDevice` / `mobileDevice` = `true` | 8     | works, but a second idiom for the same thing |
| no gate at all                                        | 6     | filtering shows for cloud-only connections   |
| mixed, including `connectionModes.web` = `"device"`   | 3     | **dead clause**                              |

`connectionModes.web` is not a key the app ever writes — only
`connectionModes.cloud`, `connectionModes.webDevice` and
`connectionModes.mobileDevice` exist. So in `intercom`,
`rockerbox` and `spotifyPixel` the web arm of the gate can never match. The
clause is `"condition": "or"`, so it fails open via the mobile arms rather than
hiding wrongly, but it is dead config.

Two destinations, `iterable` and `openai_ads`, declare the three keys under
`destConfig.web` rather than `defaultConfig` while their ui-config uses flat
`configKey`s in `baseTemplate`. `transformFromBEtoFE` only copies `defaultConfig`
keys under their flat name — `web` keys arrive as `web-eventFilteringOption` — so
a saved value would not populate the field on edit. The
two files disagree with each other and with the other 24; confirm the intended
shape with the webapp team before copying either.

---

## 6. Event mapping → its own collapsible block + `redirect`

Event mapping is not a field you drop into an existing group. It is **its own
top-level collapsible block in `baseTemplate` that contains nothing but a
`redirect` field**; the mapping itself is defined separately under
`redirectGroups`.

All 23 v2 destinations that have event mapping use the same block. Copy it and
rename:

```json
{
  "title": "Event mapping",
  "note": "Map RudderStack to Facebook events",
  "hideEditIcon": true,
  "sections": [
    {
      "groups": [
        {
          "title": "RudderStack to Facebook event mappings",
          "fields": [
            {
              "type": "redirect",
              "redirectGroupKey": "customEventMapping",
              "label": "Event and property mappings",
              "note": "Map RudderStack events/properties to Facebook custom events/properties"
            }
          ]
        }
      ]
    }
  ]
}
```

### Rules for the block

| Rule                                                                                            | Adherence across shipped configs |
| ----------------------------------------------------------------------------------------------- | -------------------------------- |
| `"hideEditIcon": true` on the collapsible                                                       | 24/24 — **hard**                 |
| Exactly one section, untitled and iconless — just `{ "groups": [...] }`                         | 24/24 — **hard**                 |
| The group holds **only** `redirect` fields; never mix a redirect into a group with input fields | 24/24 — **hard**                 |
| Collapsible title is `Event mapping` (or `Mappings`)                                            | 18/24 — convention               |
| It is the last collapsible in `baseTemplate`                                                    | 19/24 — convention               |

`hideEditIcon` correlates perfectly in both directions: every occurrence of it in
the whole corpus is on one of these blocks, and every one of these blocks has it.
The block has no editable fields of its own, so the section-level edit pencil
would do nothing — editing happens on the redirect screen.

Group title follows one template throughout — `RudderStack to <Destination>
event mappings`, or `RudderStack <X> to <Destination> <Y> Mapping` for non-event
maps (contact properties, traits, topics).

A destination may have several such blocks (`emarsys`, `ortto`,
`optimizely_fullstack`, `adobe_analytics`) — one per logical mapping, each with
its own `redirectGroupKey`.

Optionally add a group `callout` when mappings override transformations:

```json
"callout": {
  "message": "Mappings take precedence over any transformations for the destination.",
  "type": "info"
}
```

### Why a redirect at all

A `mapping` field **cannot be placed directly in a base-template group.** The
base-template field switch has no
`mapping` case — it would render nothing. Confirmed empirically: across all 80
already-migrated destinations there is not a single `mapping` field outside
`redirectGroups`.

### Defining the `redirectGroups` entry

The `redirect` field points at a key in the top-level `redirectGroups` object:

```json
// in a baseTemplate group
{
  "type": "redirect",
  "redirectGroupKey": "customEventMapping",
  "label": "Event and property mappings",
  "note": "Map RudderStack events/properties to Adobe custom events/properties"
}
```

```json
// top-level, as a sibling of baseTemplate
"redirectGroups": {
  "customEventMapping": {
    "tabs": [
      {
        "name": "Custom events",
        "fields": [
          {
            "type": "mapping",
            "label": "Map your RudderStack events to Adobe custom events",
            "note": "...",
            "configKey": "rudderEventsToAdobeEvents",
            "default": [],
            "columns": [
              { "type": "textInput", "configKey": "from", "label": "RudderStack Event", "placeholder": "e.g: Product Searched" },
              { "type": "textInput", "configKey": "to",   "label": "Adobe Custom Event", "placeholder": "e.g: conv.add_to_cart" }
            ]
          }
        ]
      }
    ]
  }
}
```

A `redirectGroup` takes either `fields` (one screen) or `tabs` (several named
screens).

**Keep a mapping's companion fields on the same screen or tab as the mapping.**
A field that changes how a mapping is read belongs next to it, not back in
`Configuration settings`. 10 of the 48 shipped redirect screens do this, and in
every case the companion parameterises that specific mapping:

| Destination                              | Tab                             | Companion fields                     |
| ---------------------------------------- | ------------------------------- | ------------------------------------ |
| `adobe_analytics`                        | Context data                    | `contextDataPrefix`                  |
| `adobe_analytics`                        | Merchandising events / products | `tagInput` of properties             |
| `adobe_analytics`                        | Properties to eVars             | `productIdentifier`                  |
| `facebook_pixel`, `facebook_conversions` | PII properties                  | `whitelistPiiProperties`             |
| `kafka`                                  | AVRO Schema                     | `convertToAvro`, `embedAvroSchemaID` |
| `kafka`                                  | Event type to Topic             | `enableMultiTopic`                   |
| `http`                                   | Request Body                    | `isDefaultMapping`, `xmlRootKey`     |

The other 38 screens are mapping-only, so this is "colocate when a companion
exists", not "every tab needs one". Use `tabs` to separate _unrelated_ mappings;
use one tab to hold a mapping together with the fields that configure it.

**Pick the inner shape:**

| Shape                                                                                                                               | Use when                                                     | Examples                    |
| ----------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ | --------------------------- |
| A single `mapping` with two columns                                                                                                 | One RS event maps to one destination event, nothing attached | ~20 of 28 shipped redirects |
| `dynamicCustomForm` whose `rowFields` are a `mappingRow` (the event pair) followed by `mapping` with `configKey: "eventProperties"` | Each event also carries its own property mapping             | `ga4_v2`, `hs`, `ortto`     |

For the nested shape, all three shipped destinations name the inner field
`eventProperties` and the row's left column `rsEventName` — follow that.

**The right-hand column type is determined by where destination event names come
from:**

| Destination event names are…     | Right column type                    | Examples                                             |
| -------------------------------- | ------------------------------------ | ---------------------------------------------------- |
| free-form strings                | `textInput`                          | `adobe_analytics`, `optimizely_fullstack`, `marketo` |
| a fixed vendor enum              | `singleSelect`                       | `bluecore`, `dub`, `reddit`, `facebook_pixel`        |
| fetched from the destination API | `dynamicDataSelect` / `autoComplete` | `emarsys`, `linkedIn_ads`, `ga4_v2`                  |

Left column is `textInput` with `configKey: "from"` almost universally. Where it
differs (`rsEventName`, `rudderProperty`, `event`) it is because the transformer
reads that key — **column `configKey`s are dictated by the transformer, not by
this convention.** Check the transformer before renaming one.

Translating the old field:

| Old (`dynamicForm` / `dynamicSelectForm`) | New (`mapping`)                                                |
| ----------------------------------------- | -------------------------------------------------------------- |
| `value`                                   | `configKey`                                                    |
| `keyLeft` / `keyRight`                    | `columns[0].configKey` / `columns[1].configKey`                |
| `labelLeft` / `labelRight`                | `columns[0].label` / `columns[1].label`                        |
| `placeholderLeft` / `placeholderRight`    | `columns[*].placeholder`                                       |
| `options` (on `dynamicSelectForm`)        | `columns[1]` becomes `type: "singleSelect"` with those options |

Columns may be `textInput`, `singleSelect`, `dynamicDataSelect`, or
`autoComplete`. `separatorIcon` defaults to an
arrow; only `http` sets `"colon"`, because its pairs are key:value rather than a
mapping.

> **Trap: use `configKey`, never `key`, on a mapping column.** Both are accepted
> on the top-level redirect screen, because `DynamicMapper` normalises `key` →
> `configKey`. A `mapping` nested
> inside a `dynamicCustomForm` row renders through `VisualMapper` **directly**
> , skipping that normalisation — rows are then
> keyed `undefined`. Nothing hits this today (`http` and `topsort` use `key`, but
> both are top-level), so it is latent rather than broken.

`mapping` is also valid inside `dynamicCustomForm.rowFields` — that path _is_
handled.

---

## 7. Consent settings

If the destination supports consent management, add
`consentSettingsTemplate` and a section carrying `"id": "consentSettings"` in
the `Configuration settings` collapsible. Copy the `consentSettingsTemplate`
block from [`scripts/template-ui-config.json`](../../../../scripts/template-ui-config.json)
rather than hand-writing it — the provider list and resolution-strategy logic
are standardised, and `test/consentManagementFieldsIntegrity.test.ts` asserts
against it.

**First decide whether the destination supports consent at all.** The gate is
`consentManagement` under `destConfig.<sourceType>` in `db-config.json` — not the
destination's category, and not what the old ui-config happened to render. Split
that way, the v2 corpus is unambiguous:

| `consentManagement` in `destConfig` | `consentSettingsTemplate` | Count |
| ----------------------------------- | ------------------------- | ----- |
| yes                                 | present                   | 75    |
| yes                                 | absent                    | **0** |
| no                                  | present — **dead config** | 3     |
| no                                  | absent                    | 3     |

So: if the destination supports consent the template is **mandatory** — 75 for,
zero against — and `test/consentManagementFieldsIntegrity.test.ts` enforces it.
If it does not, **omit the template**; adding one gives you fields with nowhere
to persist.

`custom_audience`, `linkedin_audience` and `tiktok_audience` are the three
carrying a dead template: no `consentManagement` in `destConfig`, absent from
`includeKeys`, and no `consentManagement` property in `schema.json`. They are on
the test's `skipDestinations` list, so nothing catches it. Do not copy them.

Audience destinations are **not** a category exemption — 8 of the 14 audience
destinations do support consent and are enforced (`amazon_audience`,
`fb_custom_audience`, `x_audience`, `customerio_audience`,
`launchdarkly_audience`, and the v1 `bingads_audience`, `criteo_audience`,
`snapchat_custom_audience`). Check `destConfig`, not the name.

The template and the `"id": "consentSettings"` section are a pair — the framework
injects the template's fields into that section, which is why the
section is an empty `groups: []` shell in every shipped config.

**Expect it to surface an `items.required` tightening.** The block marks
`provider` `required: true`, so the generator wants
`items.required: ["provider"]` on every source type — and 234 of the 241 schemas
defining `consentManagement` do not carry it (2026-09-10; the count falls by one
per migration). That is a pre-existing gap you inherit, and it is a
breaking change for a saved row with no `provider`. See the SKILL's Step 2
(`items.required`) before you accept it.

---

## 8. `db-config.json` checklist

Migration frequently requires db-config changes alongside the ui-config:

- [ ] `config.supportedConnectionModes` — accurate per source type. This is what the connection-mode picker renders.
- [ ] `config.destConfig.<sourceType>` / `destConfig.defaultConfig` — every `sdkTemplate` `configKey` appears in one of them, or it will not render.
- [ ] `config.secretKeys` — matches every field marked `"secret": true`.
- [ ] `config.immutableKeys` — carries any field that had `immutable: true` or `readOnly: true` in the old ui-config.

---

## 9. Regenerate `schema.json` and validate

`schema.json` is generated from `ui-config.json` and must be regenerated —
`scripts/schemaGenerator.py` already understands the v2 shape
(`baseTemplate` / `sdkTemplate` / `consentSettingsTemplate` / `rowFields`).

```bash
# one-time setup
npm run setup

# check what would change (no write) - run this FIRST, at HEAD, before editing
npm run check:schema:destination <dest>

# full test suite (fixture-driven schema validation, ~25s)
npx jest test/validation.test.ts
```

**Capture a baseline before you touch anything.** Several destinations already
emit generator warnings at HEAD (`facebook_pixel`'s `consentManagement`,
`braze` per `.agents/knowledge/concerns.md`). Without a before-image you cannot
tell a warning you introduced from one that was already there.

**But a baseline warning is not a warning you get to keep.** It only tells you
whose it is. `run-schema-validation.sh` iterates over the files a PR **changes**,
which is why the warning has sat there unnoticed — nobody was touching that
destination. Your migration changes it, so every warning it already carried turns
fatal on your PR. Plan on fixing the inherited ones, and report them to the user
as scope the migration picked up rather than created: they are usually a schema
tightening against already-saved configs, which is the user's call to accept.

> **The `$delete` trap.** `get_json_diff` is called with inverted arguments at 2
> of its 5 call sites: `consentSettingsTemplate` (`:1676`) and
> `sdkTemplate.groups[].fields` (`:1651`) pass `(new, cur)`; the old format
> (`:1526`), `baseTemplate` (`:1578`) and `sdkTemplate.fields` (`:1624`) pass
> `(cur, new)`. Consent fields cross that boundary during migration, so the same
> untouched discrepancy prints as an additive `required: ["provider"]` block
> before and as `{'$delete': ['required']}` after. Both say the committed
> `schema.json` is **missing** the key. Do not diff warning bodies across the
> migration — compare which fields warn.

**`update:schema:destination` is not safe to run blindly.** On `facebook_pixel`
it narrowed `testEventCode`'s pattern from
`(^\{\{.*\|\|(.*)\}\}$)|(^env[.].+)|^(.{0,100})$` to `^(.{0,100})$`,
dropping the `{{...}}` / `env.` interpolation escape hatch, and added unrelated
`required: ["provider"]` to consentManagement. Run it, then **read the diff line
by line** and revert anything you did not intend. Hand-editing `schema.json` is
often the safer option.

Enforcement lives in **CI, not the pre-commit hook**: `.github/workflows/test.yml`
passes changed files to `scripts/run-schema-validation.sh`, which treats any
line containing "warning" as fatal. `schemaGenerator.py` itself always exits 0
on a diff, so locally the check is advisory — you have to read the output.

> `check:schema:destination:all` currently **crashes** on `custom_audience`
> (`KeyError: 'configKey'` at `schemaGenerator.py:171`, because
> `audienceDeliveryApiBuilder` has no `configKey`). There is no working
> repo-wide baseline; check per destination.

> Warnings are written to unbuffered stderr and appear **before** the buffered
> `Schema diff for ...` banner. Do not filter the output from that banner
> onward or you will hide the very warnings you are looking for.

---

## 10. Verify in the webapp

Run the webapp against your local `rudder-integrations-config` and check, for
**each connected source type** (web, android, ios, cloud, warehouse as
applicable):

**Create flow**

- [ ] Only mandatory fields appear — the create form should be noticeably shorter than the old one.
- [ ] Connection mode picker renders with the right options.
- [ ] Immutable-field notice renders if the destination has `immutableKeys`.
- [ ] Validation fires on required/regex fields.

**Edit flow**

- [ ] Every collapsible section, section and group renders in the intended order.
- [ ] SDK settings group appears when connection mode is `device`/`hybrid`, and disappears on `cloud`.
- [ ] Consent settings group renders (if applicable).
- [ ] Every `redirect` field navigates to its mapping screen and saves.
- [ ] Conditional fields (`preRequisites`, `conditions`) appear and disappear correctly.

**Round-trip an existing destination**

- [ ] Open a destination created on the old form. Every previously saved value renders in the new form.
- [ ] Save without changes; diff the resulting config against the original. It should be identical apart from expected connection-mode normalisation.

This last check is the one that catches renamed `configKey`s. A typo there does
not error — it silently drops the user's saved value.

---

## Gotchas

**Two shapes for connection mode.** Saved config uses
`connectionMode.<sourceType>`; the form's working state uses
`<sourceType>-connectionMode`. `preRequisites` you write by
hand in `baseTemplate` use the dotted form (`connectionMode.web`); the framework
injects the hyphenated form into `sdkTemplate` groups. Copy the dotted form when
writing your own gates.

**Silent failures are the norm.** A wrong section title, a `configKey` missing
from `destConfig`, or a `mapping` field in the wrong place all produce a form
that renders _without_ the affected part and without any console error. When
something is missing, check the structural contract in step 2 first.

**The webapp's type definitions drift from reality.** Its `icon` type omits `otherSettings`;
`MappingField` declares `separatorIcon` and `addButtonLabel` as required though
most shipped configs omit them. Where the type and the shipped configs disagree,
follow the shipped configs and the renderer.

**Both builders must stay in sync.** Per the framework doc: any feature added to
one form builder should be added to the other until the old one is retired.

---

## PR checklist

- [ ] `ui-config.json` converted; `uiConfig` is an object, not an array
- [ ] Initial setup contains all and only mandatory fields
- [ ] Structural contract respected (step 2)
- [ ] Every field has a meaningful `label` and a crisp `note`
- [ ] Device-mode fields in `sdkTemplate`, cross-checked against `destConfig`
- [ ] Client-side event filtering, if present, uses `tagInput` with `tagKey: "eventName"` and a `connectionMode.<sourceType>` gate (step 5)
- [ ] Event mapping is its own collapsible block with `hideEditIcon: true`, one untitled section, and a redirect-only group (step 6)
- [ ] `db-config.json` checklist complete (step 8)
- [ ] `schema.json` regenerated; `npm run test:silent` green
- [ ] **Zero** generator warnings for this destination — inherited ones fixed, not baselined away
- [ ] Any `required` the regeneration added, at top level or inside a `dynamicCustomForm`, called out and approved
- [ ] Verified in the webapp for every supported source type, including the round-trip check
- [ ] Lossy substitutions (step 4) called out explicitly in the PR description
- [ ] Design/PM sign-off — this ships to all users of the destination at once
