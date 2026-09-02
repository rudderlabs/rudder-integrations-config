# Working in this repository

This repo holds **configuration definitions** — the JSON that describes each source, destination,
and account to config-backend, rudder-webapp, and the SDKs. There is no runtime code here. A
mistake in a definition surfaces as a customer being unable to save a destination, or as an SDK
initialising without a credential and silently dropping events.

## Read `CONVENTIONS.md` first

[`CONVENTIONS.md`](CONVENTIONS.md) is the authoritative set of naming and structural rules and is
the single source of truth. Where an existing file and `CONVENTIONS.md` disagree,
**`CONVENTIONS.md` is current** — most of the tree predates it. Do not restate its rules here or
in a skill; link to the section.

Read it before adding or editing a destination, source, or account definition, even for a change
that looks like a one-liner. It is short.

## The failure mode this repo actually has

**Copying an existing destination reproduces deprecated patterns.** Nearly every definition in the
tree predates the current conventions, so whichever file you open as a model will usually carry
something the conventions now forbid — most often the deprecated
`(^\{\{.*\|\|(.*)\}\}$)|(^env[.].+)|` regex prefix, carried by all but nine destination schemas.

Copy the _shape_ of a neighbouring destination. Take the individual rules from `CONVENTIONS.md`.

## Skills

Invoke the matching skill before starting; each one links the relevant `CONVENTIONS.md` sections.

| Task                                               | Skill                           |
| -------------------------------------------------- | ------------------------------- |
| New cloud / device / hybrid / warehouse definition | `bootstrap-new-destination`     |
| New Visual Data Mapper destination                 | `vdm-next-integration`          |
| Move a destination onto the accounts framework     | `migrate-to-accounts-framework` |

## Shared scripts are repo-wide contracts

`scripts/schemaGenerator.py` and the `scripts/validate_*.py` validators apply to every destination
in the tree. When one of them rejects your definition or won't generate the shape you expected,
**the definition is what's wrong** — fix it there.

Do not add a per-destination branch, exemption list, or special case to a shared script to get a
single destination through. If a rule genuinely needs to change for everyone, that is its own
change with its own reasoning, not a side effect of adding a destination.

## Verify before finishing

```bash
npm run check:schema:destination <dir>   # generated schema matches ui-config (no `--`)
npx jest test/validation.test.ts         # definition + validation test data
npm run format                           # prettier; CI runs `git diff --exit-code` after
```

`npx jest -d <dir>` does not filter — the whole suite runs (~10s). That is expected.

For a destination with an `accounts/` directory, also run the account coverage check, which no
workflow runs for you:

```bash
python3 scripts/validate_account_definitions.py <dir>
```
