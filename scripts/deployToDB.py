#!/usr/bin/env python3
import requests
import json
import os
import sys
import jsondiff
import argparse
from constants import CONFIG_DIR, REQUEST_TIMEOUT
from utils import (
    get_config_definition,
    get_file_content,
    update_config_definition,
    create_config_definition,
    initialize_debug_log,
)

ALL_SELECTORS = ["destination", "source"]
BLACK_LIST_DESTINATIONS = ["RUDDER_TEST"]


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

    args = parser.parse_args()

    control_plane_url = args.control_plane_url or os.getenv("CONTROL_PLANE_URL")
    username = args.username or os.getenv("API_USER")
    password = args.password or os.getenv("API_PASSWORD")
    selector = args.selector or os.getenv("SELECTOR")
    item_name = args.item_name or os.getenv("ITEM_NAME")

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
    )


CONTROL_PLANE_URL, USERNAME, PASSWORD, SELECTORS, ITEM_NAME, DRY_RUN, VERBOSE = (
    get_command_line_arguments()
)

# CONSTANTS
AUTH = (USERNAME, PASSWORD)
#########################


#########################
# UTIL METHODS


def get_persisted_store(base_url, selector, verbose=False):
    response = get_config_definition(base_url, selector, auth=AUTH, verbose=verbose)
    return json.loads(response.text)


def update_diff_db(selector, item_name=None, dry_run=False, verbose=False):
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
        # check if item is in black list
        if (
            item.upper() in BLACK_LIST_DESTINATIONS
            and CONTROL_PLANE_URL == "https://api.rudderstack.com"
        ):
            print(f"Skipping {item} as it is in black list")
            continue

        directory = f"./{CONFIG_DIR}/{selector}s/{item}"
        updated_data = get_file_content(directory)

        persisted_data = get_config_definition(
            CONTROL_PLANE_URL, selector, updated_data["name"], AUTH, verbose=verbose
        )

        if persisted_data.status_code == 200:
            diff = jsondiff.diff(
                json.loads(persisted_data.text), updated_data, marshal=True
            )
            # ignore the $delete - values present in DB but missing in files. Anyways this doesn't get reflected in DB as keys are missing in files itself.
            # Best practice is to make sure all keys are maintained in the config files irrespective of them being null.
            diff.pop("$delete", None)

            if len(diff.keys()) > 0:  # changes exist
                status, _ = update_config_definition(
                    CONTROL_PLANE_URL,
                    selector,
                    updated_data["name"],
                    updated_data,
                    auth=AUTH,
                    dry_run=dry_run,
                    verbose=verbose,
                )
                action = "update"
                final_report.append(
                    {
                        "name": updated_data["name"],
                        "action": action,
                        "status": status,
                        "diff": diff if dry_run else None,
                    }
                )
            else:
                final_report.append(
                    {
                        "name": updated_data["name"],
                        "action": "N/A",
                        "status": "No changes detected",
                    }
                )

        else:
            status, _ = create_config_definition(
                CONTROL_PLANE_URL,
                selector,
                updated_data,
                AUTH,
                dry_run=dry_run,
                verbose=verbose,
            )
            action = "create"
            final_report.append(
                {
                    "name": updated_data["name"],
                    "action": action,
                    "status": status,
                    "data": updated_data if dry_run else None,
                }
            )

    return final_report


def get_formatted_json(data):
    return json.dumps(data, indent=2)


def get_stale_data(selector, report, dry_run=False, verbose=False):
    stale_config_report = []
    persisted_data_set = get_persisted_store(
        CONTROL_PLANE_URL, selector, verbose=verbose
    )
    persisted_items = [item["name"] for item in persisted_data_set]
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
        print("- NO database connections will be made")
        print("- NO data will be modified")
        print("- Only local configurations will be analyzed")
        print("- Reports will show what WOULD be changed")

    if VERBOSE:
        print("\nVERBOSE MODE ACTIVE:")
        print("- All API requests and responses will be logged to debug.log file")
        print("- Request details include: method, URL, headers, auth, body")
        print("- Response details include: status, headers, body")
        print("- Console output will remain clean (debug logs only in file)")

    print("=" * 70)


def print_summary(selector, final_report, dry_run=False):
    print("\n")
    print("#" * 50)
    if dry_run:
        print(f"{selector.capitalize()} Summary - What Would Happen")
    else:
        print(f"{selector.capitalize()} Summary - What Happened")
    print("#" * 50)

    creates = [item for item in final_report if "create" in item["action"]]
    updates = [item for item in final_report if "update" in item["action"]]
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
        print(f"\n✅ All changes have been applied to the database!")
        print(f"🌐 Database: {CONTROL_PLANE_URL}")
        print(f"👤 User: {USERNAME}")
    print("#" * 50)


if __name__ == "__main__":
    # Initialize debug logging if verbose mode is enabled
    if VERBOSE:
        initialize_debug_log()

    # Log execution plan first
    log_execution_plan()

    if DRY_RUN:
        print("\n" + "=" * 60)
        print("DRY RUN MODE - No changes will be made to the database")
        print("=" * 60)

    for selector in SELECTORS:
        print("\n")
        print("#" * 50)
        mode_text = " (DRY RUN)" if DRY_RUN else ""
        print(
            "Running {} Definitions Updates{}".format(selector.capitalize(), mode_text)
        )
        final_report = update_diff_db(selector, ITEM_NAME, DRY_RUN, VERBOSE)

        # Always show summary first (most important for users)
        print_summary(selector, final_report, DRY_RUN)

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
                            get_stale_data(selector, final_report, DRY_RUN)
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
