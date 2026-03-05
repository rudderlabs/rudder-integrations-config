#!/usr/bin/env python3
import json
import os
import sys
import jsondiff
import argparse
from constants import CONFIG_DIR
from utils import (
    get_config_definition,
    get_file_content,
    update_config_definition,
    create_config_definition,
    get_formatted_json,
    initialize_debug_log,
)

BLACK_LIST_DESTINATIONS = []


def get_command_line_arguments():
    parser = argparse.ArgumentParser(
        description="Script to deploy account configurations to DB."
    )
    parser.add_argument("control_plane_url", nargs="?", help="Control plane URL")
    parser.add_argument("username", nargs="?", help="Control plane admin username")
    parser.add_argument("password", nargs="?", help="Control plane admin password")
    parser.add_argument(
        "definition_name", nargs="?", help="Specific item name to update.", default=None
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
    definition_name = args.definition_name or os.getenv("DEFINITION_NAME")

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

    if invalid_args:
        print("Error: The following arguments or environment variables are invalid:")
        for arg in invalid_args:
            print(arg)
        sys.exit(1)

    return (
        control_plane_url,
        username,
        password,
        definition_name,
        args.dry_run,
        args.verbose,
    )


def log_execution_plan(
    control_plane_url, username, password, definition_name, dry_run, verbose
):
    """Log detailed execution plan showing what would happen in normal mode"""
    print("=" * 70)
    print("EXECUTION PLAN")
    print("=" * 70)
    print(f"Control Plane URL: {control_plane_url}")
    print(f"Username: {username}")
    print(f"Password: {'*' * len(password)}")
    if definition_name:
        print(f"Specific account: {definition_name}")
    else:
        print("Processing: ALL account configurations")

    print("\nWhat would happen in NORMAL mode:")
    print("1. Connect to the control plane database")
    print("2. Fetch existing account definitions from database")
    print("3. Scan local account configuration directories:")
    print("   - ./src/configurations/destinations/*/accounts/*")
    print("   - ./src/configurations/sources/*/accounts/*")
    print("4. For each account configuration found:")
    print("   a) Compare local vs remote configurations")
    print("   b) If differences found: UPDATE the database record")
    print("   c) If not found in database: CREATE new database record")
    print("5. All changes would be PERMANENTLY applied to the database")

    if dry_run:
        print("\nDRY RUN MODE ACTIVE:")
        print("- Database connections will be made ONLY to fetch existing data")
        print("- NO account data will be modified")
        print("- Local configurations will be analyzed and compared")
        print("- Reports will show what WOULD be changed")

    if verbose:
        print("\nVERBOSE MODE ACTIVE:")
        print("- All API requests and responses will be logged to debug.log file")
        print("- Request details include: method, URL, headers, auth, body")
        print("- Response details include: status, headers, body")
        print("- Console output will remain clean (debug logs only in file)")

    print("=" * 70)


def print_summary(final_report, dry_run=False, control_plane_url="", username=""):
    """Print user-friendly summary of account deployment results"""
    print("\n")
    print("#" * 50)
    if dry_run:
        print("Account Summary - What Would Happen")
    else:
        print("Account Summary - What Happened")
    print("#" * 50)

    creates = [item for item in final_report if "create" in item["action"]]
    updates = [item for item in final_report if "update" in item["action"]]
    no_changes = [item for item in final_report if item["action"] == "N/A"]

    print(f"📊 Total account configurations processed: {len(final_report)}")
    if dry_run:
        print(f"🆕 Would CREATE: {len(creates)} new accounts")
        print(f"🔄 Would UPDATE: {len(updates)} existing accounts")
        print(f"✅ No changes needed: {len(no_changes)} accounts")
    else:
        print(f"🆕 CREATED: {len(creates)} new accounts")
        print(f"🔄 UPDATED: {len(updates)} existing accounts")
        print(f"✅ No changes needed: {len(no_changes)} accounts")

    if creates:
        if dry_run:
            print(f"\n🆕 New accounts that would be CREATED:")
        else:
            print(f"\n🆕 New accounts that were CREATED:")
        for item in creates:
            print(f"   - {item['name']}")

    if updates:
        if dry_run:
            print(f"\n🔄 Accounts that would be UPDATED:")
        else:
            print(f"\n🔄 Accounts that were UPDATED:")
        for item in updates:
            print(f"   - {item['name']}")

    if dry_run:
        print(f"\n⚠️  In normal mode, these changes would be PERMANENT!")
        print(f"🌐 Database: {control_plane_url}")
        print(f"👤 User: {username}")
        print(f"🔍 To run this script in normal mode, use the --no-dry-run flag")
    else:
        print(f"\n✅ All changes have been applied to the database!")
        print(f"🌐 Database: {control_plane_url}")
        print(f"👤 User: {username}")
    print("#" * 50)


def update_account_db(
    base_url, auth, definition_name=None, dry_run=False, verbose=False
):
    """
    Update account definitions in the database.

    Args:
        base_url: Control plane URL
        auth: Authentication tuple (username, password)
        definition_name: Optional specific item name to update
        dry_run: If True, show what would be changed without making actual changes

    Returns:
        List of dictionaries with update results
    """
    final_report = []

    # Get existing account definitions from the control plane

    print("🔍 Fetching existing account definitions...")

    persisted_data = get_config_definition(
        base_url, "account", auth=auth, verbose=verbose
    )
    if persisted_data.status_code == 200:
        account_definitions = json.loads(persisted_data.text)
    else:
        print(
            f"Error: Unable to fetch account definitions from the control plane. Status code: {persisted_data.status_code}"
        )
        sys.exit(1)

    # Create a map of account names for faster lookup
    account_map = {account["name"]: account for account in account_definitions}

    # Determine which categories to process
    supported_categories = ["destinations", "sources"]

    # Process each category
    for category in supported_categories:
        # Determine which items to process
        if definition_name:
            current_items = [definition_name]
        else:
            try:
                current_items = os.listdir(f"./{CONFIG_DIR}/{category}")
            except FileNotFoundError:
                print(
                    f"Warning :: Directory ./{CONFIG_DIR}/{category} not found. Skipping."
                )
                continue

        # Process each item
        for item in current_items:
            if (
                item.upper() in BLACK_LIST_DESTINATIONS
                and "api.rudderstack.com" in CONTROL_PLANE_URL
            ):
                print("Skipping BlakcListed Destination: ", item)
                continue

            item_path = f"./{CONFIG_DIR}/{category}/{item}"
            accounts_path = f"{item_path}/accounts"

            # Skip if not a directory or no accounts directory
            if not os.path.isdir(item_path):
                continue
            if not os.path.isdir(accounts_path):
                continue

            # Process each authentication type
            try:
                authentication_types = os.listdir(accounts_path)
            except FileNotFoundError:
                print(f"Warning :: Emppty directory {accounts_path}. Skipping.")
                continue

            for auth_type in authentication_types:
                auth_type_path = f"{accounts_path}/{auth_type}"

                # Skip if not a directory
                if not os.path.isdir(auth_type_path):
                    continue

                # Get account configuration
                try:
                    updated_data = get_file_content(auth_type_path)
                    if not updated_data or "name" not in updated_data:
                        print(
                            f"Warning :: Missing or invalid configuration in {auth_type_path}"
                        )
                        continue

                    account_name = updated_data["name"]
                    # Check if account already exists
                    if account_name in account_map:
                        # Update existing account if there are changes
                        existing_account = account_map[account_name]
                        diff = jsondiff.diff(
                            existing_account, updated_data, marshal=True
                        )
                        diff.pop("$delete", None)

                        if diff and len(diff.keys()) > 0:
                            status, _ = update_config_definition(
                                base_url,
                                "account",
                                account_name,
                                updated_data,
                                method="PUT",
                                auth=auth,
                                dry_run=dry_run,
                                verbose=verbose,
                            )
                            final_report.append(
                                {
                                    "name": account_name,
                                    "action": "update",
                                    "status": status,
                                    "diff": diff if dry_run else None,
                                }
                            )
                        else:
                            final_report.append(
                                {
                                    "name": account_name,
                                    "action": "N/A",
                                    "status": "No changes detected",
                                }
                            )
                    else:
                        # Create new account
                        status, _ = create_config_definition(
                            base_url,
                            "account",
                            updated_data,
                            auth,
                            dry_run=dry_run,
                            verbose=verbose,
                        )
                        final_report.append(
                            {"name": account_name, "action": "create", "status": status}
                        )
                except Exception as e:
                    print(f"Error processing {auth_type_path}: {str(e)}")
                    sys.exit(1)

    return final_report


if __name__ == "__main__":
    # Get command line arguments
    CONTROL_PLANE_URL, USERNAME, PASSWORD, DEFINITION_NAME, DRY_RUN, VERBOSE = (
        get_command_line_arguments()
    )
    AUTH = (USERNAME, PASSWORD)

    # Initialize debug logging if verbose mode is enabled
    if VERBOSE:
        initialize_debug_log()

    # Log execution plan first
    log_execution_plan(
        CONTROL_PLANE_URL, USERNAME, PASSWORD, DEFINITION_NAME, DRY_RUN, VERBOSE
    )
    if DRY_RUN:
        print("\n" + "=" * 60)
        print("DRY RUN MODE - No changes will be made to the database")
        print("=" * 60)

    print("\n")
    print("#" * 50)
    mode_text = " (DRY RUN)" if DRY_RUN else ""
    print("Deploying Account Definitions{}".format(mode_text))
    print("#" * 50)

    # Update account definitions
    final_report = update_account_db(
        CONTROL_PLANE_URL, AUTH, DEFINITION_NAME, DRY_RUN, VERBOSE
    )

    # Always show summary first (most important for users)
    print_summary(final_report, DRY_RUN, CONTROL_PLANE_URL, USERNAME)

    # Show detailed reports only when verbose flag is used (write to deploy-debug.log)
    if VERBOSE:
        changed_items = [
            item
            for item in final_report
            if item["action"] != "N/A" and item.get("status") != "No changes detected"
        ]
        try:
            with open("deploy-debug.log", "a", encoding="utf-8") as f:
                f.write(f"\n{'='*50}\n")
                f.write(f"Account Definition Update Report{mode_text}\n")
                f.write(f"{'='*50}\n")
                f.write(get_formatted_json(changed_items) + "\n\n")
        except Exception as e:
            print(f"Warning: Could not write verbose reports to deploy-debug.log: {e}")

    # Show debug log location if verbose mode was used
    if VERBOSE:
        print(f"\n📝 Debug logs have been written to: debug.log")
        print(f"💡 Review this file for detailed API request/response information")

    # Exit with error if any account failed to update (but not in dry run mode)
    if not DRY_RUN:
        failed = any(
            item["status"] not in ["", 200, 201, "No changes detected"]
            for item in final_report
        )
        sys.exit(1 if failed else 0)
    else:
        # In dry run mode, always exit successfully
        sys.exit(0)
