---
name: migrate-destination-to-form-builder-v2
description: Use when converting a destination's ui-config.json from the legacy array format to form builder v2 (baseTemplate/sdkTemplate/redirectGroups), or when asked to move a destination to the new form builder, new UI form builder, or form builder v2
argument-hint: <destination-name> (e.g. "adj" or "clevertap")
---

## Migrate a destination to form builder v2

**Reference files — read before starting:**

- [`references/migrating-destination-to-form-builder-v2.md`](references/migrating-destination-to-form-builder-v2.md) — the full runbook. **This skill is the procedure; that file is the detail.** Load the section you need, when you need it:
  - **§1 + §2** while translating fields — attribute renames and the per-type table
  - **§3** if the destination has device-mode fields or client-side event filtering
  - **§4** if it has any mapping, plus the `key` vs `configKey` trap
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
- [ ] Step 9: Get design/PM sign-off before merging

**The migration is one-way and ungated.** v2 activates purely because `uiConfig` stops being a JSON array — the webapp picks the renderer on that one test. There is no feature flag. Merging ships the new form to every workspace using the destination.

---

## Gotchas

Environment facts that defy the obvious assumption. Read these before Step 0.

- **Generator warnings print to unbuffered stderr, which appears _before_ the buffered `Schema diff for ...` banner.** Filtering from that banner onward (`sed '/Schema diff/,$p'`) hides every warning you are looking for, including the `required` one.
- **`schemaGenerator.py`'s exit code tells you nothing.** It exits 0 on a schema diff _and_ on a destination name that does not exist — a typo in `<dest>` looks exactly like a clean run. Confirm the directory exists before trusting silence. Locally the check is advisory — you must read the output. In CI, `.github/workflows/test.yml` pipes changed files to `scripts/run-schema-validation.sh`, which treats any line containing "warning" as fatal. It is **not** a pre-commit hook.
- **Several destinations already emit warnings at HEAD** — `facebook_pixel` and `adj` (consentManagement), `braze` (per `.agents/knowledge/concerns.md`). This is why Step 0 exists: without a baseline you cannot tell your warning from theirs.
- **A pre-existing warning on the destination you are migrating is _your_ blocker, not background noise.** It is dormant at HEAD only because `run-schema-validation.sh` runs over files a PR **changes** — nobody is touching that destination. (That wrapper reads only `$1`, so on a PR touching several destinations it validates just the first; do not rely on CI to catch the others — check each one locally.) Your migration is what makes it changed, so every warning it already carried becomes fatal in CI on your PR. Baseline the warning to prove you did not cause it; then fix it anyway. The merge gate is **zero warnings for this destination**, not "no new warnings" — see Step 7.
- **A `$delete` in a consentSettingsTemplate warning means the committed schema is _missing_ that key, not that it has a spare one.** `get_json_diff` is called with inverted arguments at 2 of its 5 call sites — `consentSettingsTemplate` (`schemaGenerator.py:1676`) and the second `sdkTemplate.fields` pass (`:1651`) use `(new, cur)`, while the old format (`:1526`), `baseTemplate` (`:1578`) and the first `sdkTemplate.fields` pass (`:1624`) use `(cur, new)`. Consent fields cross that boundary during migration, so **one unchanged discrepancy prints as an addition before and as `$delete` after**. Both mean "add it to `schema.json`".
- **A `mapping` field placed directly in a `baseTemplate` group renders nothing.** The base-template switch has no `mapping` case; mappings only render behind a `redirect`, or inside `dynamicCustomForm.rowFields`.
- **An `sdkTemplate` field whose `configKey` is absent from `destConfig` silently does not appear.** No error, no warning in the form — just a missing field.
- **`connectionModes.web` is not a key the app ever writes.** Only `connectionModes.cloud`, `.webDevice` and `.mobileDevice` exist. Three shipped destinations gate on it, so that clause is dead — do not copy it.
- **A renamed `configKey` does not error.** It silently drops the customer's saved value. This is what the Step 8 round-trip catches.

---

### Step 0: Capture the baseline — before editing anything

**Do this first. Without a before-image you cannot tell a problem you introduced from one that was already there.**

```bash
cd <repo root>
git status --short              # must be clean for this destination
python3 scripts/schemaGenerator.py destination -name <dest> 2>&1 | tee /tmp/<dest>-baseline.txt
npx jest test/validation.test.ts 2>&1 | tail -5   # note pass/fail counts
python3 -c "import json;print(json.load(open('src/configurations/destinations/<dest>/schema.json'))['configSchema'].get('required'))"
```

Record: the set of `UserWarning` lines, the test counts, and the `required` array.

Warning **bodies** are not comparable across the migration (see Gotchas — the diff
direction inverts for consent), and the `schemaGenerator.py:<line>` prefix moves
too. Record which **fields** warn, which is stable:

```bash
grep -oE 'For type:[A-Za-z]+ field:[A-Za-z]+|For required field|[A-Za-z]+ field is not in schema' \
  /tmp/<dest>-baseline.txt | sort -u
```

Do not filter this output — see Gotchas. If `schemaGenerator.py` crashes, stop and report it rather than migrating blind — a field type it cannot key, such as the multi-key `audienceDeliveryApiBuilder`, raises `KeyError: 'configKey'` at `schemaGenerator.py:171`.

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

Three separate paths append to the schema's top-level `required`, and only the
first is about placement:

| Source                                          | Condition                                                                                                                              |
| ----------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `baseTemplate` (`schemaGenerator.py:1376-1385`) | collapsible titled exactly `Initial setup` **and** `configKey` in `defaultConfig` **and** (no `preRequisites` **or** `required: true`) |
| `sdkTemplate.fields` (`:1403-1408`)             | `required: true` **and** `configKey` in `defaultConfig` — **placement irrelevant**                                                     |
| `consentSettingsTemplate.fields` (`:1414-1420`) | `required: true` **and** `configKey` in `defaultConfig` — **placement irrelevant**                                                     |

So Initial setup is the path that catches people out, but it is not the only
one: marking a device-mode or consent field `required: true` tightens the schema
just as hard, from outside Initial setup entirely.

The old format's rule is `required: true` with placement irrelevant. **So
migration changes the meaning of "required" for `baseTemplate` fields**, while
leaving the other two paths behaving as before.

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

#### The same hazard one level down: `items.required`

Everything above is about **top-level** `schema.required`. A `dynamicCustomForm`
has its own required set with the same consequences, and the `For required field`
check above **will not report it** — it arrives as a `For type:dynamicCustomForm
field:<name>` warning instead, which is easy to read as cosmetic drift.

The rule (`schemaGenerator.py:630-633`, `:663`): a `rowField` with
`required: true` is added to the form's `items.required` only if
`is_always_visible(...)` also holds — absence of `preRequisites` is necessary
but **not** sufficient, since a row can be conditional on a sibling's value. A
conditional one (consent's `resolutionStrategy`) is folded into an
`allOf`/`if`/`then` branch instead. As above, read the generator's warning
rather than deciding this by eye.

This bites hardest on consent — when the destination supports it — because the standard block marks `provider`
`required: true` — so the generator wants `items.required: ["provider"]` on every
source type, and **234 of the 241 schemas that define `consentManagement` do not
have it** (as of 2026-09-10 — this count drops by one each time somebody
migrates a destination). Whichever destination you are migrating, expect to
inherit it. To recompute:

```bash
python3 - <<'EOF'
import json, glob
n = [f.split('/')[-2] for f in glob.glob('src/configurations/destinations/*/schema.json')
     if (lambda c: c and 'properties' in c and not any('required' in v.get('items', {})
         for v in c['properties'].values()))(
         json.load(open(f)).get('configSchema', {}).get('properties', {}).get('consentManagement'))]
print(len(n))
EOF
```

Adding it is a real tightening: a saved `consentManagement` row with no `provider`
would start failing validation. An empty array is unaffected, and `provider` is
already `required: true` in the UI plus the `uniqueRowFields` key, so genuine rows
carry one — but that is an argument for the change, not a reason to skip asking.
**Treat it exactly like a top-level insertion: name it, and get an explicit
decision before committing.**

---

### Step 3: Build `baseTemplate`

Start from [`scripts/template-ui-config.json`](../../../scripts/template-ui-config.json). Honour the structural contract in the runbook — positional and exact-title dependencies that fail **silently** when wrong:

- `baseTemplate[0].sections[1].groups[0]` = connection mode slot, `fields: []` (framework overwrites)
- `baseTemplate[0].sections[2].groups[0]` = immutable fields (optional)
- a collapsible titled exactly `Configuration settings`, containing a section titled exactly `Destination settings`
- consent, **only if `destConfig.<sourceType>` lists `consentManagement`**, needs a section with `"id": "consentSettings"` plus a `consentSettingsTemplate`. Gate on `db-config.json`, not on the destination's category: all 75 v2 destinations that support consent have the template and none lack it, but 3 that do not support it (`custom_audience`, `linkedin_audience`, `tiktok_audience`) ship a dead one — fields with nowhere to persist. Do not copy those. Copy the consent block from `scripts/template-ui-config.json`, which carries the standardised provider list.

Apply the attribute renames and per-type mapping from the runbook (`value`→`configKey`, `options[].name`→`label`, `defaultOption`→`default`, `preRequisiteField`→`preRequisites`, `dynamicForm`/`dynamicSelectForm`→`mapping`, `useNativeSDK`/`defaultCheckbox`→delete).

Every field needs a real `label` and a crisp `note`. For `regex` on every field and what an optional field's regex must accept, follow [String `pattern` / `regex`](../../../CONVENTIONS.md#string-pattern-and-regex) and [Optional fields must accept the empty string](../../../CONVENTIONS.md#optional-fields-must-accept-the-empty-string) — do not copy a regex from a neighbouring destination, most of the tree predates those rules.

---

### Step 4: `sdkTemplate`, event filtering, event mapping

Three patterns with fixed shapes — copy them from the runbook rather than inventing:

**Device-mode fields** → `sdkTemplate`. A field renders only if its `configKey` is in `destConfig` for that source type; otherwise it silently disappears.

**Client-side event filtering** → stays in `baseTemplate`, in `Configuration settings` → section `Other settings` (`icon: "otherSettings"`). `singleSelect(eventFilteringOption)` plus two **`tagInput`s** with `tagKey: "eventName"` — the `tagKey` is what preserves the stored `[{"eventName": "..."}]` shape. Gate the group on `connectionMode.<sourceType>: "device"` OR'd across exactly the source types that support device. Do not copy the gate from another destination — four idioms exist and one is dead (see Gotchas).

**Event mapping** → its own top-level collapsible with `hideEditIcon: true`, one untitled section, and a group holding **only** `redirect` fields. The mapping itself goes in `redirectGroups`.

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

The baseline tells you whether a warning is _yours_. It does not excuse it: CI
validates the destinations your PR **changes**, so anything still warning here
blocks the merge regardless of who caused it. Compare warning **field names**,
not bodies (Step 0).

| Check                              | Pass condition                                                                                                       | If it fails                                              |
| ---------------------------------- | -------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| Generator warnings                 | **Zero** warnings for this destination — the merge gate, not "no new warnings". Baseline only decides whose they are | Fix it, inherited or not. Report inherited ones as scope |
| `schema.required`                  | No `For required field Difference` warning that was absent at baseline, or every insertion explicitly approved       | Go back to Step 2                                        |
| `items.required`                   | No `For type:dynamicCustomForm field:<name>` warning left, and any `required` it added was explicitly approved       | Go back to Step 2's `items.required` section             |
| `npx jest test/validation.test.ts` | Same pass count as baseline                                                                                          | A fixture failure means saved configs would now break    |
| `git diff` on `schema.json`        | Only changes you can each explain                                                                                    | Revert the rest                                          |
| `npm run format`                   | Clean `git diff --exit-code` afterwards                                                                              | CI runs this check                                       |

Classify every remaining line of the schema diff:

- **breaking** — `required` additions **at any depth** (top-level or a `dynamicCustomForm`'s `items.required`), removed properties, narrowed `enum`/`pattern`, tightened `type`
- **mechanical** — `connectionMode` added to properties, new properties for genuinely new fields
- **suspicious** — anything else

**Report the classified diff to the user and get explicit confirmation before finishing.** Say plainly which changes the migration _caused_ and which it merely _inherited and had to fix_ — the second kind is scope the user did not ask for, with customer-visible validation consequences, and it is their call whether it rides along in this PR or goes in its own. "The schema changed" is not a finding to bury in a summary; name each breaking change and what it does to already-saved destinations. If the schema is unchanged, say that plainly — it is the good outcome and worth stating.

---

### Step 8: Verify in the webapp

For each connected source type (web, android, ios, cloud, warehouse as applicable):

- **Create flow** — only mandatory fields appear; connection mode picker renders; validation fires
- **Edit flow** — sections render in order; SDK group appears on `device`/`hybrid` and vanishes on `cloud`; each `redirect` navigates and saves; conditional fields toggle correctly
- **Round-trip** — open a destination created on the **old** form, confirm every saved value renders, save without changes and diff the resulting config against the original

---

### Step 9: Get design/PM sign-off

The migration is one-way and reaches every workspace using the destination the
moment it merges, and it rewrites labels, grouping and which fields a user sees
at creation. That is a product change, not only a config change. Get a
design/PM review of the labels and grouping before merging, not just a code
review.

---

### Red flags — stop and re-check

- A field moved into Initial setup "because it's important" without checking the `required` delta
- `npm run update:schema:destination` run and the diff not read
- Generator output filtered from the `Schema diff` banner onward
- A warning waved through as "pre-existing" — on the destination you are migrating, that makes it yours to fix
- A `$delete` in a consent warning read as "the schema has something extra" rather than "the schema is missing it"
- A `mapping` field placed directly in a `baseTemplate` group
- Event-filtering gate copied verbatim from another destination
- Schema diff reported as "regenerated the schema" rather than as a classified list
- `--no-verify` used to get past the pre-commit hook
