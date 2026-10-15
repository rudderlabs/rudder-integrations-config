## What are the changes introduced in this PR?

Write a brief explainer on your code changes.

## What is the related Linear task?

Resolves INT-XXX

## Please explain the objectives of your changes below

Put down any required details on the broader aspect of your changes.

### Runtime dependency

Runtime dependency: none / `<repo>#<PR>`, released in `vX.Y.Z`, rolled out ☐

Config changes that depend on transformer, rudder-server, integrations-info, rudder-auth, webapp, or another runtime must not merge until the dependency is fully rolled out to production in every region. Apply the `blocked: dependency-rollout` label until rollout is complete.

### Any changes to existing capabilities/behaviour, mention the reason & what are the changes ?

N/A

### Any new dependencies introduced with this change?

N/A

### Any new checks got introduced or modified in test suites. Please explain the changes.

N/A

<hr>

### Developer checklist

- [ ] My code follows the style guidelines of this project

- [ ] **No breaking changes are being introduced.**

- [ ] All related docs linked with the PR?

- [ ] All changes manually tested?

- [ ] Any documentation changes needed with this change?

- [ ] I have executed schemaGenerator tests and updated schema if needed

- [ ] Are sensitive fields marked as secret in definition config?

- [ ] My test cases and placeholders use only masked/sample values for sensitive fields

- [ ] Is the PR limited to 10 file changes & one task?

### Reviewer checklist

- [ ] Is the type of change in the PR title appropriate as per the changes?

- [ ] Verified that there are no credentials or confidential data exposed with the changes.
