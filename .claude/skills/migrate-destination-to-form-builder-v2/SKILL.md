---
name: migrate-destination-to-form-builder-v2
description: Use when converting a destination's ui-config.json from the legacy array format to form builder v2 (baseTemplate/sdkTemplate/redirectGroups), or when asked to move a destination to the new form builder, new UI form builder, or form builder v2
argument-hint: <destination-name> (e.g. "adj" or "clevertap")
---

## Migrate a destination to form builder v2

**Reference files — read before starting:**

- [`references/migrating-destination-to-form-builder-v2.md`](references/migrating-destination-to-form-builder-v2.md) — the full runbook. **This skill is the procedure; that file is the detail.** Load the section you need, when you need it:
  - **§2 + §2a** before Step 3 — the structural contract and the `schema.required` rule
  - **§3 + §4** while translating fields — attribute renames and the per-type table
  - **§5** if the destination has device-mode fields or client-side event filtering
  - **§6** if it has any mapping, plus the `key` vs `configKey` trap
  - **§Gotchas** if something renders blank and you cannot see why
- [`CONVENTIONS.md`](../../../CONVENTIONS.md) — [String `pattern` / `regex`](../../../CONVENTIONS.md#string-pattern-and-regex), [Optional fields must accept the empty string](../../../CONVENTIONS.md#optional-fields-must-accept-the-empty-string), [Restricting a field by connection mode](../../../CONVENTIONS.md#restricting-a-field-by-connection-mode) all apply.
- `am` (device mode, sdkTemplate, event filtering) and `adobe_analytics` (redirect + redirectGroups) are the reference configs.

**Progress:**

- [ ] Step 0: Capture the baseline (before editing anything)
- [ ] Step 1: Inventory the old config
- [ ] Step 2: Decide Initial setup contents — gate on `required` changes
- [ ] Step 3: Build `baseTemplate`
- [ ] Step 4: `sdkTemplate`, event filtering, event mapping
- [ ] Step 5: Update `db-config.json`
- [ ] Step 6: Regenerate `schema.json`
- [ ] Step 7: Safety gate — compare against Step 0
- [ ] Step 8: Verify in the webapp

**The migration is one-way and ungated.** v2 activates purely because `uiConfig` stops being a JSON array (`rudder-webapp` `components/common/util/util.ts:195`). There is no feature flag. Merging ships the new form to every workspace using the destination.

---

## Gotchas

Environment facts that defy the obvious assumption. Read these before Step 0.

- **Generator warnings print to unbuffered stderr, which appears _before_ the buffered `Schema diff for ...` banner.** Filtering from that banner onward (`sed '/Schema diff/,$p'`) hides every warning you are looking for, including the `required` one.
- **`schemaGenerator.py` always exits 0 on a schema diff.** Only a missing folder exits non-zero. Locally the check is advisory — you must read the output. In CI, `.github/workflows/test.yml` pipes changed files to `scripts/run-schema-validation.sh`, which treats any line containing "warning" as fatal. It is **not** a pre-commit hook.
- **Several destinations already emit warnings at HEAD** — `facebook_pixel` and `adj` (consentManagement), `braze` (per `.agents/knowledge/concerns.md`). This is why Step 0 exists: without a baseline you cannot tell your warning from theirs.
- **`check:schema:destination:all` crashes** on `custom_audience` — `KeyError: 'configKey'` at `schemaGenerator.py:171`, because `audienceDeliveryApiBuilder` is a multi-key field with no `configKey`. There is no working repo-wide baseline; check one destination at a time.
- **`npm run check:schema:destination <dir>` takes no `--`** (per CLAUDE.md), and **`npx jest -d <dir>` does not filter** — the whole suite runs, ~25s. Both are expected.
- **A `mapping` field placed directly in a `baseTemplate` group renders nothing.** The base-template switch has no `mapping` case; mappings only render behind a `redirect`, or inside `dynamicCustomForm.rowFields`.
- **An `sdkTemplate` field whose `configKey` is absent from `destConfig` silently does not appear.** No error, no warning in the form — just a missing field.
- **`connectionModes.web` is not a key the app ever writes.** Only `connectionModes.cloud`, `.webDevice` and `.mobileDevice` exist. Three shipped destinations gate on it, so that clause is dead — do not copy it.
- **A renamed `configKey` does not error.** It silently drops the customer's saved value. This is what the Step 8 round-trip catches.

---

### Step 0: Capture the baseline — before editing anything

**Do this first. Without a before-image you cannot tell a problem you introduced from one that was already there.** Several destinations already emit generator warnings at HEAD.

```bash
cd <repo root>
git status --short              # must be clean for this destination
python3 scripts/schemaGenerator.py destination -name <dest> 2>&1 | tee /tmp/<dest>-baseline.txt
npx jest test/validation.test.ts 2>&1 | tail -5   # note pass/fail counts
python3 -c "import json;print(json.load(open('src/configurations/destinations/<dest>/schema.json'))['configSchema'].get('required'))"
```

Record: the set of `UserWarning` lines, the test counts, and the `required` array.

Do not filter this output — see Gotchas. If `schemaGenerator.py` crashes for this destination, stop and report it rather than migrating blind.

---

### Step 1: Inventory the old config

Build a row per field from the existing `ui-config.json`: `configKey` (old `value`), label, type, required, secret, conditional.

Then classify each field's home from `db-config.json` — **by source scoping, not by `defaultConfig` membership**:

| `configKey` listed in      | Goes in                                                              |
| -------------------------- | -------------------------------------------------------------------- |
| `destConfig.<sourceType>`  | `sdkTemplate` — mandatory; `baseTemplate` would never populate it    |
| `destConfig.defaultConfig` | `baseTemplate` normally; `sdkTemplate` if device-mode-only behaviour |
| neither                    | nothing renders — fix `db-config.json` first                         |

Do not infer device-mode from old section titles ("Native SDK", "Client-side Events Filtering"); they are unreliable.

---

### Step 2: Decide the Initial setup contents — this sets validation, not just layout

**STOP and think here. This is where this migration has already shipped a production bug.**

A field enters `schema.required` by **placement**, not because it is marked required (`schemaGenerator.py:1376-1385`): title is exactly `Initial setup` AND `configKey` is in `defaultConfig` AND (no `preRequisites` OR `required: true`).

The old format's rule is the opposite — `required: true` and placement irrelevant. **So migration changes the meaning of "required."**

**The generator is the authority on this — do not hand-compute it.** Running the
generator prints an authoritative warning whenever the required set would change:

```
UserWarning: For required field Difference is :  { "$insert": [ [ 1, "accessToken" ] ] }
```

Capture that line at baseline (Step 0) and again after drafting. A `$insert`
that was not there at baseline is a field your migration made mandatory.

```bash
python3 scripts/schemaGenerator.py destination -name <dest> 2>&1 | grep -A12 "For required field"
```

`-A12` matters: the field name sits ~7 lines below the match, so a shorter
context window shows you `"$insert": [ [` and cuts off before the name. **No
output (grep exits 1) is the pass case** — it means the required set is
unchanged.

Reimplementing the rule in a throwaway script is tempting and unreliable: a
faithful-looking reimplementation disagrees with 44 of the 247 shipped schemas,
because the generator also skips conditional fields, folds some requirements
into `allOf`/`oneOf` branches, and several schemas carry hand-added entries.
Use the rule below to _understand and fix_ what the generator reports, not to
compute it yourself.

For each inserted field, choose deliberately:

- genuinely mandatory for **existing** configs too → keep it, and say so explicitly in the PR
- mandatory only in some modes → give it `preRequisites` and enforce with a schema conditional per [CONVENTIONS.md](../../../CONVENTIONS.md#restricting-a-field-by-connection-mode)
- not actually mandatory → move it out of Initial setup

Precedent for getting this wrong: `facebook_pixel`'s `accessToken` became required at `f6ff024f` (Oct 2023) with no `required: true` anywhere — placement alone did it — and was walked back at `32e1d10d` (`fix: make accessToken required only for cloud mode`) four months later. `mp` did the same with `dataResidency` and `identityMergeApi`.

**Do not proceed past this step with an unexplained insertion. Surface the list to the user and get an explicit decision.**

---

### Step 3: Build `baseTemplate`

Start from [`scripts/template-ui-config.json`](../../../scripts/template-ui-config.json). Honour the structural contract in the runbook — positional and exact-title dependencies that fail **silently** when wrong:

- `baseTemplate[0].sections[1].groups[0]` = connection mode slot, `fields: []` (framework overwrites)
- `baseTemplate[0].sections[2].groups[0]` = immutable fields (optional)
- a collapsible titled exactly `Configuration settings`, containing a section titled exactly `Destination settings`
- consent needs a section with `"id": "consentSettings"`

Apply the attribute renames and per-type mapping from the runbook (`value`→`configKey`, `options[].name`→`label`, `defaultOption`→`default`, `preRequisiteField`→`preRequisites`, `dynamicForm`/`dynamicSelectForm`→`mapping`, `useNativeSDK`/`defaultCheckbox`→delete).

Every field needs a real `label` and a crisp `note`. For `regex` on every field and what an optional field's regex must accept, follow [String `pattern` / `regex`](../../../CONVENTIONS.md#string-pattern-and-regex) and [Optional fields must accept the empty string](../../../CONVENTIONS.md#optional-fields-must-accept-the-empty-string) — do not copy a regex from a neighbouring destination, most of the tree predates those rules.

---

### Step 4: `sdkTemplate`, event filtering, event mapping

Three patterns with fixed shapes — copy them from the runbook rather than inventing:

**Device-mode fields** → `sdkTemplate`. A field renders only if its `configKey` is in `destConfig` for that source type; otherwise it silently disappears.

**Client-side event filtering** → stays in `baseTemplate`, in `Configuration settings` → section `Other settings` (`icon: "otherSettings"`). `singleSelect(eventFilteringOption)` plus two **`tagInput`s** with `tagKey: "eventName"` — the `tagKey` is what preserves the stored `[{"eventName": "..."}]` shape. Gate the group on `connectionMode.<sourceType>: "device"` OR'd across exactly the source types that support device. Do not copy the gate from a random migrated destination; four different idioms exist and three destinations use a dead `connectionModes.web` key.

**Event mapping** → its own top-level collapsible with `hideEditIcon: true`, one untitled section, and a group holding **only** `redirect` fields. The mapping itself goes in `redirectGroups`. A `mapping` field placed directly in a base-template group renders nothing.

Keep a mapping's companion fields (the ones that change how it is read — a prefix, a delimiter, an "is default" toggle) on the **same tab** as that mapping, not in `Configuration settings`.

---

### Step 5: Update `db-config.json`

- `supportedConnectionModes` — accurate per source type; this drives the picker
- `destConfig.<sourceType>` — must contain `useNativeSDK` **and** `connectionMode` for every source type supporting more than cloud; add `useNativeSDKToSend` if `hybrid` is supported, or hybrid collapses into device
- every `sdkTemplate` `configKey` appears in `destConfig` somewhere
- `secretKeys` matches every `"secret": true` field
- `immutableKeys` carries anything that was `immutable`/`readOnly` in the old ui-config

---

### Step 6: Regenerate `schema.json` — read every line of the diff

```bash
npm run check:schema:destination <dest>          # inspect first
npm run update:schema:destination <dest>         # then write
git diff src/configurations/destinations/<dest>/schema.json
```

**`update:schema:destination` is not safe to run blindly.** On `facebook_pixel` it silently narrowed `testEventCode`'s pattern, dropping the `{{...}}` / `env.` interpolation escape hatch, and added unrelated `required` entries. Revert anything you did not intend; hand-editing is often safer.

---

### Step 7: The safety gate — compare against Step 0

Re-run the Step 0 commands and diff against what you recorded. **Loop until
every row passes** — fix, re-run, re-compare. Do not proceed with a known-red row.

| Check                              | Pass condition                                                                                                 | If it fails                                            |
| ---------------------------------- | -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| Generator warnings                 | No warning that was not in `/tmp/<dest>-baseline.txt`                                                          | Fix it. Pre-existing warnings stay; new ones are yours |
| `schema.required`                  | No `For required field Difference` warning that was absent at baseline, or every insertion explicitly approved | Go back to Step 2                                      |
| `npx jest test/validation.test.ts` | Same pass count as baseline                                                                                    | A fixture failure means saved configs would now break  |
| `git diff` on `schema.json`        | Only changes you can each explain                                                                              | Revert the rest                                        |
| `npm run format`                   | Clean `git diff --exit-code` afterwards                                                                        | CI runs this check                                     |

Classify every remaining line of the schema diff:

- **breaking** — `required` additions, removed properties, narrowed `enum`/`pattern`, tightened `type`
- **mechanical** — `connectionMode` added to properties, new properties for genuinely new fields
- **suspicious** — anything else

**Report the classified diff to the user and get explicit confirmation before finishing.** "The schema changed" is not a finding to bury in a summary; name each breaking change and what it does to already-saved destinations. If the schema is unchanged, say that plainly — it is the good outcome and worth stating.

---

### Step 8: Verify in the webapp

For each connected source type (web, android, ios, cloud, warehouse as applicable):

- **Create flow** — only mandatory fields appear; connection mode picker renders; validation fires
- **Edit flow** — sections render in order; SDK group appears on `device`/`hybrid` and vanishes on `cloud`; each `redirect` navigates and saves; conditional fields toggle correctly
- **Round-trip** — open a destination created on the **old** form, confirm every saved value renders, save without changes and diff the resulting config against the original

The round-trip is what catches a renamed `configKey`. A typo there does not error; it silently drops the customer's saved value.

---

### Red flags — stop and re-check

- A field moved into Initial setup "because it's important" without checking the `required` delta
- `npm run update:schema:destination` run and the diff not read
- Generator output filtered from the `Schema diff` banner onward
- A `mapping` field placed directly in a `baseTemplate` group
- Event-filtering gate copied verbatim from another destination
- Schema diff reported as "regenerated the schema" rather than as a classified list
- `--no-verify` used to get past the pre-commit hook
