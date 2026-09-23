---
name: migrate-to-accounts-framework
description: Migrate a destination to the RudderStack accounts framework by adding account definitions and updating destination config, schema, UI config, and validation tests
argument-hint: <destination-name> (e.g. "amplitude" or "mixpanel")
---

## Migrate Destination to Accounts Framework

**Reference files — read all before starting:**

- [`CONVENTIONS.md`](../../../CONVENTIONS.md) — repo-wide rules. [Account definition naming](../../../CONVENTIONS.md#accountdefinition-naming-accountdefinitionname), [where account credential fields live](../../../CONVENTIONS.md#where-account-credential-fields-live), and [string `pattern` / `regex`](../../../CONVENTIONS.md#string-pattern-and-regex) all apply here. Where an existing account definition and `CONVENTIONS.md` disagree, **`CONVENTIONS.md` is current** — most files predate it, so copy the shape of a neighbour but take the rules from there.
- `src/schemas/account/account-db-config-schema.json` — structure and field semantics for the account `db-config.json`
- `src/schemas/account/account-schema-schema.json` — structure for the account `schema.json` (`secretSchema` vs `optionsSchema`)
- `src/schemas/account/account-ui-config-schema.json` — structure for the account `ui-config.json`
- All existing account definitions under `src/configurations/destinations/*/accounts/` — read a representative sample for patterns and real examples

---

### Step 1: Gather context

- The destination name is in `$ARGUMENTS`. If not provided, ask the user.
- Read the destination's `db-config.json`, `ui-config.json`, and `schema.json`.
- Identify which fields belong at the account level:
  - **Secret fields** (`secretFields`): credentials stored encrypted — validated by `secretSchema`
  - **Option fields** (`optionFields`): non-secret account-level config — validated by `optionsSchema`
- Derive automatically — do not ask the user:
  - Auth type: infer from the credential fields (see `authenticationType` description in `account-db-config-schema.json`)
  - Account definition name: `DESTINATION_<DEST_NAME_UPPER>_<AUTH_TYPE_UPPER>`
  - Account directory name: lowercase of the above
  - Required/non-required: mirrors the destination's `schema.json` exactly
  - Field labels, placeholders, notes: copy from the destination's `ui-config.json`

**Ask the user only:** which fields should move to the account level (secret credential fields and non-secret option fields).

Do NOT proceed until confirmed.

---

### Step 2: Create the account definition directory and files

Create: `src/configurations/destinations/<destination>/accounts/<account_definition_name>/`

Use the schema files as the source of truth for structure. Use the existing account definitions under `src/configurations/destinations/*/accounts/` as reference for real-world patterns.

- **`db-config.json`** — follow `account-db-config-schema.json`; use `[]` for `optionFields` if there are none
- **`schema.json`** — follow `account-schema-schema.json`; the `required` array in both `secretSchema` and `optionsSchema` must mirror which fields are required in the destination's `schema.json`. **This file is where all account field validation lives** — see below.
- **`ui-config.json`** — follow `account-ui-config-schema.json`; copy labels, placeholders, and notes from the destination's `ui-config.json`. **Rendering metadata only — it takes no `regex`** — see below.

#### Validation goes in `schema.json`, never in the account `ui-config.json`

At the destination level, [CONVENTIONS.md](../../../CONVENTIONS.md#always-give-a-ui-config-field-an-explicit-regex)
tells you to put a `regex` on every ui-config string field and let `schemaGenerator.py` derive the
`schema.json` `pattern` from it. **Account definitions invert this, and nothing warns you.**

- The account ui-config field contract in `account-ui-config-schema.json` is
  `component | label | placeholder | key | secret | optional | note | options | default`. There is
  no `regex`, and none of the account definitions in the tree uses one. Nothing reads such a key,
  and the schema generator does not walk account definitions at all.
- The authoritative validation is the account `schema.json`. `account-schema-schema.json` makes
  `type` + `pattern` **required** on every `secretSchema` property, so a secret field cannot be
  declared without one. `optionsSchema` properties are not held to that by the meta-schema — give
  them a `pattern` anyway; an option field with none is validated against nothing on save.
- Attach an `errorMessage` next to the `pattern` for anything a customer can plausibly get wrong.
  Neither sub-schema restricts additional keys, so `ajv-errors` `errorMessage` passes validation,
  and it is the only way the customer sees a readable reason instead of a raw schema failure. It
  is the account-level counterpart of
  [`regexErrorMessage`](../../../CONVENTIONS.md#pair-every-regex-with-a-regexerrormessage).

> **Do not take the pattern from the meta-schema's own description.** The `secretSchema.properties`
> description in `account-schema-schema.json` suggests `(^\{\{.*\|\|(.*)\}\}$)|^(.{1,500})$` for
> required fields and `(^\{\{.*\|\|(.*)\}\}$)|^(.{0,200})$` for optional ones. Both carry the
> deprecated `{{ }}` / `env.` prefix that
> [CONVENTIONS.md](../../../CONVENTIONS.md#string-pattern-and-regex) rules out for new fields. Take
> the length bound, drop the alternation: `^.{1,500}$` and `^(.{0,200})$`.

Encode length bounds in the `pattern` itself — never add a sibling `maxLength`. `^(?=.{1,200}$).*\S.*$`
is the idiom for "at most 200 characters and not all whitespace". Full reasoning:
[CONVENTIONS.md — keep the expression to what the value is](../../../CONVENTIONS.md#keep-the-expression-to-what-the-value-is).

#### URL-valued account fields

A field holding a delivery endpoint reuses the shared expression rather than inventing one. Copy it
from **`src/configurations/destinations/http/schema.json`** (`apiUrl`) — that is the clean copy,
matching scheme, DNS-style host, optional port, and optional path, and rejecting the `localhost` and
`ngrok` host classes:

```text
^(https?://)(?![a-zA-Z0-9-]*\.ngrok\.io)(?!localhost|.*\.localhost)([a-zA-Z0-9-]{1,63}\.)+[a-zA-Z]{2,}(:(6553[0-5]|655[0-2][0-9]|65[0-4][0-9]{2}|6[0-4][0-9]{3}|[1-5]\d{4}|[1-9]\d{1,3}))?(/.*)?$
```

`webhook`'s `webhookUrl` is the same expression but prefixed with the deprecated `{{ }}` / `env.`
alternation — if you copy from there, strip the prefix.

**Vary only the trailing path group** for an integration-specific restriction, and leave the rest
byte-identical so a reviewer can diff the two at a glance. To reject a query string or fragment —
appropriate when the partner expects a base URL that the transformer appends its own parameters to —
change `(/.*)?$` to `(/[^?#\s]*)?$` and say so in the `errorMessage`.

**Where the boundary is.** A JSON Schema pattern is a syntactic check on a stored string. It cannot
resolve DNS, so it cannot stop a name that resolves to a link-local or private address, and it has
no view of redirects, DNS rebinding, or egress. Those are runtime concerns owned by the
transformer/delivery layer — **do not try to encode them here**, and do not widen the host lookaheads
in pursuit of them. The host-class lookaheads above are there to catch obvious misconfiguration, not
to serve as an SSRF control.

---

### Step 3: Update the destination's `db-config.json`

Add `supportedAccountDefinitions` and prepend `rudderAccountId` to `destConfig.defaultConfig`:

```json
"supportedAccountDefinitions": {
  "rudderAccountId": ["<ACCOUNT_DEFINITION_NAME>"]
}
```

```json
"destConfig": {
  "defaultConfig": ["rudderAccountId", "<existing fields...>"]
}
```

**The account fields themselves stay declared here too.** Moving a field to the account level does
not remove it from destination metadata — the account owns its _definition_, the destination still
declares it:

- every `secretFields` + `optionFields` entry from the account `db-config.json` → `config.destConfig.defaultConfig`
- every `secretFields` entry → also `config.secretKeys`
- device mode only: any account field the browser SDK needs → also `config.includeKeys`, but never `rudderAccountId`

What each of these does, what breaks when one is missed, and why the validator takes no
exemptions: [CONVENTIONS.md — where account credential fields live](../../../CONVENTIONS.md#where-account-credential-fields-live).
Step 7 verifies them.

---

### Step 4: Update the destination's `ui-config.json`

Add `accountManagementInput` as the **first** field in the group containing the auth fields:

```json
{
  "type": "accountManagementInput",
  "label": "Event delivery account",
  "configKey": "rudderAccountId"
}
```

---

### Step 5: Update the destination's `schema.json`

`rudderAccountId` is the only account-related key the destination schema declares — the credential
fields get no `properties` entry here. This is the one place they are _not_ mirrored; Step 3 has
the rest.

The `oneOf` in **(b)** below exists because a _migration_ must keep configs valid that still carry
the legacy destination-level auth fields. A net-new account-backed destination has no legacy
fields: it declares `rudderAccountId` and no `oneOf` at all.

**a)** Add `rudderAccountId` to `properties`:

```json
"rudderAccountId": {
  "type": "string",
  "pattern": "^.{1,100}$"
}
```

**b)** Keep existing non-auth required fields unchanged. Remove only the migrated auth fields from the top-level `required` array, then add a `oneOf` mutual-exclusivity constraint (place before `allOf` if present). If multiple auth fields are being migrated as a group, include all of them together in each branch:

```json
"oneOf": [
  {
    "required": ["<authField1>", "<authField2>"],
    "not": { "required": ["rudderAccountId"] }
  },
  {
    "required": ["rudderAccountId"],
    "not": { "required": ["<authField1>", "<authField2>"] }
  }
]
```

For a single auth field, use `["<authField>"]` instead of the array above.

---

### Step 6: Update validation tests

Append three test cases to `test/data/validation/destinations/<destination>.json` using the minimal valid config as the base:

```json
{
  "testTitle": "Valid config with only rudderAccountId (no <authField>)",
  "config": { "rudderAccountId": "acc123", "<other required fields>": "<values>" },
  "result": true
},
{
  "testTitle": "Invalid config with both <authField> and rudderAccountId present",
  "config": { "<authField>": "<value>", "rudderAccountId": "acc123", "<other required fields>": "<values>" },
  "result": false,
  "err": [
    " must NOT be valid",
    " must NOT be valid",
    " must match exactly one schema in oneOf"
  ]
},
{
  "testTitle": "Invalid config with neither <authField> nor rudderAccountId",
  "config": { "<other required fields>": "<values>" },
  "result": false,
  "err": [
    " must have required property '<authField>'",
    " must have required property 'rudderAccountId'",
    " must match exactly one schema in oneOf"
  ]
}
```

Error strings must match AJV output exactly.

---

### Step 7: Verify

```bash
npm test -- --testPathPattern="<destination>"
python3 scripts/validate_account_definitions.py <destination>
```

The second command checks the Step 3 declarations. CI runs it too — a migration always touches
`db-config.json`, which is what triggers it — but no npm script or hook does, so run it before you
push rather than finding out from a red build. Fix any failures in the definition files, never by
exempting the destination in the validator.

---
