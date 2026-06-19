#!/usr/bin/env python3
import json
import os
import sys
import jsondiff
import argparse
import re
from constants import CONFIG_DIR
from utils import (
    get_all_config_definitions,
    get_file_content,
    update_config_definition,
    create_config_definition,
    initialize_debug_log,
    normalize_nullable_column_deletions,
)

ALL_SELECTORS = ["destination", "source"]
# Definitions to skip when deploying to production. Compared against the
# directory name upper-cased (which equals the definition `name`). Test
# destinations are served only on non-prod environments and must never reach
# production.
BLACK_LIST_DESTINATIONS = ["TEST_DESTINATION"]
# The deploy target environment is supplied by the `--environment` CLI flag (the
# GitHub workflow passes its DEPLOY_ENV value through to it). Production is the
# only environment that skips the black-listed definitions above; on any other
# environment they deploy normally.
PRODUCTION_ENVIRONMENT = "production"
# Accepted deploy environments. `--environment` is required and must match one
# of these exactly (no normalization), so a missing or misspelled value fails
# loudly instead of silently bypassing the production skip above.
VALID_ENVIRONMENTS = ("development", "staging", "production")
# Top-level fields that map to nullable DB columns. Keep in sync with the DDL
# for `destination_definitions` / `source_definitions`. See
# `normalize_nullable_column_deletions` for why this list matters.
NULLABLE_COLUMN_FIELDS = ("options", "uiConfig", "configSchema")
# Allowed lifecycle statuses for archived (non-current) majors in the `versions`
# archive. The current version is the served default, so its status is implicit.
VERSION_ARCHIVE_STATUSES = ("supported", "retired")
# Top-level fields excluded from the destination update diff: changes confined
# to these alone should neither trigger an update nor show up in the diff report.
IGNORED_DESTINATION_DIFF_FIELDS = ("version", "versions")

CONTROL_PLANE_URL = None
USERNAME = None
PASSWORD = None
SELECTORS = []
ITEM_NAME = None
DRY_RUN = True
VERBOSE = False
AUTH = (None, None)
ENVIRONMENT = None


def get_command_line_arguments():
    parser = argparse.ArgumentParser(
        description="Script to deploy definition config files to DB."
    )
    parser.add_argument("control_plane_url", nargs="?", help="Control plane URL")
    parser.add_argument("username", nargs="?", help="Control plane admin username")
    parser.add_argument("password", nargs="?", help="Control plane admin password")
    parser.add_argument(
        "selector",
        nargs="?",
        help="Specify (destination or source) to deploy corresponding definitions.",
        default=None,
    )
    parser.add_argument(
        "item_name", nargs="?", help="Specific item name to update.", default=None
    )
    parser.add_argument(
        "--dry-run",
        dest="dry_run",
        action="store_true",
        help="Show what would be changed without making actual changes to the database",
        default=True,
    )
    parser.add_argument(
        "--no-dry-run",
        dest="dry_run",
        action="store_false",
        help="Make actual changes to the database",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed JSON reports in addition to summary",
        default=False,
    )
    parser.add_argument(
        "--environment",
        help="Target deploy environment (e.g. development, staging, production). Black-listed definitions are skipped only on production.",
        default=None,
    )

    args = parser.parse_args()

    control_plane_url = args.control_plane_url or os.getenv("CONTROL_PLANE_URL")
    username = args.username or os.getenv("API_USER")
    password = args.password or os.getenv("API_PASSWORD")
    selector = args.selector or os.getenv("SELECTOR")
    item_name = args.item_name or os.getenv("ITEM_NAME")
    environment = args.environment

    invalid_args = []

    if control_plane_url is None:
        invalid_args.append(
            "1st positional argument or CONTROL_PLANE_URL environment variable is missing"
        )
    if username is None:
        invalid_args.append(
            "2nd positional argument or API_USER environment variable is missing"
        )
    if password is None:
        invalid_args.append(
            "3rd positional argument or API_PASSWORD environment variable is missing"
        )
    if selector is None:
        SELECTORS = ALL_SELECTORS
    elif selector not in ALL_SELECTORS:
        invalid_args.append(
            "4th positional argument or SELECTOR environment variable is invalid"
        )
    else:
        SELECTORS = [selector]

    if environment not in VALID_ENVIRONMENTS:
        invalid_args.append(
            "--environment is required and must be one of: "
            + ", ".join(VALID_ENVIRONMENTS)
        )

    if invalid_args:
        print("Error: The following arguments or environment variables are invalid:")
        for arg in invalid_args:
            print(arg)
        sys.exit(1)

    return (
        control_plane_url,
        username,
        password,
        SELECTORS,
        item_name,
        args.dry_run,
        args.verbose,
        environment,
    )


def initialize_runtime_config():
    global CONTROL_PLANE_URL, USERNAME, PASSWORD, SELECTORS, ITEM_NAME, DRY_RUN, VERBOSE, AUTH, ENVIRONMENT
    (
        CONTROL_PLANE_URL,
        USERNAME,
        PASSWORD,
        SELECTORS,
        ITEM_NAME,
        DRY_RUN,
        VERBOSE,
        ENVIRONMENT,
    ) = get_command_line_arguments()
    AUTH = (USERNAME, PASSWORD)


#########################
# UTIL METHODS


def is_black_listed(item, environment):
    """A black-listed definition (e.g. the test destination) is skipped only on
    production; on every other environment it deploys normally."""
    return (
        item.upper() in BLACK_LIST_DESTINATIONS
        and environment == PRODUCTION_ENVIRONMENT
    )


def build_versions_archive(directory):
    versions_directory = os.path.join(directory, "versions")
    if not os.path.isdir(versions_directory):
        return {}

    versions_archive = {}
    for major in sorted(
        os.listdir(versions_directory),
        key=lambda name: (0, int(name)) if name.isdigit() else (1, name),
    ):
        major_directory = os.path.join(versions_directory, major)
        if not os.path.isdir(major_directory):
            continue

        if not re.fullmatch(r"[1-9]\d*", major):
            raise ValueError(
                f"Archived version directory name must be a canonical major integer, got '{major}' in {versions_directory}"
            )

        versioned_data = get_file_content(major_directory)

        # On disk, an archived major carries a flat `version` (major.minor string)
        # plus sibling `status`/`retirementDate?`/`migrationDocsUrl?` — the same
        # shape as the root db-config.json. The archive entry the backend persists
        # renames `version` to `number`.
        number = versioned_data.get("version")
        if not isinstance(number, str) or not re.fullmatch(r"\d+\.\d+", number):
            raise ValueError(
                f"Archived version requires a major.minor `version` string in {major_directory}/db-config.json"
            )
        if number.split(".")[0] != major:
            raise ValueError(
                f"Archived `version` ({number}) major does not match directory '{major}' in {major_directory}/db-config.json"
            )

        status = versioned_data.get("status")
        if status not in VERSION_ARCHIVE_STATUSES:
            raise ValueError(
                f"Archived version `status` must be one of {list(VERSION_ARCHIVE_STATUSES)} in {major_directory}/db-config.json"
            )

        entry = {"number": number, "status": status}
        for slice_key in ("config", "configSchema"):
            slice_value = versioned_data.get(slice_key)
            if not isinstance(slice_value, dict):
                raise ValueError(
                    f"Archived version is missing a valid `{slice_key}` object in {major_directory}"
                )
            entry[slice_key] = slice_value

        # `uiConfig` may be an object (current `baseTemplate` form) or an array
        # (legacy form), so accept either rather than forcing a dict.
        ui_config = versioned_data.get("uiConfig")
        if not isinstance(ui_config, (dict, list)):
            raise ValueError(
                f"Archived version is missing a valid `uiConfig` object or array in {major_directory}"
            )
        entry["uiConfig"] = ui_config

        for optional_key in ("retirementDate", "migrationDocsUrl"):
            if optional_key in versioned_data:
                entry[optional_key] = versioned_data[optional_key]

        versions_archive[major] = entry

    return versions_archive


def update_diff_db(
    selector, persisted_by_name, item_name=None, dry_run=False, verbose=False
):
    final_report = []

    ## data sets
    if item_name:
        current_items = [item_name]
    else:
        current_items = os.listdir(f"./{CONFIG_DIR}/{selector}s")

    print(f"Current items: {current_items}")

    for item in current_items:
        # check if item is a directory
        if not os.path.isdir(f"./{CONFIG_DIR}/{selector}s/{item}"):
            print(f"Skipping {item} as it is not a directory")
            continue
        # Skip black-listed definitions (e.g. the test destination) on production.
        if is_black_listed(item, ENVIRONMENT):
            print(
                f"Skipping {item} as it is black-listed for the {ENVIRONMENT} environment"
            )
            continue

        directory = f"./{CONFIG_DIR}/{selector}s/{item}"
        # Track the current operation so a failure can name exactly what broke.
        # Start with the directory name; switch to the definition name once known.
        item_name = item
        operation = "loading config files"
        try:
            updated_data = get_file_content(directory)
            if selector == "destination":
                operation = "building versions archive"
                updated_data["versions"] = build_versions_archive(directory)

            item_name = updated_data["name"]
            persisted_data = persisted_by_name.get(item_name)

            if persisted_data is not None:
                diff = jsondiff.diff(persisted_data, updated_data, marshal=True)
                normalize_nullable_column_deletions(
                    diff, persisted_data, updated_data, NULLABLE_COLUMN_FIELDS
                )

                # Drop version-related fields so changes confined to them don't
                # trigger an update or appear in the reported diff. Destination
                # definitions only.
                if selector == "destination":
                    for ignored_field in IGNORED_DESTINATION_DIFF_FIELDS:
                        diff.pop(ignored_field, None)

                if len(diff.keys()) > 0:  # changes exist
                    operation = "updating definition"
                    status, _ = update_config_definition(
                        CONTROL_PLANE_URL,
                        selector,
                        item_name,
                        updated_data,
                        auth=AUTH,
                        dry_run=dry_run,
                        verbose=verbose,
                    )
                    final_report.append(
                        {
                            "name": item_name,
                            "action": "update",
                            "status": status,
                            "diff": diff if dry_run else None,
                        }
                    )
                else:
                    final_report.append(
                        {
                            "name": item_name,
                            "action": "N/A",
                            "status": "No changes detected",
                        }
                    )

            else:
                operation = "creating definition"
                status, _ = create_config_definition(
                    CONTROL_PLANE_URL,
                    selector,
                    updated_data,
                    AUTH,
                    dry_run=dry_run,
                    verbose=verbose,
                )
                final_report.append(
                    {
                        "name": item_name,
                        "action": "create",
                        "status": status,
                        "data": updated_data if dry_run else None,
                    }
                )
        except Exception as error:
            print(f"❌ {item_name}: failed while {operation} — {error}")
            final_report.append(
                {
                    "name": item_name,
                    "action": "failed",
                    "status": f"Failed while {operation}: {error}",
                }
            )

    return final_report


def get_formatted_json(data):
    return json.dumps(data, indent=2)


def get_stale_data(persisted_store, report):
    stale_config_report = []
    persisted_items = [item["name"] for item in persisted_store]
    file_items = [item["name"] for item in report]

    for item in persisted_items:
        if item not in file_items:
            stale_config_report.append(item)

    return stale_config_report


def log_execution_plan():
    """Log detailed execution plan showing what would happen in normal mode"""
    print("=" * 70)
    print("EXECUTION PLAN")
    print("=" * 70)
    print(f"Control Plane URL: {CONTROL_PLANE_URL}")
    print(f"Environment: {ENVIRONMENT}")
    print(f"Username: {USERNAME}")
    print(f"Password: {'*' * len(PASSWORD)}")
    print(f"Selectors to process: {', '.join(SELECTORS)}")
    if ITEM_NAME:
        print(f"Specific item: {ITEM_NAME}")
    else:
        print("Processing: ALL items in selected categories")

    print("\nWhat would happen in NORMAL mode:")
    print("1. Connect to the control plane database")
    print("2. For each selector (destination/source):")
    print("   - Scan local configuration directories")
    print("   - For each configuration found:")
    print("     a) Fetch existing configuration from database")
    print("     b) Compare local vs remote configurations")
    print("     c) If differences found: UPDATE the database record")
    print("     d) If not found in database: CREATE new database record")
    print("3. Generate stale data report (items in DB but not in files)")
    print("4. All changes would be PERMANENTLY applied to the database")

    if DRY_RUN:
        print("\nDRY RUN MODE ACTIVE:")
        print("- Read-only API calls will be made to compute the diff")
        print("- NO write operations will be performed")
        print("- Reports will show what WOULD be changed")

    if VERBOSE:
        print("\nVERBOSE MODE ACTIVE:")
        print("- All API requests and responses will be logged to debug.log file")
        print("- Request details include: method, URL, headers, auth, body")
        print("- Response details include: status, headers, body")
        print("- Console output will remain clean (debug logs only in file)")

    print("=" * 70)


def is_failed(item):
    """Check if a report item represents a failed operation."""
    if item.get("action") == "failed":
        return True
    status = item.get("status")
    if isinstance(status, int):
        return status < 200 or status > 300
    return False


def print_summary(selector, final_report, dry_run=False):
    print("\n")
    print("#" * 50)
    if dry_run:
        print(f"{selector.capitalize()} Summary - What Would Happen")
    else:
        print(f"{selector.capitalize()} Summary - What Happened")
    print("#" * 50)

    failures = [item for item in final_report if is_failed(item)]
    failed_names = {item["name"] for item in failures}
    creates = [
        item
        for item in final_report
        if "create" in item["action"] and item["name"] not in failed_names
    ]
    updates = [
        item
        for item in final_report
        if "update" in item["action"] and item["name"] not in failed_names
    ]
    no_changes = [item for item in final_report if item["action"] == "N/A"]

    print(f"📊 Total configurations processed: {len(final_report)}")
    if dry_run:
        print(f"🆕 Would CREATE: {len(creates)} new records")
        print(f"🔄 Would UPDATE: {len(updates)} existing records")
        print(f"✅ No changes needed: {len(no_changes)} records")
    else:
        print(f"🆕 CREATED: {len(creates)} new records")
        print(f"🔄 UPDATED: {len(updates)} existing records")
        print(f"✅ No changes needed: {len(no_changes)} records")
        if failures:
            print(f"❌ FAILED: {len(failures)} records")

    if failures:
        print(f"\n❌ Records that FAILED:")
        for item in failures:
            print(
                f"   - {item['name']} (action={item['action']}, status={item['status']})"
            )

    if creates:
        if dry_run:
            print(f"\n🆕 New records that would be CREATED:")
        else:
            print(f"\n🆕 New records that were CREATED:")
        for item in creates:
            config_size = item.get("config_size", len(str(item.get("data", ""))))
            print(f"   - {item['name']} ({config_size} chars)")

    if updates:
        if dry_run:
            print(f"\n🔄 Records that would be UPDATED:")
        else:
            print(f"\n🔄 Records that were UPDATED:")
        for item in updates:
            print(f"   - {item['name']}")

    if dry_run:
        print(f"\n⚠️  In normal mode, these changes would be PERMANENT!")
        print(f"🌐 Database: {CONTROL_PLANE_URL}")
        print(f"👤 User: {USERNAME}")
        print(f"🔍 To run this script in normal mode, use the --no-dry-run flag")
    else:
        if failures:
            print(f"\n❌ Some changes failed! Review the errors above.")
        else:
            print(f"\n✅ All changes have been applied to the database!")
        print(f"🌐 Database: {CONTROL_PLANE_URL}")
        print(f"👤 User: {USERNAME}")
    print("#" * 50)


if __name__ == "__main__":
    initialize_runtime_config()

    # Initialize debug logging if verbose mode is enabled
    if VERBOSE:
        initialize_debug_log()

    # Log execution plan first
    log_execution_plan()

    if DRY_RUN:
        print("\n" + "=" * 60)
        print("DRY RUN MODE - No changes will be made to the database")
        print("=" * 60)

    has_failures = False

    for selector in SELECTORS:
        print("\n")
        print("#" * 50)
        mode_text = " (DRY RUN)" if DRY_RUN else ""
        print(
            "Running {} Definitions Updates{}".format(selector.capitalize(), mode_text)
        )

        # Single batch API call to fetch all definitions for this selector
        try:
            persisted_store = get_all_config_definitions(
                CONTROL_PLANE_URL, selector, AUTH, VERBOSE
            )
        except Exception as error:
            print(
                f"\n❌ Failed to fetch existing {selector} definitions from "
                f"{CONTROL_PLANE_URL} — {error}"
            )
            print(
                "   Check that the control plane URL is reachable and the "
                "credentials are valid, then retry."
            )
            sys.exit(1)
        persisted_by_name = {item["name"]: item for item in persisted_store}

        final_report = update_diff_db(
            selector, persisted_by_name, ITEM_NAME, DRY_RUN, VERBOSE
        )

        # Always show summary first (most important for users)
        print_summary(selector, final_report, DRY_RUN)
        has_failures = has_failures or any(is_failed(item) for item in final_report)

        # Show detailed reports only when verbose flag is used (write to deploy-debug.log)
        if VERBOSE:
            changed_items = [
                item
                for item in final_report
                if item["action"] != "N/A"
                and item.get("status") != "No changes detected"
            ]
            try:
                with open("deploy-debug.log", "a", encoding="utf-8") as f:
                    f.write(f"\n{'='*50}\n")
                    f.write(
                        f"{selector.capitalize()} Definition Update Report{mode_text}\n"
                    )
                    f.write(f"{'='*50}\n")
                    f.write(get_formatted_json(changed_items) + "\n\n")

                    f.write(f"\n{'='*50}\n")
                    f.write(f"Stale {selector.capitalize()}s Report\n")
                    f.write(f"{'='*50}\n")
                    f.write(
                        get_formatted_json(
                            get_stale_data(persisted_store, final_report)
                        )
                        + "\n\n"
                    )
            except Exception as e:
                print(
                    f"Warning: Could not write verbose reports to deploy-debug.log: {e}"
                )

    # Show debug log location if verbose mode was used
    if VERBOSE:
        print(f"\n📝 Debug logs have been written to: debug.log")
        print(f"💡 Review this file for detailed API request/response information")

    sys.exit(1 if has_failures else 0)
