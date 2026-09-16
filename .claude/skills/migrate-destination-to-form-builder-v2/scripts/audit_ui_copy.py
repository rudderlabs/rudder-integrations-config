#!/usr/bin/env python3
"""Flag missing user-facing copy in a v2 ui-config.json.

Usage (from the repo root):
    python3 .claude/skills/migrate-destination-to-form-builder-v2/scripts/audit_ui_copy.py <dest>

Reports:
  - any textInput with a `regex` but no `regexErrorMessage` (every template, every depth)
  - any tagInput carrying a `regexErrorMessage` (the v2 TagInput never renders it)
  - a `regexErrorMessage` breaking the wording rules: technical, not actionable,
    blaming/apologising, over 8 words, trailing full stop, not sentence case
  - any input field with no `note` (baseTemplate, sdkTemplate, redirectGroups, rowFields)
  - any collapsible, or baseTemplate group holding non-redirect fields, with no `note`

Exempt: `accountManagementInput`, `mapping` columns (the column label is the copy), references inside
`preRequisites`, and the standard consent block copied from
scripts/template-ui-config.json. Exits 1 when anything is reported.
"""
import json
import re
import sys

# Heuristics for customer-facing regexErrorMessage copy (CONVENTIONS.md,
# "Pair every regex with a regexErrorMessage"). They catch the common failures;
# a clean result still needs a human read.
MAX_WORDS = 8
TECHNICAL = re.compile(
    r"[\\^$]|\{\d|\[[^\]]*-[^\]]*\]|\b(regex|regexp|pattern|jsonpath|wildcard|matches?|configKey|null|undefined)\b",
    re.I,
)
NOT_ACTIONABLE = re.compile(r"\b(invalid|wrong|incorrect|bad|error|failed)\b", re.I)
BLAME_OR_APOLOGY = re.compile(
    r"\b(sorry|apolog\w*|you entered|you typed|you have|your input)\b", re.I
)


def message_problems(msg):
    """Wording problems in one regexErrorMessage, per CONVENTIONS.md."""
    problems = []
    if TECHNICAL.search(msg):
        problems.append("uses technical terms")
    if NOT_ACTIONABLE.search(msg):
        problems.append("says what went wrong instead of what to do")
    if BLAME_OR_APOLOGY.search(msg):
        problems.append("blames the user, apologises or repeats their input")
    if len(msg.split()) > MAX_WORDS:
        problems.append(f"over {MAX_WORDS} words")
    if msg.rstrip().endswith("."):
        problems.append("ends with a full stop")
    if msg[:1] != msg[:1].upper():
        problems.append("not sentence case")
    return problems


def audit(ui):
    out = []

    def walk(node, path):
        if isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{path}[{i}]")
            return
        if not isinstance(node, dict):
            return

        key = node.get("configKey")
        in_columns = "/columns[" in path
        in_consent = path.startswith("/consentSettingsTemplate")

        if node.get("type") == "tagInput":
            if "regexErrorMessage" in node:
                out.append(
                    f"tagInput never shows regexErrorMessage, remove it  {path}  ({key})"
                )
        elif "regex" in node and "regexErrorMessage" not in node:
            out.append(f"regex without regexErrorMessage  {path}  ({key})")
        msg = node.get("regexErrorMessage")
        if isinstance(msg, str) and node.get("type") != "tagInput":
            problems = message_problems(msg)
            if problems:
                out.append(
                    f"regexErrorMessage {', '.join(problems)}  {path}  ({key}): {msg}"
                )
        if (
            key
            and node.get("type") not in ("redirect", "accountManagementInput")
            and not node.get("note")
            and not in_columns
            and not in_consent
        ):
            out.append(f"field without note                {path}  ({key})")
        if "sections" in node and not node.get("note"):
            out.append(
                f'collapsible without note          {path}  "{node.get("title")}"'
            )
        if (
            path.startswith("/baseTemplate")
            and node.get("title")
            and node.get("fields")
            and any(f.get("type") != "redirect" for f in node["fields"])
            and not node.get("note")
        ):
            out.append(f'group without note                {path}  "{node["title"]}"')

        for k, v in node.items():
            if k != "preRequisites":
                walk(v, f"{path}/{k}")

    walk(ui, "")
    return out


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    dest = sys.argv[1]
    path = f"src/configurations/destinations/{dest}/ui-config.json"
    ui = json.load(open(path))["uiConfig"]
    if isinstance(ui, list):
        sys.exit(f"{path} is still the legacy array format")
    problems = audit(ui)
    print("\n".join(problems) if problems else "clean")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
