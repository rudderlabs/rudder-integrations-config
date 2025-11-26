#!/usr/bin/env python3
"""
Interactive script to add androidKotlin and iosSwift cloud mode support to destinations.

State is tracked in markdown files (docs/destinations-tracking-*.md) using status emojis:
- ⬜ Not Started
- 🟨 In Progress
- ✅ Completed

Usage:
    python3 update_destination.py --destination am --dry-run
    python3 update_destination.py --next --update
    python3 update_destination.py --resume --update
"""

import json
import os
import sys
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
import shutil

# Configuration
REPO_ROOT = Path(__file__).parent.parent.parent
DESTINATIONS_DIR = REPO_ROOT / "src" / "configurations" / "destinations"
TRACKING_DIR = Path(__file__).parent.parent / "docs"
SCHEMA_GENERATOR_V2 = Path(__file__).parent / "schemaGeneratorV2.py"

# Destinations already configured - skip these
SKIP_DESTINATIONS = {"adj", "af", "braze", "fb", "firebase", "webhook"}

# All 171 destinations that need updating (read from tracking file)
ALL_DESTINATIONS = []


class MigrationState:
    """Manages migration state by parsing markdown tracking files."""

    def __init__(self):
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        """Load state from markdown tracking files."""
        state = {
            "last_processed": None,
            "completed": [],
            "skipped": [],
            "failed": [],
            "count": 0,
        }

        if not TRACKING_DIR.exists():
            return state

        tracking_files = sorted(TRACKING_DIR.glob("destinations-tracking-*.md"))
        if not tracking_files:
            return state

        last_in_progress = None

        for tracking_file in tracking_files:
            try:
                with open(tracking_file, "r") as f:
                    for line in f:
                        line = line.strip()

                        # Parse table rows
                        if line.startswith("|"):
                            parts = [p.strip() for p in line.split("|")]
                            if len(parts) >= 3:
                                status = parts[1]
                                dest_name = parts[2]

                                # Skip header and separator rows
                                if dest_name in ["Status", "Destination", "-----", ""]:
                                    continue

                                # Skip destinations that should be excluded
                                if dest_name in SKIP_DESTINATIONS:
                                    continue

                                # Parse status emoji
                                if "✅" in status:
                                    state["completed"].append(dest_name)
                                    state["last_processed"] = dest_name
                                elif "🟨" in status:
                                    # Track the last in-progress item
                                    last_in_progress = dest_name
                                elif "⬜" in status and "⏭" in (
                                    parts[6] if len(parts) > 6 else ""
                                ):
                                    # Destinations marked as skipped in notes
                                    state["skipped"].append(dest_name)
            except Exception as e:
                print(f"Warning: Could not parse {tracking_file}: {e}")
                continue

        # If we have an in-progress item, use it as last_processed
        if last_in_progress:
            state["last_processed"] = last_in_progress

        state["count"] = len(state["completed"])
        return state

    def save(self):
        """State is persisted in markdown files, no separate save needed."""
        pass

    def mark_completed(self, destination: str):
        """Mark destination as completed."""
        if destination not in self.state["completed"]:
            self.state["completed"].append(destination)
        self.state["last_processed"] = destination
        self.state["count"] = len(self.state["completed"])
        # Update tracking document (markdown is the source of truth)
        self._update_tracking_doc(destination, "completed")

    def mark_skipped(self, destination: str):
        """Mark destination as skipped."""
        if destination not in self.state["skipped"]:
            self.state["skipped"].append(destination)
        self.state["last_processed"] = destination
        # Update tracking document (markdown is the source of truth)
        self._update_tracking_doc(destination, "skipped")

    def mark_failed(self, destination: str, error: str):
        """Mark destination as failed."""
        self.state["failed"].append({"destination": destination, "error": error})
        self.state["last_processed"] = destination
        # Update tracking document (keep as in_progress or not started)
        # Failed items should be manually reviewed
        print(f"  ⚠️  Marked as failed: {error}")

    def get_next_destination(self) -> Optional[str]:
        """Get next destination to process."""
        if not self.state["last_processed"]:
            return ALL_DESTINATIONS[0] if ALL_DESTINATIONS else None

        try:
            idx = ALL_DESTINATIONS.index(self.state["last_processed"])
            if idx + 1 < len(ALL_DESTINATIONS):
                return ALL_DESTINATIONS[idx + 1]
        except ValueError:
            pass

        return None

    def should_prompt_batch(self) -> bool:
        """Check if we've completed a batch of 20."""
        return self.state["count"] > 0 and self.state["count"] % 20 == 0

    def _update_tracking_doc(self, destination: str, status: str):
        """Update tracking document with destination status.

        Column structure (after Tests column removal):
        | Status | Destination | db-config.json | schema.json | ui-config.json | Notes |
          parts[1]  parts[2]      parts[3]         parts[4]      parts[5]        parts[6]
        """
        if not TRACKING_DIR.exists():
            return

        # Find which tracking file contains this destination
        tracking_files = sorted(TRACKING_DIR.glob("destinations-tracking-*.md"))
        if not tracking_files:
            return

        try:
            for tracking_file in tracking_files:
                with open(tracking_file, "r") as f:
                    lines = f.readlines()

                updated = False
                for i, line in enumerate(lines):
                    # Check if this line contains the destination (handle padded spacing)
                    # Pattern: | status | destination (padded) | ...
                    parts = line.split("|")
                    if (
                        len(parts) >= 6
                    ):  # Updated: now 6 columns instead of 7 (removed Tests)
                        # parts[2] contains the destination name (with padding)
                        dest_in_line = parts[2].strip()
                        if dest_in_line == destination:
                            # Update status emoji (preserve padding)
                            if status == "completed":
                                parts[1] = " ✅     "  # Match original padding
                                # Add checkmarks to columns (preserve padding)
                                parts[3] = " ✓              "  # db-config.json
                                parts[4] = " ✓           "  # schema.json
                                # ui-config.json - only if there's content
                                if parts[5].strip() == "":
                                    parts[5] = " ✓              "
                            elif status == "in_progress":
                                parts[1] = " 🟨     "  # Match original padding
                            elif status == "skipped":
                                parts[1] = " ⬜     "  # Match original padding

                            lines[i] = "|".join(parts)
                            updated = True
                            break

                if updated:
                    with open(tracking_file, "w") as f:
                        f.writelines(lines)
                    break  # Found and updated, no need to check other files

        except Exception as e:
            # Don't fail the whole operation if tracking update fails
            print(f"  ⚠️  Could not update tracking document: {e}")


class DestinationUpdater:
    """Updates destination configuration files."""

    def __init__(self, destination: str, dry_run: bool = True, verbose: bool = False):
        self.destination = destination
        self.dry_run = dry_run
        self.verbose = verbose
        self.dest_dir = DESTINATIONS_DIR / destination
        self.changes_made = []
        self.backup_files = []

    def log(self, message: str, force: bool = False):
        """Log message if verbose or forced."""
        if self.verbose or force:
            print(f"  {message}")

    def update_db_config(self) -> bool:
        """Update db-config.json with androidKotlin and iosSwift support (preserves formatting)."""
        db_config_path = self.dest_dir / "db-config.json"

        if not db_config_path.exists():
            self.log(f"❌ db-config.json not found", force=True)
            return False

        # Read original content
        with open(db_config_path, "r") as f:
            original_content = f.read()

        content = original_content
        changes = []

        # First, parse JSON to check what needs updating
        config = json.loads(content)
        source_types = config.get("config", {}).get("supportedSourceTypes", [])
        conn_modes = config.get("config", {}).get("supportedConnectionModes", {})
        dest_config = config.get("config", {}).get("destConfig", {})

        # Update supportedSourceTypes - text-based insertion
        if "android" in source_types and "androidKotlin" not in source_types:
            import re

            # Find "android" entry - match without leading newline
            pattern = r'^([ \t]*)"android"(,?)[ \t]*$'
            match = re.search(pattern, content, re.MULTILINE)
            if match:
                indent = match.group(1)  # Just spaces/tabs, no newline
                # Replace the line with android + new androidKotlin line
                old_line = match.group(0)
                new_lines = (
                    f'{indent}"android",\n{indent}"androidKotlin"{match.group(2)}'
                )
                content = content.replace(old_line, new_lines, 1)
                changes.append("Added androidKotlin to supportedSourceTypes")

        if "ios" in source_types and "iosSwift" not in source_types:
            import re

            # Find "ios" entry - match without leading newline
            pattern = r'^([ \t]*)"ios"(,?)[ \t]*$'
            match = re.search(pattern, content, re.MULTILINE)
            if match:
                indent = match.group(1)  # Just spaces/tabs, no newline
                # Replace the line with ios + new iosSwift line
                old_line = match.group(0)
                new_lines = f'{indent}"ios",\n{indent}"iosSwift"{match.group(2)}'
                content = content.replace(old_line, new_lines, 1)
                changes.append("Added iosSwift to supportedSourceTypes")

        # Update supportedConnectionModes - text-based insertion (search only in correct section)
        if "android" in conn_modes and "androidKotlin" not in conn_modes:
            import re

            # Find supportedConnectionModes section first to avoid matching wrong section
            connmodes_start = content.find('"supportedConnectionModes"')
            if connmodes_start != -1:
                # Search only within supportedConnectionModes section (next 2000 chars should be enough)
                section_size = 2000
                connmodes_section = content[
                    connmodes_start : connmodes_start + section_size
                ]
                pattern = r'^([ \t]*)"android":\s*(\[[^\]]*\])(,?)[ \t]*$'
                match = re.search(pattern, connmodes_section, re.MULTILINE)
                if match:
                    indent = match.group(1)  # Just spaces/tabs, no newline
                    array = match.group(2)
                    comma = match.group(3)
                    old_line = match.group(0)
                    new_lines = f'{indent}"android": {array},\n{indent}"androidKotlin": ["cloud"]{comma}'
                    # Replace in section, then reconstruct full content
                    modified_section = connmodes_section.replace(old_line, new_lines, 1)
                    content = (
                        content[:connmodes_start]
                        + modified_section
                        + content[connmodes_start + section_size :]
                    )
                    changes.append(
                        "Added androidKotlin to supportedConnectionModes (cloud only)"
                    )

        if "ios" in conn_modes and "iosSwift" not in conn_modes:
            import re

            # Find supportedConnectionModes section first to avoid matching wrong section
            connmodes_start = content.find('"supportedConnectionModes"')
            if connmodes_start != -1:
                # Search only within supportedConnectionModes section
                section_size = 2000
                connmodes_section = content[
                    connmodes_start : connmodes_start + section_size
                ]
                pattern = r'^([ \t]*)"ios":\s*(\[[^\]]*\])(,?)[ \t]*$'
                match = re.search(pattern, connmodes_section, re.MULTILINE)
                if match:
                    indent = match.group(1)  # Just spaces/tabs, no newline
                    array = match.group(2)
                    comma = match.group(3)
                    old_line = match.group(0)
                    new_lines = (
                        f'{indent}"ios": {array},\n{indent}"iosSwift": ["cloud"]{comma}'
                    )
                    # Replace in section, then reconstruct full content
                    modified_section = connmodes_section.replace(old_line, new_lines, 1)
                    content = (
                        content[:connmodes_start]
                        + modified_section
                        + content[connmodes_start + section_size :]
                    )
                    changes.append(
                        "Added iosSwift to supportedConnectionModes (cloud only)"
                    )

        # Update destConfig - text-based insertion (more complex due to nested arrays)
        if dest_config and "androidKotlin" not in dest_config:
            import re

            # Find "android": [...] entry within destConfig section
            # Look for the pattern after "destConfig" but match conservatively
            destconfig_start = content.find('"destConfig"')
            if destconfig_start != -1:
                # Search only within destConfig section (to end of file since it's typically last)
                destconfig_section = content[destconfig_start:]
                pattern = r'^([ \t]*)"android":\s*(\[[^\]]*\])(,?)[ \t]*$'
                match = re.search(pattern, destconfig_section, re.MULTILINE)
                if match:
                    indent = match.group(1)  # Just spaces/tabs, no newline
                    array = match.group(2)
                    comma = match.group(3)
                    old_line = match.group(0)
                    new_lines = f'{indent}"android": {array},\n{indent}"androidKotlin": ["connectionMode", "consentManagement"]{comma}'
                    # Replace in section, then reconstruct full content
                    modified_section = destconfig_section.replace(
                        old_line, new_lines, 1
                    )
                    content = content[:destconfig_start] + modified_section
                    changes.append("Added androidKotlin to destConfig")

        if dest_config and "iosSwift" not in dest_config:
            import re

            # Find "ios": [...] entry within destConfig section
            destconfig_start = content.find('"destConfig"')
            if destconfig_start != -1:
                # Search only within destConfig section (to end of file since it's typically last)
                destconfig_section = content[destconfig_start:]
                pattern = r'^([ \t]*)"ios":\s*(\[[^\]]*\])(,?)[ \t]*$'
                match = re.search(pattern, destconfig_section, re.MULTILINE)
                if match:
                    indent = match.group(1)  # Just spaces/tabs, no newline
                    array = match.group(2)
                    comma = match.group(3)
                    old_line = match.group(0)
                    new_lines = f'{indent}"ios": {array},\n{indent}"iosSwift": ["connectionMode", "consentManagement"]{comma}'
                    # Replace in section, then reconstruct full content
                    modified_section = destconfig_section.replace(
                        old_line, new_lines, 1
                    )
                    content = content[:destconfig_start] + modified_section
                    changes.append("Added iosSwift to destConfig")

        if changes:
            self.changes_made.extend(changes)

            if not self.dry_run:
                # Backup original file
                backup_path = db_config_path.with_suffix(".json.backup")
                shutil.copy2(db_config_path, backup_path)
                self.backup_files.append(backup_path)

                # Write updated content (preserving original formatting)
                with open(db_config_path, "w") as f:
                    f.write(content)

                self.log("✓ Updated db-config.json", force=True)
            else:
                self.log("✓ Would update db-config.json (dry-run)", force=True)

            return True
        else:
            self.log("✓ db-config.json already up to date", force=True)
            return False

    def update_ui_config(self) -> bool:
        """Update ui-config.json prerequisites (cloud mode only, preserves formatting)."""
        ui_config_path = self.dest_dir / "ui-config.json"

        if not ui_config_path.exists():
            self.log("⚠ ui-config.json not found (optional)", force=True)
            return False

        # Read original content
        with open(ui_config_path, "r") as f:
            original_content = f.read()

        # Parse to check format
        config = json.loads(original_content)
        ui_config = config.get("uiConfig")

        if not ui_config:
            return False

        # Handle both NEW format (baseTemplate) and OLD format (array)
        if isinstance(ui_config, list):
            # OLD format - typically doesn't have connectionMode prerequisites
            self.log("✓ OLD format ui-config (no prerequisites needed)", force=True)
            return False
        elif not isinstance(ui_config, dict) or "baseTemplate" not in ui_config:
            return False

        # Use text-based replacement for prerequisites
        content = original_content
        changes = []
        import re

        # Find all connectionMode.android with value "cloud" and add androidKotlin after
        pattern = r'(\{\s*"configKey"\s*:\s*"connectionMode\.android"\s*,\s*"value"\s*:\s*"cloud"\s*\})\s*,?\s*\n'
        matches = list(re.finditer(pattern, content))

        # Process in reverse to maintain positions
        for match in reversed(matches):
            matched_text = match.group(1)
            full_match = match.group(0)

            # Check if androidKotlin already exists after this entry
            pos = match.end()
            next_section = content[pos : pos + 200]  # Look ahead a bit
            if "connectionMode.androidKotlin" not in next_section.split("\n")[0]:
                # Detect indentation
                indent_match = re.search(r"\n(\s*)\{", full_match)
                if indent_match:
                    indent = indent_match.group(1)
                    new_entry = f',\n{indent}{{"configKey": "connectionMode.androidKotlin", "value": "cloud"}}'

                    # Replace the matched text
                    content = (
                        content[: match.start()]
                        + matched_text
                        + new_entry
                        + content[match.end() :]
                    )
                    changes.append(
                        "Added connectionMode.androidKotlin prerequisite (cloud mode)"
                    )

        # Find all connectionMode.ios with value "cloud" and add iosSwift after
        pattern = r'(\{\s*"configKey"\s*:\s*"connectionMode\.ios"\s*,\s*"value"\s*:\s*"cloud"\s*\})\s*,?\s*\n'
        matches = list(re.finditer(pattern, content))

        # Process in reverse to maintain positions
        for match in reversed(matches):
            matched_text = match.group(1)
            full_match = match.group(0)

            # Check if iosSwift already exists after this entry
            pos = match.end()
            next_section = content[pos : pos + 200]  # Look ahead a bit
            if "connectionMode.iosSwift" not in next_section.split("\n")[0]:
                # Detect indentation
                indent_match = re.search(r"\n(\s*)\{", full_match)
                if indent_match:
                    indent = indent_match.group(1)
                    new_entry = f',\n{indent}{{"configKey": "connectionMode.iosSwift", "value": "cloud"}}'

                    # Replace the matched text
                    content = (
                        content[: match.start()]
                        + matched_text
                        + new_entry
                        + content[match.end() :]
                    )
                    changes.append(
                        "Added connectionMode.iosSwift prerequisite (cloud mode)"
                    )

        if changes:
            self.changes_made.extend(changes)

            if not self.dry_run:
                # Backup original file
                backup_path = ui_config_path.with_suffix(".json.backup")
                shutil.copy2(ui_config_path, backup_path)
                self.backup_files.append(backup_path)

                # Write updated content (preserving original formatting)
                with open(ui_config_path, "w") as f:
                    f.write(content)

                self.log("✓ Updated ui-config.json", force=True)
            else:
                self.log("✓ Would update ui-config.json (dry-run)", force=True)

            return True
        else:
            self.log("✓ ui-config.json has no cloud mode prerequisites", force=True)
            return False

    def regenerate_schema(self) -> bool:
        """Regenerate schema.json using V2 schema generator."""
        if self.dry_run:
            self.log("✓ Would regenerate schema.json (dry-run)", force=True)
            return True

        try:
            cmd = [
                "python3",
                str(SCHEMA_GENERATOR_V2),
                f"-name={self.destination}",
                "-update",
                "destination",
            ]

            self.log(f"Running: {' '.join(cmd)}")
            result = subprocess.run(
                cmd, cwd=REPO_ROOT, capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                self.log("✓ Regenerated schema.json", force=True)
                self.changes_made.append("Regenerated schema.json")
                return True
            else:
                self.log(f"❌ Schema generation failed: {result.stderr}", force=True)
                return False

        except Exception as e:
            self.log(f"❌ Schema generation error: {e}", force=True)
            return False

    def revert_changes(self):
        """Revert changes by restoring backup files."""
        for backup_path in self.backup_files:
            original_path = backup_path.with_suffix("")
            if backup_path.exists():
                shutil.copy2(backup_path, original_path)
                backup_path.unlink()
                self.log(f"✓ Reverted {original_path.name}", force=True)

    def cleanup_backups(self):
        """Remove backup files after successful update."""
        for backup_path in self.backup_files:
            if backup_path.exists():
                backup_path.unlink()

    def validate_destination(self) -> tuple[bool, list[str], list[str], list[str]]:
        """Validate destination configuration after changes.

        Returns: (is_valid, errors, warnings, passed_checks)
        """
        errors = []
        warnings = []
        passed = []

        # Validate db-config.json
        db_config_path = self.dest_dir / "db-config.json"
        if not db_config_path.exists():
            errors.append("db-config.json not found")
            return False, errors, warnings, passed

        try:
            with open(db_config_path, "r") as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"db-config.json is invalid JSON: {e}")
            return False, errors, warnings, passed

        # Check supportedSourceTypes
        source_types = config.get("config", {}).get("supportedSourceTypes", [])

        if "android" in source_types:
            if "androidKotlin" in source_types:
                android_idx = source_types.index("android")
                kotlin_idx = source_types.index("androidKotlin")
                if kotlin_idx == android_idx + 1:
                    passed.append(
                        "androidKotlin in supportedSourceTypes (correct position)"
                    )
                else:
                    warnings.append(f"androidKotlin not immediately after android")
            else:
                errors.append("androidKotlin missing from supportedSourceTypes")

        if "ios" in source_types:
            if "iosSwift" in source_types:
                ios_idx = source_types.index("ios")
                swift_idx = source_types.index("iosSwift")
                if swift_idx == ios_idx + 1:
                    passed.append("iosSwift in supportedSourceTypes (correct position)")
                else:
                    warnings.append(f"iosSwift not immediately after ios")
            else:
                errors.append("iosSwift missing from supportedSourceTypes")

        # Check supportedConnectionModes
        conn_modes = config.get("config", {}).get("supportedConnectionModes", {})

        if "androidKotlin" in conn_modes:
            if conn_modes["androidKotlin"] == ["cloud"]:
                passed.append("androidKotlin has cloud mode only")
            else:
                errors.append(
                    f"androidKotlin should be ['cloud'], got {conn_modes['androidKotlin']}"
                )
        else:
            errors.append("androidKotlin missing from supportedConnectionModes")

        if "iosSwift" in conn_modes:
            if conn_modes["iosSwift"] == ["cloud"]:
                passed.append("iosSwift has cloud mode only")
            else:
                errors.append(
                    f"iosSwift should be ['cloud'], got {conn_modes['iosSwift']}"
                )
        else:
            errors.append("iosSwift missing from supportedConnectionModes")

        # Check destConfig
        dest_config = config.get("config", {}).get("destConfig", {})

        if dest_config:
            if "androidKotlin" in dest_config:
                expected = ["connectionMode", "consentManagement"]
                if dest_config["androidKotlin"] == expected:
                    passed.append("androidKotlin destConfig correct")
                else:
                    warnings.append(
                        f"androidKotlin destConfig unexpected: {dest_config['androidKotlin']}"
                    )
            else:
                errors.append("androidKotlin missing from destConfig")

            if "iosSwift" in dest_config:
                expected = ["connectionMode", "consentManagement"]
                if dest_config["iosSwift"] == expected:
                    passed.append("iosSwift destConfig correct")
                else:
                    warnings.append(
                        f"iosSwift destConfig unexpected: {dest_config['iosSwift']}"
                    )
            else:
                errors.append("iosSwift missing from destConfig")

        # Validate schema.json exists and is valid JSON
        schema_path = self.dest_dir / "schema.json"
        if not schema_path.exists():
            errors.append("schema.json not found")
        else:
            try:
                with open(schema_path, "r") as f:
                    json.load(f)
                passed.append("schema.json is valid JSON")
            except json.JSONDecodeError as e:
                errors.append(f"schema.json is invalid JSON: {e}")

        is_valid = len(errors) == 0
        return is_valid, errors, warnings, passed

    def run_npm_tests(self) -> tuple[bool, str]:
        """Run npm validation tests for this destination.

        Returns: (success, output_message)
        """
        try:
            # Note: We run validation tests without coverage checks because:
            # 1. Jest doesn't support the -d flag properly when run through npm test
            # 2. Coverage thresholds (100%) cause false failures even when all tests pass
            # 3. We only care about validation passing, not code coverage here
            cmd = [
                "npx",
                "jest",
                "test/validation.test.ts",
                "--coverage=false",
                "--silent",
            ]

            self.log(f"Running: {' '.join(cmd)}")
            result = subprocess.run(
                cmd, cwd=REPO_ROOT, capture_output=True, text=True, timeout=120
            )

            if result.returncode == 0:
                return True, "npm validation tests passed"
            else:
                return (
                    False,
                    f"npm validation tests failed:\n{result.stdout}\n{result.stderr}",
                )

        except subprocess.TimeoutExpired:
            return False, "npm tests timed out (increased to 120s)"
        except Exception as e:
            return False, f"Error running tests: {e}"

    def process(self) -> bool:
        """Process the destination update."""
        print(f"\n{'='*60}")
        print(f"Processing: {self.destination}")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'UPDATE'}")
        print(f"{'='*60}\n")

        # Check if destination exists
        if not self.dest_dir.exists():
            print(f"❌ Destination directory not found: {self.dest_dir}")
            return False

        # Update db-config.json
        db_updated = self.update_db_config()

        # Update ui-config.json (if needed)
        ui_updated = self.update_ui_config()

        # Regenerate schema.json
        if db_updated or ui_updated:
            schema_ok = self.regenerate_schema()
            if not schema_ok and not self.dry_run:
                print("\n❌ Schema regeneration failed!")
                return False

        # Show summary
        print(f"\n{'─'*60}")
        print("Changes made:")
        if self.changes_made:
            for change in self.changes_made:
                print(f"  • {change}")
        else:
            print("  • No changes needed (already up to date)")
        print(f"{'─'*60}\n")

        return True


def load_destinations_from_tracking() -> List[str]:
    """Load list of destinations from all tracking files."""
    destinations = []

    if not TRACKING_DIR.exists():
        print(f"❌ Tracking directory not found: {TRACKING_DIR}")
        return destinations

    # Find all tracking files
    tracking_files = sorted(TRACKING_DIR.glob("destinations-tracking-*.md"))
    if not tracking_files:
        print(f"❌ No tracking files found in: {TRACKING_DIR}")
        return destinations

    # Read all tracking files
    for tracking_file in tracking_files:
        with open(tracking_file, "r") as f:
            for line in f:
                line = line.strip()

                # Detect table rows
                if (
                    line.startswith("| ⬜")
                    or line.startswith("| 🟨")
                    or line.startswith("| ✅")
                ):
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) >= 3:
                        dest_name = parts[2]
                        if (
                            dest_name
                            and dest_name not in SKIP_DESTINATIONS
                            and dest_name not in ["Status", "Destination", "-----"]
                        ):
                            destinations.append(dest_name)

    return destinations


def print_validation_summary(
    is_valid: bool, errors: list, warnings: list, passed: list
):
    """Print validation results summary."""
    print(f"\n{'='*60}")
    print("Validation Results")
    print(f"{'='*60}\n")

    if passed:
        print("✅ PASSED:")
        for msg in passed:
            print(f"  • {msg}")
        print()

    if warnings:
        print("⚠️  WARNINGS:")
        for msg in warnings:
            print(f"  • {msg}")
        print()

    if errors:
        print("❌ ERRORS:")
        for msg in errors:
            print(f"  • {msg}")
        print()

    if is_valid:
        print("✅ Overall: VALID")
    else:
        print("❌ Overall: INVALID")

    print(f"{'='*60}\n")


def interactive_prompt(state: MigrationState, updater: "DestinationUpdater") -> str:
    """Show interactive prompt and get user response.

    New workflow:
    1. Ask if user wants to run validation
    2. If yes, run validation (JSON + npm tests)
    3. If validation passes, ask to mark complete
    4. Handle batch prompts
    """
    # Check batch milestone first
    if state.should_prompt_batch():
        print(f"\n{'='*60}")
        print(f"🎉 Batch of 20 completed! ({state.state['count']} total)")
        print(f"{'='*60}")
        print("Consider creating a commit for this batch.")
        response = input("\nContinue to next destination? (y/n): ").lower().strip()
        if response != "y":
            return "quit"

    # Ask if user wants to run validation
    print("\n" + "─" * 60)
    response = input("Run validation checks? (Y/n): ").lower().strip()

    # Default to yes if empty response
    if response == "" or response in ["y", "yes"]:
        print("\n🔍 Running validation checks...")

        # Run JSON structure validation
        is_valid, errors, warnings, passed = updater.validate_destination()
        print_validation_summary(is_valid, errors, warnings, passed)

        if not is_valid:
            print("❌ Validation failed! Changes will be reverted.")
            return "revert"

        # Run npm tests
        print("🧪 Running npm validation tests...")
        test_passed, test_message = updater.run_npm_tests()

        if test_passed:
            print(f"✅ {test_message}\n")
        else:
            print(f"❌ {test_message}\n")
            print("npm tests failed! Changes will be reverted.")
            return "revert"

        print("✅ All validation checks passed!")
    else:
        print("⏭  Skipping validation checks")

    # Final decision
    print("\nOptions:")
    print("  y - Mark complete and continue to next")
    print("  n - Revert changes and continue to next")
    print("  s - Skip this destination")
    print("  q - Save state and quit")

    response = input("\nYour choice: ").lower().strip()

    if response in ["y", "yes"]:
        return "complete"
    elif response in ["n", "no"]:
        return "revert"
    elif response in ["s", "skip"]:
        return "skip"
    elif response in ["q", "quit"]:
        return "quit"
    else:
        print("Invalid choice. Please try again.")
        return interactive_prompt(state, updater)


def main():
    parser = argparse.ArgumentParser(
        description="Interactive destination updater for androidKotlin/iosSwift support"
    )
    parser.add_argument("--destination", "-d", help="Process specific destination")
    parser.add_argument(
        "--next",
        "-n",
        action="store_true",
        help="Process next destination from tracking",
    )
    parser.add_argument(
        "--resume",
        "-r",
        action="store_true",
        help="Resume from last processed destination",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Preview changes without writing (default: false)",
    )
    parser.add_argument(
        "--update",
        "-u",
        action="store_true",
        help="Actually write changes (opposite of dry-run)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Load destinations list
    global ALL_DESTINATIONS
    ALL_DESTINATIONS = load_destinations_from_tracking()

    if not ALL_DESTINATIONS:
        print("❌ No destinations found in tracking file")
        return 1

    print(f"Loaded {len(ALL_DESTINATIONS)} destinations from tracking file")

    # Initialize state
    state = MigrationState()

    # Determine dry-run mode
    dry_run = not args.update

    # Determine which destination to process
    destination = None

    if args.destination:
        destination = args.destination
    elif args.next or args.resume:
        destination = state.get_next_destination()
        if not destination:
            print("✅ All destinations processed!")
            return 0
    else:
        print("❌ Must specify --destination, --next, or --resume")
        parser.print_help()
        return 1

    # Skip if already configured
    if destination in SKIP_DESTINATIONS:
        print(f"⏭  Skipping {destination} (already configured)")
        return 0

    # Process destination
    updater = DestinationUpdater(destination, dry_run=dry_run, verbose=args.verbose)

    # Mark as in progress (only in update mode)
    if not dry_run:
        state._update_tracking_doc(destination, "in_progress")

    try:
        success = updater.process()

        if not success:
            state.mark_failed(destination, "Processing failed")
            return 1

        # Interactive prompt (only in update mode)
        if not dry_run:
            response = interactive_prompt(state, updater)

            if response == "complete":
                updater.cleanup_backups()
                state.mark_completed(destination)
                print(f"✅ Marked {destination} as completed")
                print(f"   Updated tracking document: destinations-tracking.md")
            elif response == "revert":
                updater.revert_changes()
                state.mark_skipped(destination)
                print(f"↩️  Reverted changes for {destination}")
            elif response == "skip":
                updater.revert_changes()
                state.mark_skipped(destination)
                print(f"⏭  Skipped {destination}")
            elif response == "quit":
                print(f"\n💾 Saved state. Resume with: --resume --update")
                return 0

        return 0

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted! State saved.")
        if not dry_run:
            updater.revert_changes()
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if not dry_run:
            updater.revert_changes()
        state.mark_failed(destination, str(e))
        return 1


if __name__ == "__main__":
    sys.exit(main())
