# Form builder v2 — field reference

Lookup detail for the `migrate-destination-to-form-builder-v2` skill. **The
skill carries the procedure, the baseline and the gates — read it first.** This
file is what you consult while translating individual fields.

Canonical configs to copy shapes from: `am` (device mode, `sdkTemplate`, event
filtering) and `adobe_analytics` (`redirect` + `redirectGroups`). Take the rules
from [`CONVENTIONS.md`](../../../../CONVENTIONS.md), not from whichever
neighbour you opened — most of the tree predates it.

For the skeleton of a v2 `ui-config.json`, copy
[`scripts/template-ui-config.json`](../../../../scripts/template-ui-config.json)
directly. It already encodes the structural contract as data, including the full
standardised consent block.

---

## 1. Attribute renames

These apply to every field regardless of type:

| Old                                                                                                    | New                                                 | Notes                                                                                                                                                                                                                                                                                                              |
| ------------------------------------------------------------------------------------------------------ | --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `value`                                                                                                | `configKey`                                         | The single most common rename                                                                                                                                                                                                                                                                                      |
| `label`                                                                                                | `label`                                             | unchanged, but now **required** on input fields — write a real one                                                                                                                                                                                                                                                 |
| `footerNote`                                                                                           | `note`                                              |                                                                                                                                                                                                                                                                                                                    |
| `sectionNote`                                                                                          | `note` on the enclosing section/group               |                                                                                                                                                                                                                                                                                                                    |
| `labelNote`                                                                                            | `note`                                              | Merge into `note`; if the field had both `labelNote` and `footerNote`, combine them into one crisp sentence                                                                                                                                                                                                        |
| `footerURL: { text, link }`                                                                            | `note` as an array                                  | `["Some text ", { "text": "link text", "link": "https://..." }]`                                                                                                                                                                                                                                                   |
| `options: [{ name, value }]`                                                                           | `options: [{ label, value }]`                       | `name` → `label`                                                                                                                                                                                                                                                                                                   |
| `defaultOption: { name, value }`                                                                       | `default: "<value>"`                                | Just the value string                                                                                                                                                                                                                                                                                              |
| `preRequisiteField` — **both a bare object and an array occur** (92 object, 152 array across the tree) | `preRequisites: { fields: [{ configKey, value }] }` | Normalise both into the array form. `name`→`configKey`, `selectedValue`→`value`. Add `"condition": "or"` only if any-of was intended; the default is AND, and a singleton object carries no condition to preserve                                                                                                  |
| `featureFlag: "AMP_..."`                                                                               | **stop — no safe mechanical equivalent**            | All 33 occurrences in the tree sit on an individual `options[]` entry, not on a field. `preRequisites.featureFlags` gates the **whole field**, so converting one hides the entire selector and loses its unflagged options. Ask the webapp team for an option-level equivalent before migrating such a destination |
| `immutable: true`                                                                                      | _(no ui-config equivalent)_                         | Move the key into `db-config.json` → `config.immutableKeys: [...]`; v2 reads `destinationDefinition.config.immutableKeys`                                                                                                                                                                                          |
| `required`                                                                                             | `required`                                          | unchanged                                                                                                                                                                                                                                                                                                          |
| `secret`                                                                                               | `secret`                                            | unchanged (`textInput` only)                                                                                                                                                                                                                                                                                       |
| `regex`, `regexErrorMessage`, `placeholder`, `default`                                                 | unchanged                                           |                                                                                                                                                                                                                                                                                                                    |

`preRequisites` is shared between both builders, so if the old config already uses
`preRequisites` rather than `preRequisiteField`, copy it across as-is.

---

---

## 2. Field type mapping

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
| `dynamicForm`                                    | 65    | `mapping` **behind a `redirect`** | See §4                                                                                           |
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

---

## 3. Device-mode fields → `sdkTemplate`

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

> **Sub-groups are invisible to `schemaGenerator.py`.** `sdkTemplate.groups[]`
> renders in the UI, but every generator pass iterates `sdkTemplate.fields`
> only — there is no `groups` traversal anywhere in the script. A field placed
> in a sub-group is **not generated into `schema.json`, and produces no
> warning**: verified by adding a probe field to `am`'s sub-group, which the
> generator ignored entirely and `-update` declined to add. `am`'s 11 sub-group
> fields are in its schema only because they predate the regrouping.
>
> Keep every device-mode field in `sdkTemplate.fields`. Use `groups[]` only to
> re-title fields that are already there, and re-run the generator afterwards to
> confirm nothing dropped out.

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

---

## 4. Event mapping → its own collapsible block + `redirect`

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
