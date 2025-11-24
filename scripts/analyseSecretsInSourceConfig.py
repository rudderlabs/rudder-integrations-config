#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to analyze destination configuration files for secret field mismatches.

This script parses db-config.json, schema.json, and ui-config.json files across
all destination directories to identify secrets and validate their consistency.

Rules:
1. Secrets are identified by being in secretKeys in db-config.json AND secret=true in ui-config.json
2. If only one condition is met, it's flagged as a mismatch
3. Secret keys validation with includeKeys/excludeKeys:
   - If includeKeys exists and is not empty: ERROR if secret is in includeKeys
   - If includeKeys is empty/undefined: ERROR if secret is NOT in excludeKeys
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, asdict


@dataclass
class SecretAnalysis:
    """Data class to hold secret analysis results for a destination."""
    destination: str
    valid_secrets: List[str]
    not_in_dest_config: List[str]  # In secretKeys and ui-config but not in defaultConfig
    secrets_in_include_keys: List[str]  # Secret keys in includeKeys (ERROR)
    not_in_exclude_keys_error: List[str]  # Secrets not in excludeKeys when includeKeys is empty (ERROR)
    source_specific_secrets: Dict[str, List[str]]  # Secrets defined in source-specific configs that support device/hybrid mode
    has_include_keys: bool  # Whether includeKeys is defined and non-empty
    supports_device_mode: bool  # Whether destination supports device or hybrid mode
    supports_cloud_mode: bool  # Whether destination supports cloud or hybrid mode

    def has_issues(self) -> bool:
        """Check if this destination has any issues."""
        return bool(
            self.secrets_in_include_keys or
            self.not_in_exclude_keys_error
        )

    def has_secrets(self) -> bool:
        """Check if this destination has any secrets defined."""
        return bool(self.valid_secrets or self.source_specific_secrets)

    def is_relevant(self) -> bool:
        """Check if this destination is relevant for analysis."""
        # Only relevant if:
        # 1. Supports device/hybrid mode (for secret transmission)
        # 2. Also supports cloud mode (secrets are only needed for cloud/hybrid communication)
        # 3. Has valid secrets or source-specific secrets or has issues that need to be addressed
        return (self.supports_device_mode and
                self.supports_cloud_mode and
                (self.valid_secrets or self.source_specific_secrets or self.has_issues()))


def find_secret_fields_in_ui_config(ui_config_data: dict) -> tuple[Set[str], Set[str]]:
    """
    Recursively find all fields marked with secret=true and all fields in ui-config.json.

    Args:
        ui_config_data: Parsed ui-config.json data

    Returns:
        Tuple of (secret_fields, all_fields) - sets of field names
    """
    secret_fields = set()
    all_fields = set()

    def traverse(obj):
        if isinstance(obj, dict):
            # Check if this is a field definition
            field_name = None
            if 'value' in obj and isinstance(obj['value'], str):
                field_name = obj['value']
            elif 'configKey' in obj and isinstance(obj['configKey'], str):
                field_name = obj['configKey']

            if field_name:
                all_fields.add(field_name)
                # Check if this field is marked as secret
                if obj.get('secret') is True:
                    secret_fields.add(field_name)

            # Recursively traverse all values
            for value in obj.values():
                traverse(value)
        elif isinstance(obj, list):
            for item in obj:
                traverse(item)

    traverse(ui_config_data)
    return secret_fields, all_fields


def check_connection_mode_support(supported_connection_modes: dict) -> tuple[bool, bool]:
    """
    Check if destination supports device/hybrid mode and cloud mode.

    Args:
        supported_connection_modes: The supportedConnectionModes dict from db-config.json

    Returns:
        Tuple of (supports_device_or_hybrid, supports_cloud)
    """
    if not supported_connection_modes:
        return False, False

    has_device_or_hybrid = False
    has_cloud = False

    for source_type, modes in supported_connection_modes.items():
        if isinstance(modes, list):
            if 'device' in modes or 'hybrid' in modes:
                has_device_or_hybrid = True
            if 'cloud' in modes or 'hybrid' in modes:
                has_cloud = True

    return has_device_or_hybrid, has_cloud


def get_default_config_fields(dest_config: dict) -> Set[str]:
    """
    Get all fields mentioned in defaultConfig only.

    Args:
        dest_config: The destConfig dict from db-config.json

    Returns:
        Set of all field names mentioned in defaultConfig
    """
    fields = set()

    if not dest_config:
        return fields

    # Only get fields from defaultConfig
    default_config = dest_config.get('defaultConfig', [])
    if isinstance(default_config, list):
        fields.update(default_config)

    return fields


def get_source_specific_secrets(
    dest_config: dict,
    supported_connection_modes: dict,
    secrets_in_both: Set[str]
) -> Dict[str, List[str]]:
    """
    Get secrets that are defined in source-specific configs (not defaultConfig)
    where the source type supports device or hybrid mode.

    Args:
        dest_config: The destConfig dict from db-config.json
        supported_connection_modes: The supportedConnectionModes dict
        secrets_in_both: Secrets that are in both secretKeys and ui-config

    Returns:
        Dict mapping source type to list of secrets
    """
    source_specific = {}

    if not dest_config or not supported_connection_modes:
        return source_specific

    # Get fields from defaultConfig to exclude them
    default_fields = set(dest_config.get('defaultConfig', []))

    # Check each source type
    for source_type, config_fields in dest_config.items():
        # Skip defaultConfig
        if source_type == 'defaultConfig':
            continue

        # Check if this source type supports device or hybrid mode
        modes = supported_connection_modes.get(source_type, [])
        if not isinstance(modes, list):
            continue

        has_device_or_hybrid = 'device' in modes or 'hybrid' in modes

        if not has_device_or_hybrid:
            continue

        # Get fields that are in this source config but NOT in defaultConfig
        if isinstance(config_fields, list):
            source_fields = set(config_fields)
            # Find secrets that are in this source config but not in defaultConfig
            source_only_secrets = (source_fields & secrets_in_both) - default_fields

            if source_only_secrets:
                source_specific[source_type] = sorted(list(source_only_secrets))

    return source_specific


def analyze_destination(dest_path: Path) -> SecretAnalysis:
    """
    Analyze a single destination directory for secret field consistency.

    Args:
        dest_path: Path to the destination directory

    Returns:
        SecretAnalysis object with results
    """
    dest_name = dest_path.name

    db_config_path = dest_path / "db-config.json"
    ui_config_path = dest_path / "ui-config.json"

    # Initialize result sets
    secret_keys_in_db = set()
    include_keys_in_db = set()
    exclude_keys_in_db = set()
    dest_config_fields = set()
    has_include_keys = False
    supports_device_mode = False
    supports_cloud_mode = False
    supported_connection_modes = {}
    dest_config = {}

    # Parse db-config.json
    if db_config_path.exists():
        try:
            with open(db_config_path, 'r') as f:
                db_config = json.load(f)
                config = db_config.get('config', {})
                secret_keys_in_db = set(config.get('secretKeys', []))

                include_keys = config.get('includeKeys', [])
                if include_keys:  # Non-empty list
                    has_include_keys = True
                    include_keys_in_db = set(include_keys)

                exclude_keys_in_db = set(config.get('excludeKeys', []))

                # Check if destination supports device/hybrid and cloud modes
                supported_connection_modes = config.get('supportedConnectionModes', {})
                supports_device_mode, supports_cloud_mode = check_connection_mode_support(supported_connection_modes)

                # Get all fields from defaultConfig only
                dest_config = config.get('destConfig', {})
                dest_config_fields = get_default_config_fields(dest_config)
        except json.JSONDecodeError as e:
            print(f"Warning: Failed to parse {db_config_path}: {e}", file=sys.stderr)

    # Parse ui-config.json
    # if ui_config_path.exists():
    #     try:
    #         with open(ui_config_path, 'r') as f:
    #             ui_config = json.load(f)
    #             secret_fields_in_ui, all_fields_in_ui = find_secret_fields_in_ui_config(ui_config)
    #     except json.JSONDecodeError as e:
    #         print(f"Warning: Failed to parse {ui_config_path}: {e}", file=sys.stderr)

    # Analyze the results
    # A secret is valid only if it's in secretKeys AND in defaultConfig
    # We consider all secrets in secretKeys (ui-config check was removed per user's improvements)
    valid_secrets = list(secret_keys_in_db & dest_config_fields)

    # Secrets not in defaultConfig
    secrets_not_in_dest_config = list(secret_keys_in_db - dest_config_fields)

    # Get source-specific secrets (secrets in source type configs but not defaultConfig)
    # that support device/hybrid mode
    source_specific_secrets = get_source_specific_secrets(
        dest_config,
        supported_connection_modes,
        secret_keys_in_db
    )

    # Check includeKeys/excludeKeys logic
    secrets_in_include_keys = []
    not_in_exclude_keys_error = []

    if has_include_keys:
        # If includeKeys exists and is non-empty, secrets should NOT be in it
        secrets_in_include_keys = list(secret_keys_in_db & include_keys_in_db)
    else:
        # If includeKeys is empty/undefined AND excludeKeys is non-empty, secrets MUST be in excludeKeys
        # If both are empty/undefined, we don't flag as violation
        if exclude_keys_in_db:  # Only check if excludeKeys has items
            not_in_exclude_keys_error = list(secret_keys_in_db - exclude_keys_in_db)

    return SecretAnalysis(
        destination=dest_name,
        valid_secrets=sorted(valid_secrets),
        not_in_dest_config=sorted(secrets_not_in_dest_config),
        secrets_in_include_keys=sorted(secrets_in_include_keys),
        not_in_exclude_keys_error=sorted(not_in_exclude_keys_error),
        source_specific_secrets=source_specific_secrets,
        has_include_keys=has_include_keys,
        supports_device_mode=supports_device_mode,
        supports_cloud_mode=supports_cloud_mode
    )


def print_console_output(results: List[SecretAnalysis]):
    """
    Print human-readable console output.

    Args:
        results: List of SecretAnalysis objects
    """
    print("=" * 80)
    print("SECRET FIELDS ANALYSIS REPORT")
    print("=" * 80)
    print()

    # Summary statistics
    total_destinations = len(results)
    destinations_with_secrets = sum(1 for r in results if r.has_secrets())
    destinations_without_secrets = total_destinations - destinations_with_secrets
    destinations_without_device_mode = sum(1 for r in results if r.has_secrets() and not r.supports_device_mode)
    destinations_device_only = sum(1 for r in results if r.has_secrets() and r.supports_device_mode and not r.supports_cloud_mode)
    destinations_relevant = sum(1 for r in results if r.is_relevant())
    destinations_with_issues = sum(1 for r in results if r.is_relevant() and r.has_issues())
    destinations_clean = destinations_relevant - destinations_with_issues

    print(f"Total Destinations Analyzed: {total_destinations}")
    print(f"Destinations with Secrets: {destinations_with_secrets}")
    print(f"Destinations without Secrets (skipped): {destinations_without_secrets}")
    print(f"Destinations without Device/Hybrid Mode (skipped): {destinations_without_device_mode}")
    print(f"Destinations with Device-Only Mode (skipped): {destinations_device_only}")
    print(f"Destinations Relevant for Analysis: {destinations_relevant}")
    print(f"Destinations with Issues: {destinations_with_issues}")
    print(f"Destinations Clean (no violations): {destinations_clean}")
    print()

    # Detailed results for destinations with issues
    if destinations_with_issues > 0:
        print("=" * 80)
        print("DESTINATIONS WITH ISSUES")
        print("=" * 80)
        print()

        for result in results:
            # Skip destinations that are not relevant (no secrets or no device mode)
            if not result.is_relevant():
                continue

            if not result.has_issues():
                continue

            print(f"Destination: {result.destination}")
            print("-" * 80)

            if result.valid_secrets:
                print(f"  [OK] Valid Secrets ({len(result.valid_secrets)}):")
                for secret in result.valid_secrets:
                    print(f"    - {secret}")
                print()

            if result.source_specific_secrets:
                print(f"  [INFO] Source-Specific Secrets (device/hybrid mode):")
                for source_type, secrets in result.source_specific_secrets.items():
                    print(f"    {source_type}:")
                    for secret in secrets:
                        print(f"      - {secret}")
                print()

            if result.secrets_in_include_keys:
                print(f"  [ERROR] Secret in includeKeys ({len(result.secrets_in_include_keys)}):")
                for secret in result.secrets_in_include_keys:
                    print(f"    - {secret} (SECRET SHOULD NOT BE IN includeKeys!)")
                print()

            if result.not_in_exclude_keys_error:
                print(f"  [ERROR] Secret not in excludeKeys ({len(result.not_in_exclude_keys_error)}):")
                for secret in result.not_in_exclude_keys_error:
                    print(f"    - {secret} (includeKeys is empty/undefined, so secret MUST be in excludeKeys!)")
                print()

            print()

    # Summary footer
    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print()


def save_json_output(results: List[SecretAnalysis], output_path: Path):
    """
    Save results to a JSON file.

    Args:
        results: List of SecretAnalysis objects
        output_path: Path to save the JSON file
    """
    # Filter out destinations that are not relevant (no secrets or no device mode)
    results_relevant = [r for r in results if r.is_relevant()]
    # Include destinations with issues OR with source-specific secrets
    results_to_report = [r for r in results_relevant if r.has_issues() or r.source_specific_secrets]

    # Convert results to dict and remove empty fields
    def clean_result(result: SecretAnalysis) -> dict:
        """Convert result to dict and remove empty list fields and internal flags."""
        data = asdict(result)
        # Remove empty lists/dicts, internal boolean flags, and valid_secrets
        fields_to_exclude = ['has_include_keys', 'supports_device_mode', 'supports_cloud_mode', 'valid_secrets']
        cleaned = {}
        for k, v in data.items():
            # Skip excluded fields
            if k in fields_to_exclude:
                continue
            # Skip empty lists
            if isinstance(v, list) and len(v) == 0:
                continue
            # Skip empty dicts
            if isinstance(v, dict) and len(v) == 0:
                continue
            cleaned[k] = v
        return cleaned

    output_data = {
        "summary": {
            "total_destinations": len(results),
            "destinations_with_secrets": sum(1 for r in results if r.has_secrets()),
            "destinations_without_secrets": sum(1 for r in results if not r.has_secrets()),
            "destinations_without_device_mode": sum(1 for r in results if r.has_secrets() and not r.supports_device_mode),
            "destinations_device_only": sum(1 for r in results if r.has_secrets() and r.supports_device_mode and not r.supports_cloud_mode),
            "destinations_relevant": len(results_relevant),
            "destinations_with_issues": sum(1 for r in results_relevant if r.has_issues()),
            "destinations_with_source_specific_secrets": sum(1 for r in results_relevant if r.source_specific_secrets),
            "destinations_clean": len([r for r in results_relevant if not r.has_issues() and not r.source_specific_secrets])
        },
        "results": [clean_result(r) for r in results_to_report]
    }

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"JSON output saved to: {output_path}")


def main():
    """Main execution function."""
    # Determine the base path
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    destinations_dir = repo_root / "src" / "configurations" / "destinations"

    if not destinations_dir.exists():
        print(f"Error: Destinations directory not found: {destinations_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Scanning destinations in: {destinations_dir}")
    print()

    # Find all destination directories
    destination_dirs = [d for d in destinations_dir.iterdir() if d.is_dir()]

    # Analyze each destination
    results = []
    for dest_dir in sorted(destination_dirs):
        analysis = analyze_destination(dest_dir)
        results.append(analysis)

    # Print console output
    print_console_output(results)

    # Save JSON output
    output_json_path = script_dir / "secrets_analysis_report.json"
    save_json_output(results, output_json_path)


if __name__ == "__main__":
    main()
