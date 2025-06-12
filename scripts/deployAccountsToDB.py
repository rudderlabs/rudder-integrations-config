#!/usr/bin/env python3
import requests
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
)

BLACK_LIST_DESTINATIONS = ["ZOHO_DEV"]


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

    return control_plane_url, username, password, definition_name


def update_account_db(base_url, auth, definition_name=None):
    """
    Update account definitions in the database.

    Args:
        base_url: Control plane URL
        auth: Authentication tuple (username, password)
        definition_name: Optional specific item name to update

    Returns:
        List of dictionaries with update results
    """
    final_report = []

    # Get existing account definitions from the control plane
    persisted_data = get_config_definition(base_url, "accounts", "", auth)
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

                        if diff and len(diff.keys()) > 0:
                            status, response = update_config_definition(
                                base_url, "accounts", account_name, updated_data, auth
                            )
                            final_report.append(
                                {
                                    "name": account_name,
                                    "action": "update",
                                    "status": status,
                                }
                            )
                        else:
                            final_report.append(
                                {"name": account_name, "action": "N/A", "status": ""}
                            )
                    else:
                        # Create new account
                        status, response = create_config_definition(
                            base_url, "accounts", updated_data, auth
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
    CONTROL_PLANE_URL, USERNAME, PASSWORD, DEFINITION_NAME = (
        get_command_line_arguments()
    )
    AUTH = (USERNAME, PASSWORD)

    if CONTROL_PLANE_URL == "https://api.rudderstack.com":
        print("Skipping accounts update for production.")
        sys.exit(0)

    print("#" * 50)
    print("Deploying Account Definitions")
    print("#" * 50)

    # Update account definitions
    final_report = update_account_db(CONTROL_PLANE_URL, AUTH, DEFINITION_NAME)

    print("\n")
    print("#" * 50)
    print("Account Definition Update Report")
    print(get_formatted_json(final_report))

    # Count statistics
    created = sum(1 for item in final_report if item["action"] == "create")
    updated = sum(1 for item in final_report if item["action"] == "update")
    unchanged = sum(1 for item in final_report if item["action"] == "N/A")

    print("\n")
    print("#" * 50)
    print("Summary:")
    print(f"  Total accounts processed: {len(final_report)}")
    print(f"  Created: {created}")
    print(f"  Updated: {updated}")
    print(f"  Unchanged: {unchanged}")
    print("#" * 50)

    # Exit with error if any account failed to update
    failed = any(item["status"] not in ["", 200, 201] for item in final_report)
    sys.exit(1 if failed else 0)
