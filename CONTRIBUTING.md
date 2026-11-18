# Contributing to Rudder-Integrations-Config

Thanks for taking the time and for your help in improving this project!

## Table of contents

- [**RudderStack Contributor Agreement**](#rudderstack-contributor-agreement)
- [**Before you start**](#before-you-start)
- [**Adding a new destination**](#adding-a-new-destination)
- [**Verify before opening a pull request**](#verify-before-opening-a-pull-request)
- [**Merge and release policy**](#merge-and-release-policy)
- [**Source and destination visibility gating**](#source-and-destination-visibility-gating)
- [**Getting help**](#getting-help)

## RudderStack Contributor Agreement

To contribute to this project, we need you to sign the [**Contributor License Agreement ("CLA")**][CLA] for the first commit you make. By agreeing to the [**CLA**][CLA], we can add you to list of approved contributors and review the changes proposed by you.

## Before you start

This repository holds the integration _definitions_: the JSON that describes each source, destination and account to the RudderStack dashboard and the SDKs. A new integration usually also needs transformer code; see the [rudder-transformer contributing guide][transformer-contributing] for that half.

- **Read [`CONVENTIONS.md`](/CONVENTIONS.md) first.** It is the single source of truth for naming and structure, for example the `SCREAMING_SNAKE_CASE` `{CATEGORY}_{TYPE}[_{AUTH_QUALIFIER}]` pattern for `accountDefinitionName`. Where an existing file and `CONVENTIONS.md` disagree, `CONVENTIONS.md` is current.
- **Don't copy an existing destination as a template.** Nearly every definition in the tree predates the current conventions, so copying one reproduces deprecated patterns, most often in [string `pattern` and `regex`](/CONVENTIONS.md#string-pattern-and-regex). Copy the _shape_ of a neighbouring destination; take the rules from `CONVENTIONS.md`.
- **Use the repo's skills** in [`.claude/skills/`](/.claude/skills/). AI coding agents such as Claude Code load them automatically; point other agents at them, or read them yourself.

| Task                                               | Skill                                    |
| -------------------------------------------------- | ---------------------------------------- |
| New cloud / device / hybrid / warehouse definition | `bootstrap-new-destination`              |
| New Visual Data Mapper destination                 | `vdm-next-integration`                   |
| Move a destination onto the accounts framework     | `migrate-to-accounts-framework`          |
| Move a destination onto form builder v2            | `migrate-destination-to-form-builder-v2` |

## Adding a new destination

The [`bootstrap-new-destination`](/.claude/skills/bootstrap-new-destination/SKILL.md) skill walks through every step below. A new destination is:

- **A folder `src/configurations/destinations/<dir>/`** with three files:
  - `db-config.json`, started from [`scripts/template-db-config.json`](/scripts/template-db-config.json). For a destination built on the transformer's batching framework, keep the template's `transformAtV1: "router"`.
  - `ui-config.json`, started from [`scripts/template-ui-config.json`](/scripts/template-ui-config.json). Give every text input field an explicit `regex`.
  - `schema.json`, written by hand so that its `required` and `properties` mirror the ui-config fields. Keep it in step with `ui-config.json` whenever you change a field; `npm run check:schema:destination <dir>` reports drift, except for event mapping fields (`redirectGroups`), whose schema the generator never produces — see [the schema entry is hand-maintained](/CONVENTIONS.md#the-schema-entry-is-hand-maintained).
- **Validation test data** in `test/data/validation/destinations/<dir>.json`.
- **An icon**, referenced by `options.icon` in `db-config.json`. Icons live in the `@rudderlabs/icons` package; if yours doesn't exist yet, share the SVG with the RudderStack team in your pull request.

## Verify before opening a pull request

```bash
npm run check:schema:destination <dir>   # generated schema matches ui-config (no `--`)
npx jest test/validation.test.ts         # definition + validation test data
npm run format                           # prettier; CI runs `git diff --exit-code` after
```

A destination with an `accounts/` directory has one more check, which CI runs; see [where account credential fields live](/CONVENTIONS.md#where-account-credential-fields-live).

## Merge and release policy

This repository uses a single `main` trunk. Every pull request targets `main`, uses a conventional-commit title, and is squash-merged. `main` must remain releasable because every merged change is included in the next release-please release PR.

### Runtime dependencies

A configuration pull request that depends on transformer, rudder-server, integrations-info, rudder-auth, webapp, or another runtime change must wait until that dependency is fully rolled out to production in every region—not merely merged or released. Record the repository, pull request, release version, and rollout status in the pull request template, and apply the `blocked: dependency-rollout` label until rollout is complete.

### Breaking changes

Prefer additive, backward-compatible changes: new fields are optional, have safe defaults, and are ignored by older consumers. Renames and removals use two releases: first add the new field while consumers accept both, then remove the old field only after those consumers are fully deployed. Incompatible definition shapes must use a new versioned definition, following patterns such as `ga4_v2` and `intercom_v2`, rather than mutating the live definition.

### Releases

release-please maintains a standing `chore: release X.Y.Z` pull request. Before merging it, review the CHANGELOG diff and confirm that every runtime dependency is fully rolled out. If an entry is not safe to ship, revert that change on `main` with a `revert:` commit rather than holding the release train. Merging the release pull request creates the version tag and GitHub Release and deploys that tag to production; treat it as a production deployment.

Hotfixes follow the same path: merge an ordinary `fix:` pull request to `main`, then merge the updated release pull request.

For rollback, dispatch the rollback workflow from the known-good `vX.Y.Z` tag (or from `main` when explicitly intended).

## Source and destination visibility gating

Use `options.hidden` in source and destination `db-config.json` files for catalog hiding. It supports two states:

- `hidden: true` for blanket hiding from all customers.
- `hidden.gate` for hide-when gating by one or more Flagsmith flags or billing features.

Use `hidden.gate` when beta or GA access depends on a Flagsmith flag, a billing feature, or both:

```json
{
  "options": {
    "hidden": {
      "gate": {
        "flags": [
          { "name": "AMP_EXAMPLE_BETA_FLAG", "value": false },
          { "name": "example_billing_feature", "value": false }
        ],
        "condition": "and"
      }
    }
  }
}
```

The gate uses hide-when semantics: the integration is hidden when the flag reduction matches the configured values. Author beta gates with the exact Flagsmith flag name, including the `AMP_` prefix. Author GA billing features as the exact feature name resolved by the webapp. Every flag item must include a boolean `value`.

For a single flag, `condition` is optional. For two or more flags, set `condition` to `"and"` or `"or"`. The beta-to-GA transition shape is usually `value: false` on both the beta flag and the billing feature with `condition: "and"`, so the integration is hidden only when neither gate grants access.

Beta-to-GA lifecycle:

- During beta, use `hidden.gate` with the beta Flagsmith flag.
- **At GA, remove the `options.hidden` block entirely** — this is the default. An integration that everyone on any plan can use should carry no gate at all.
- Only if GA access is genuinely **plan-gated** should `hidden.gate` move to the billing feature (or combine the beta flag and the billing feature with an explicit `condition` during the transition). Don't reach for a billing feature just because the integration is leaving beta.
- Keep `hidden: true` only for blanket hiding from all customers.

## Getting help

For any questions, concerns, or queries, open an [issue][issue] or ask in our [**Slack**](https://rudderstack.com/join-rudderstack-slack-community/) community. You can also contribute to any open-source RudderStack project; see our [**GitHub page**](https://github.com/rudderlabs).

<!----variables---->

[issue]: https://github.com/rudderlabs/rudder-integrations-config/issues/new
[CLA]: https://contributor.rudderlabs.com/
[transformer-contributing]: https://github.com/rudderlabs/rudder-transformer/blob/develop/CONTRIBUTING.md
