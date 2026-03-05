#!/usr/bin/env python3
"""
Validation script to ensure consistency between destination account definitions
and account configuration files.

This script checks that all rudderAccountId values listed in a destination's
db-config.json have corresponding account configuration files.
"""

import os
import sys
import json
import glob
from pathlib import Path


def load_json_file(file_path):
    """Load and parse a JSON file."""
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading {file_path}: {e}")
        return None


def validate_destination_accounts(destination_name):
    """
    Validate that all rudderAccountId values in the destination's db-config.json
    have corresponding account configuration files.

    Args:
        destination_name: Name of the destination (e.g., 'zoho')

    Returns:
        bool: True if validation passes, False otherwise
    """
    # Paths
    base_dir = Path("src/configurations/destinations")
    dest_dir = base_dir / destination_name
    main_config_path = dest_dir / "db-config.json"
    accounts_dir = dest_dir / "accounts"

    # Check if destination exists
    if not dest_dir.exists():
        print(
            f"Error: Destination '{destination_name}' not found. Skipping validation."
        )
        return True

    # Load main destination config
    main_config = load_json_file(main_config_path)
    if not main_config:
        return False

    # Extract rudderAccountId values
    try:
        account_definitions = main_config.get("config", {}).get(
            "supportedAccountDefinitions", {}
        )
        if not account_definitions:
            print(
                f"Warning: No supportedAccountDefinitions found in {main_config_path}"
            )
            return True  # No accounts to validate

        required_account_ids = []

        # Extract account IDs from rudderAccountId array
        if "rudderAccountId" in account_definitions and isinstance(
            account_definitions["rudderAccountId"], list
        ):
            required_account_ids.extend(account_definitions["rudderAccountId"])

        # Also check for rudderDeleteAccountId if present
        if "rudderDeleteAccountId" in account_definitions and isinstance(
            account_definitions["rudderDeleteAccountId"], list
        ):
            required_account_ids.extend(account_definitions["rudderDeleteAccountId"])

        # Print debug information
        print(
            f"Found {len(required_account_ids)} required account IDs: {required_account_ids}"
        )
    except (KeyError, AttributeError) as e:
        print(f"Error extracting account definitions: {e}")
        return False

    if not required_account_ids:
        print(f"Warning: No rudderAccountId values found in {main_config_path}")
        return True  # No accounts to validate

    # Find all account configuration files
    account_configs = []

    # Check if accounts directory exists
    if not accounts_dir.exists():
        print(f"Warning: Accounts directory not found at {accounts_dir}")
        if required_account_ids:
            print(f"Error: Required account IDs found but no accounts directory exists")
            return False
        return True

    # Find all account configuration files in all authentication type directories
    for auth_type_dir in accounts_dir.glob("*"):
        if auth_type_dir.is_dir():
            for config_file in auth_type_dir.glob("db-config.json"):
                account_configs.append(config_file)

    print(f"Found {len(account_configs)} account configuration files")

    # Extract account names from configuration files
    existing_account_names = []
    for config_file in account_configs:
        config = load_json_file(config_file)
        if config and "name" in config:
            existing_account_names.append(config["name"])
            print(f"  - Found account: {config['name']} in {config_file}")
        else:
            print(f"  - Warning: Missing 'name' field in {config_file}")

    # Validate that all required accounts exist
    missing_accounts = []
    for account_id in required_account_ids:
        if account_id not in existing_account_names:
            missing_accounts.append(account_id)

    if missing_accounts:
        print(
            f"\nERROR: The following account IDs do not have corresponding account configurations:"
        )
        for account in missing_accounts:
            print(f"  - {account}")
        print(
            "\nPlease create the missing account configuration files or remove them from supportedAccountDefinitions."
        )
        return False

    print(f"\n✅ Validation successful for destination '{destination_name}'")
    print(
        f"   All {len(required_account_ids)} required account(s) have corresponding configuration files"
    )
    return True


def validate_all_destinations():
    """Validate all destinations in the repository."""
    base_dir = Path("src/configurations/destinations")
    success = True

    for dest_dir in base_dir.glob("*"):
        if dest_dir.is_dir() and (dest_dir / "db-config.json").exists():
            dest_name = dest_dir.name
            if not validate_destination_accounts(dest_name):
                success = False

    return success


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        # Validate specific destination
        destination_name = sys.argv[1]
        success = validate_destination_accounts(destination_name)
    else:
        # Validate all destinations
        success = validate_all_destinations()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
