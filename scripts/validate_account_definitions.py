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


def validate_account_field_coverage(dest_dir):
    """
    Validate that for each non-oauth account definition:
      1. All fields (secretFields + optionFields) are present in the destination's destConfig.
      2. All secretFields are present in the destination's secretKeys.

    The workspace config API (v1) filters its response based on the fields declared
    in the destination definition's destConfig. If an account field is missing from
    destConfig, it will be silently dropped from the API response.

    OAuth accounts are excluded because their secrets are managed by the OAuth flow,
    not through destConfig.

    Args:
        dest_dir: Path to the destination directory.

    Returns:
        bool: True if validation passes, False otherwise
    """
    accounts_dir = dest_dir / "accounts"

    if not accounts_dir.exists():
        return True  # No accounts to validate

    dest_config = load_json_file(dest_dir / "db-config.json")
    cfg = dest_config.get("config", {})
    dest_secret_keys = set(cfg.get("secretKeys", []))
    dest_config_fields = set(cfg.get("destConfig", {}).get("defaultConfig", []))

    success = True

    for account_dir in accounts_dir.glob("*"):
        if not account_dir.is_dir():
            continue

        account_config = load_json_file(account_dir / "db-config.json")

        if account_config.get("authenticationType") == "oauth":
            continue

        account_name = account_config["name"]
        account_cfg = account_config.get("config", {})
        secret_fields = account_cfg.get("secretFields", [])
        option_fields = account_cfg.get("optionFields", [])
        all_fields = secret_fields + option_fields

        missing_from_dest_config = [f for f in all_fields if f not in dest_config_fields]
        if missing_from_dest_config:
            print(
                f"\nERROR: Account '{account_name}' has fields missing from destination "
                f"'{dest_dir.name}' destConfig:"
            )
            for field in missing_from_dest_config:
                print(f"  - {field}")
            print(
                f"\n  The workspace config API filters its response based on destConfig. "
                f"Add the missing field(s) to '{dest_dir.name}' destConfig to prevent "
                f"them from being silently dropped from the API response."
            )
            success = False

        missing_from_secret_keys = [f for f in secret_fields if f not in dest_secret_keys]
        if missing_from_secret_keys:
            print(
                f"\nERROR: Account '{account_name}' has secretFields missing from destination "
                f"'{dest_dir.name}' secretKeys:"
            )
            for field in missing_from_secret_keys:
                print(f"  - {field}")
            print(
                f"\n  Add the missing field(s) to '{dest_dir.name}' secretKeys."
            )
            success = False

    return success


def validate_destinations(dest_dirs):
    """Run all validations for the given destination directories."""
    success = True
    for dest_dir in dest_dirs:
        if not validate_destination_accounts(dest_dir.name):
            success = False
        if not validate_account_field_coverage(dest_dir):
            success = False
    return success


def main():
    """Main entry point."""
    base_dir = Path("src/configurations/destinations")
    if len(sys.argv) > 1:
        dest_dirs = [base_dir / sys.argv[1]]
    else:
        dest_dirs = [d for d in base_dir.glob("*") if d.is_dir() and (d / "db-config.json").exists()]

    sys.exit(0 if validate_destinations(dest_dirs) else 1)


if __name__ == "__main__":
    main()
