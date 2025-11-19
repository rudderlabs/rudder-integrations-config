"""
Improved Schema Generator V2

This is an improved version of schemaGenerator.py that:
1. Preserves original formatting (no reformatting unless needed)
2. Only adds or updates fields, NEVER removes existing fields
3. Preserves existing patterns and values when they exist
4. Provides clear logging of changes

Usage: schemaGeneratorV2.py [-h] [-name name | -all] [-update] selector
    1. selector - "source" or "destination"
    2. all - runs the validator for all the selector.
    3. name - any particular source or destination name such as `google_analytics`
    4. update - updates existing schema with detected changes

Example:
    1. python3 configure-cloud-mode-sources-for-mobile-sources/schemaGenerator/schemaGeneratorV2.py -name="adobe_analytics" destination
    2. python3 configure-cloud-mode-sources-for-mobile-sources/schemaGenerator/schemaGeneratorV2.py -all source
"""

import os
import sys
import json
import argparse
from typing import Dict, Any, List, Set
from enum import Enum

# Add scripts directory to Python path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(os.path.dirname(script_dir))
scripts_dir = os.path.join(repo_root, "scripts")
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

from constants import CONFIG_DIR

# Import the original generator functions we'll reuse
from schemaGenerator import (
    generate_schema,
    get_json_from_file,
    EXCLUDED_DEST,
)

VERBOSE = False


def log(message: str, level: str = "INFO"):
    """Log messages with levels."""
    if VERBOSE or level in ["WARN", "ERROR", "CHANGE"]:
        prefix = {
            "INFO": "ℹ️ ",
            "WARN": "⚠️ ",
            "ERROR": "❌",
            "CHANGE": "✏️ ",
            "SUCCESS": "✅",
        }.get(level, "  ")
        print(f"{prefix} {message}")


def deep_merge_preserve(
    existing: Dict[str, Any],
    generated: Dict[str, Any],
    path: str = "",
) -> tuple[Dict[str, Any], List[str]]:
    """
    Deep merge two dictionaries, preserving existing values and only adding new ones.

    Rules:
    1. If key exists in existing but not in generated: KEEP IT (never remove)
    2. If key exists in generated but not in existing: ADD IT
    3. If key exists in both:
       - For dicts: recursively merge
       - For lists: keep existing (schemas shouldn't change list structure)
       - For primitives: prefer generated (it's the source of truth from configs)

    Returns:
        (merged_dict, list_of_changes)
    """
    result = {}
    changes = []

    # First, copy all existing keys (ensures nothing is removed)
    for key in existing.keys():
        result[key] = existing[key]

    # Then, add or update with generated keys
    for key, gen_value in generated.items():
        current_path = f"{path}.{key}" if path else key

        if key not in existing:
            # NEW KEY - Add it
            result[key] = gen_value
            changes.append(f"ADD {current_path}")
            log(f"Adding new field: {current_path}", "CHANGE")
        else:
            existing_value = existing[key]

            # Key exists in both - decide how to merge
            if isinstance(gen_value, dict) and isinstance(existing_value, dict):
                # Both are dicts - recursively merge
                merged, sub_changes = deep_merge_preserve(
                    existing_value, gen_value, current_path
                )
                result[key] = merged
                changes.extend(sub_changes)
            elif isinstance(gen_value, list) and isinstance(existing_value, list):
                # Both are lists
                # For schema arrays like "required", we should merge them
                if key == "required":
                    # Merge required fields - union of both
                    merged_required = list(set(existing_value + gen_value))
                    if sorted(merged_required) != sorted(existing_value):
                        result[key] = merged_required
                        changes.append(
                            f"UPDATE {current_path} (merged required fields)"
                        )
                        log(f"Merged required fields at {current_path}", "CHANGE")
                    else:
                        result[key] = existing_value
                elif key == "enum":
                    # For enums, prefer generated (source of truth)
                    if sorted(gen_value) != sorted(existing_value):
                        result[key] = gen_value
                        changes.append(f"UPDATE {current_path} (enum values changed)")
                        log(f"Updated enum at {current_path}", "CHANGE")
                    else:
                        result[key] = existing_value
                else:
                    # For other lists, keep existing structure
                    result[key] = existing_value
            else:
                # Primitives or type mismatch
                if gen_value != existing_value:
                    # For patterns, be cautious - only update if significantly different
                    if key == "pattern":
                        # Preserve existing pattern if it's more comprehensive
                        # (e.g., has env variable support)
                        if is_pattern_more_comprehensive(existing_value, gen_value):
                            result[key] = existing_value
                            log(
                                f"Preserving existing pattern at {current_path} "
                                f"(more comprehensive)",
                                "INFO",
                            )
                        else:
                            result[key] = gen_value
                            changes.append(f"UPDATE {current_path}")
                            log(f"Updated pattern at {current_path}", "CHANGE")
                    else:
                        # For other primitives, prefer generated value
                        result[key] = gen_value
                        changes.append(
                            f"UPDATE {current_path}: {existing_value} -> {gen_value}"
                        )
                        log(f"Updated {current_path}", "CHANGE")
                else:
                    result[key] = existing_value

    return result, changes


def is_pattern_more_comprehensive(existing: str, generated: str) -> bool:
    """
    Check if existing pattern is more comprehensive than generated.

    A pattern is considered more comprehensive if it includes:
    - Environment variable support: (^env[.].+)
    - Template support: (^\\{\\{.*\\|\\|(.*)\\}\\}$)
    """
    if not isinstance(existing, str) or not isinstance(generated, str):
        return False

    # Check for env variable support
    has_env_existing = "env[.]" in existing or "^env" in existing
    has_env_generated = "env[.]" in generated or "^env" in generated

    # Check for template support
    has_template_existing = "{{" in existing or "\\{\\{" in existing
    has_template_generated = "{{" in generated or "\\{\\{" in generated

    # Existing is more comprehensive if it has features that generated doesn't
    if has_env_existing and not has_env_generated:
        return True
    if has_template_existing and not has_template_generated:
        return True

    return False


def get_fields_in_conditionals(schema: Dict[str, Any]) -> Set[str]:
    """
    Extract all field names that appear in conditional blocks (allOf, anyOf, oneOf).

    These fields should NOT also appear in root properties since they're conditional.

    Args:
        schema: The configSchema object

    Returns:
        Set of field names found in conditional blocks
    """
    conditional_fields = set()

    def extract_from_conditionals(obj, path=""):
        """Recursively extract field names from conditional blocks."""
        if not isinstance(obj, dict):
            return

        # Check allOf, anyOf, oneOf
        for conditional_key in ["allOf", "anyOf", "oneOf"]:
            if conditional_key in obj:
                for item in obj[conditional_key]:
                    # Look in "then" blocks
                    if "then" in item and "properties" in item["then"]:
                        for field_name in item["then"]["properties"].keys():
                            conditional_fields.add(field_name)
                            log(
                                f"Found conditional field: {field_name} in {conditional_key}",
                                "INFO",
                            )

                    # Recursively check nested conditionals
                    extract_from_conditionals(item, f"{path}.{conditional_key}")

        # Recursively check properties
        if "properties" in obj:
            for prop_name, prop_value in obj["properties"].items():
                if isinstance(prop_value, dict):
                    extract_from_conditionals(prop_value, f"{path}.{prop_name}")

    extract_from_conditionals(schema)
    return conditional_fields


def validate_and_clean_conditional_fields(
    schema: Dict[str, Any],
) -> tuple[Dict[str, Any], List[str]]:
    """
    Validate and clean schema to ensure conditional fields are not in root properties.

    Fields that have preRequisites should only appear in allOf/anyOf blocks,
    not in root properties.

    Args:
        schema: The configSchema object to validate and clean

    Returns:
        (cleaned_schema, list_of_issues)
    """
    issues = []
    cleaned_schema = schema.copy()

    # Get fields that appear in conditional blocks
    conditional_fields = get_fields_in_conditionals(schema)

    if not conditional_fields:
        log("No conditional fields found", "INFO")
        return cleaned_schema, issues

    # Check if any of these also appear in root properties
    root_properties = schema.get("properties", {})
    conflicting_fields = []

    for field_name in conditional_fields:
        if field_name in root_properties:
            conflicting_fields.append(field_name)
            issue = (
                f"Generated schema tried to add '{field_name}' to root properties, "
                f"but this field has preRequisites and should only exist in "
                f"conditional blocks (allOf/anyOf/oneOf)."
            )
            issues.append(issue)
            log(issue, "WARN")

    # Clean up: Remove conflicting fields from root properties
    if conflicting_fields:
        log(
            f"\n⚠️  Generator tried to add {len(conflicting_fields)} conditional "
            f"field(s) to root properties:",
            "WARN",
        )
        for field_name in conflicting_fields:
            log(
                f"   - {field_name} (has preRequisites, should only be in allOf/anyOf)",
                "WARN",
            )

        # Create cleaned schema
        if "properties" in cleaned_schema:
            cleaned_properties = {
                k: v
                for k, v in cleaned_schema["properties"].items()
                if k not in conflicting_fields
            }
            cleaned_schema["properties"] = cleaned_properties

        log(
            f"✏️  Auto-fixed: Prevented {len(conflicting_fields)} conditional "
            f"field(s) from being added to root properties",
            "CHANGE",
        )

    return cleaned_schema, issues


def should_format_array_inline(arr: list, key: str = None) -> bool:
    """
    Determine if an array should be formatted on a single line.

    Criteria:
    - Small arrays (< 5 items)
    - Simple string values
    - Commonly used for enums and required arrays
    """
    if not isinstance(arr, list):
        return False

    # Don't inline if more than 4 items
    if len(arr) > 4:
        return False

    # Don't inline if items are complex (dicts or lists)
    for item in arr:
        if isinstance(item, (dict, list)):
            return False

    # Don't inline if total length would be very long
    str_repr = json.dumps(arr)
    if len(str_repr) > 80:
        return False

    return True


def format_json_custom(obj: Any, indent_level: int = 0, indent_str: str = "  ") -> str:
    """
    Custom JSON formatter that preserves single-line arrays for enums and short lists.
    """
    if isinstance(obj, dict):
        if not obj:
            return "{}"

        lines = ["{"]
        items = list(obj.items())
        for i, (key, value) in enumerate(items):
            is_last = i == len(items) - 1
            comma = "" if is_last else ","

            # Handle arrays that should be inline
            if isinstance(value, list) and should_format_array_inline(value, key):
                formatted_value = json.dumps(value, ensure_ascii=False)
                lines.append(
                    f'{indent_str * (indent_level + 1)}"{key}": {formatted_value}{comma}'
                )
            else:
                formatted_value = format_json_custom(
                    value, indent_level + 1, indent_str
                )
                lines.append(
                    f'{indent_str * (indent_level + 1)}"{key}": {formatted_value}{comma}'
                )

        lines.append(indent_str * indent_level + "}")
        return "\n".join(lines)

    elif isinstance(obj, list):
        if not obj:
            return "[]"

        # For arrays that should be inline
        if should_format_array_inline(obj):
            return json.dumps(obj, ensure_ascii=False)

        # For complex arrays, format across multiple lines
        lines = ["["]
        for i, item in enumerate(obj):
            is_last = i == len(obj) - 1
            comma = "" if is_last else ","
            formatted_item = format_json_custom(item, indent_level + 1, indent_str)
            lines.append(f"{indent_str * (indent_level + 1)}{formatted_item}{comma}")
        lines.append(indent_str * indent_level + "]")
        return "\n".join(lines)

    elif isinstance(obj, str):
        return json.dumps(obj, ensure_ascii=False)

    elif isinstance(obj, bool):
        return "true" if obj else "false"

    elif obj is None:
        return "null"

    else:
        return json.dumps(obj, ensure_ascii=False)


def format_json_preserve(obj: Any, reference: str = None) -> str:
    """
    Format JSON while attempting to preserve the style of a reference.

    If reference is provided, try to match its indentation and array formatting.
    Otherwise, use a sensible default (2 spaces).
    """
    # Detect indentation from reference if provided
    indent = 2
    indent_str = "  "
    if reference:
        lines = reference.split("\n")
        for line in lines:
            if line.startswith("  ") and not line.startswith("   "):
                indent = 2
                indent_str = "  "
                break
            elif line.startswith("    "):
                indent = 4
                indent_str = "    "
                break

    # Use custom formatter that preserves single-line arrays
    return format_json_custom(obj, 0, indent_str)


def update_schema_file(
    selector: str,
    name: str,
    generated_schema: Dict[str, Any],
    dry_run: bool = True,
) -> None:
    """
    Update schema file with generated schema, preserving existing fields.

    Args:
        selector: "source" or "destination"
        name: Integration name
        generated_schema: The newly generated schema
        dry_run: If True, only show what would change without writing
    """
    # Construct file path from repo root
    # repo_root is calculated at module level - use that for consistent paths
    relative_path = f"{CONFIG_DIR}/{selector}s/{name}/schema.json"
    file_path = os.path.join(repo_root, relative_path)

    # Read existing schema if it exists
    existing_schema = None
    original_content = None
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            original_content = f.read()
            try:
                existing_full = json.loads(original_content)
                existing_schema = existing_full.get("configSchema")
            except json.JSONDecodeError as e:
                log(f"Error reading existing schema: {e}", "ERROR")
                return

    if existing_schema:
        log(f"Merging with existing schema for {name}...", "INFO")

        # Merge preserving existing fields
        merged_schema, changes = deep_merge_preserve(
            existing_schema, generated_schema["configSchema"]
        )

        if not changes:
            log(f"No changes needed for {name}", "SUCCESS")
            return

        log(f"\n{len(changes)} change(s) detected for {name}:", "CHANGE")
        for change in changes[:20]:  # Show first 20 changes
            log(f"  - {change}", "CHANGE")
        if len(changes) > 20:
            log(f"  ... and {len(changes) - 20} more changes", "CHANGE")

        final_schema = {"configSchema": merged_schema}
    else:
        log(f"Creating new schema for {name}", "INFO")
        final_schema = generated_schema
        changes = ["NEW_SCHEMA"]

    # Validate and clean: Remove conditional fields from root properties
    log(f"\nValidating conditional fields for {name}...", "INFO")
    cleaned_config_schema, validation_issues = validate_and_clean_conditional_fields(
        final_schema["configSchema"]
    )

    if validation_issues:
        log(
            f"\n{'='*60}",
            "WARN",
        )
        log(
            f"⚠️  VALIDATION ISSUES FOUND FOR {name.upper()}",
            "WARN",
        )
        log(
            f"{'='*60}",
            "WARN",
        )
        for issue in validation_issues:
            log(f"  • {issue}", "WARN")
        log(
            f"\n💡 Auto-fix applied: These fields were NOT added to root properties.",
            "WARN",
        )
        log(
            f"   They remain only in their correct conditional (allOf/anyOf) blocks.",
            "WARN",
        )
        log(
            f"{'='*60}\n",
            "WARN",
        )

        # Update final_schema with cleaned version
        final_schema["configSchema"] = cleaned_config_schema
    else:
        log(f"✅ No conditional field conflicts found", "SUCCESS")

    # Check if content actually differs (not just formatting)
    # If content is identical, skip writing to preserve original formatting
    if original_content:
        try:
            existing_parsed = json.loads(original_content)
            # Compare parsed JSON objects (ignores formatting differences)
            if existing_parsed == final_schema:
                log(
                    f"No content changes for {name} (skipping to preserve formatting)",
                    "SUCCESS",
                )
                return
        except (json.JSONDecodeError, KeyError):
            # If we can't parse or compare, proceed with update
            log("Could not compare content, proceeding with update", "WARN")

    if dry_run:
        log(f"\n[DRY RUN] Would update {file_path}", "WARN")
        log("Run with -update flag to apply changes", "WARN")
    else:
        # Format preserving original style if possible
        formatted = format_json_preserve(final_schema, original_content)

        # Write the file
        with open(file_path, "w") as f:
            f.write(formatted)
            f.write("\n")  # Ensure trailing newline

        log(f"Updated schema file: {file_path}", "SUCCESS")


def process_integration(name: str, selector: str, should_update: bool) -> None:
    """Process a single integration."""
    directory = f"./{CONFIG_DIR}/{selector}s/{name}"
    if not os.path.isdir(directory):
        log(f"Directory not found: {directory}", "ERROR")
        return

    if name in EXCLUDED_DEST:
        log(f"Skipping excluded destination: {name}", "INFO")
        return

    log(f"\n{'='*60}", "INFO")
    log(f"Processing {name} ({selector})", "INFO")
    log(f"{'='*60}", "INFO")

    # Read config files
    file_selectors = ["db-config.json", "ui-config.json", "schema.json"]
    available_files = os.listdir(directory)
    file_content = {}

    for file_selector in file_selectors:
        if file_selector in available_files:
            file_content.update(get_json_from_file(f"{directory}/{file_selector}"))

    ui_config = file_content.get("uiConfig")
    db_config = file_content.get("config")

    if not ui_config:
        log(f"No ui-config found for {name}, skipping", "WARN")
        return

    # Generate schema using original generator
    log(f"Generating schema for {name}...", "INFO")
    generated_schema = generate_schema(ui_config, db_config, name, selector)

    # Update schema file
    update_schema_file(selector, name, generated_schema, dry_run=not should_update)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Schema Generator V2 - Improved version that preserves existing fields"
    )
    group = parser.add_mutually_exclusive_group()
    parser.add_argument(
        "selector",
        metavar="selector",
        type=str,
        help="Enter whether -name is a source or destination",
    )
    parser.add_argument(
        "-update",
        action="store_true",
        help="Will update existing schema with changes (default: dry-run)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output",
    )
    group.add_argument(
        "-name", metavar="name", type=str, help="Enter the folder name under selector"
    )
    group.add_argument(
        "-all",
        action="store_true",
        help="Will run for all entities under selector",
    )

    args = parser.parse_args()
    selector = args.selector
    should_update = args.update
    VERBOSE = args.verbose

    if not should_update:
        log("\n🔍 DRY RUN MODE - No files will be modified", "WARN")
        log("Add -update flag to apply changes\n", "WARN")

    dir_path = f"./{CONFIG_DIR}/{selector}s"

    if args.all:
        if not os.path.isdir(dir_path):
            log(f"No {selector}s folder found", "ERROR")
            exit(1)

        current_items = os.listdir(dir_path)
        for name in current_items:
            try:
                process_integration(name, selector, should_update)
            except Exception as e:
                log(f"Error processing {name}: {e}", "ERROR")
                if VERBOSE:
                    import traceback

                    traceback.print_exc()
    else:
        name = args.name
        if not name:
            log("Please provide -name or -all", "ERROR")
            exit(1)
        process_integration(name, selector, should_update)

    log("\n✨ Done!", "SUCCESS")
