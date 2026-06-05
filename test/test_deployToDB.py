import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
scripts_dir = os.path.join(parent_dir, "scripts")
sys.path.insert(0, parent_dir)
sys.path.insert(0, scripts_dir)

import deployToDB


def write_json(path, payload):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle)


class TestDeployToDBVersionsArchive(unittest.TestCase):
    def setUp(self):
        self.original_cwd = os.getcwd()
        self.temp_dir = tempfile.mkdtemp(prefix="deploy-to-db-test-")
        os.chdir(self.temp_dir)

        self.original_config_dir = deployToDB.CONFIG_DIR
        deployToDB.CONFIG_DIR = "local-configs"

        deployToDB.CONTROL_PLANE_URL = "https://example.test"
        deployToDB.AUTH = ("user", "password")

    def tearDown(self):
        deployToDB.CONFIG_DIR = self.original_config_dir
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)

    def _create_destination_root(self, destination_name):
        destination_dir = os.path.join(
            self.temp_dir, "local-configs", "destinations", destination_name
        )
        os.makedirs(destination_dir, exist_ok=True)

        write_json(
            os.path.join(destination_dir, "db-config.json"),
            {
                "name": "TEST_DESTINATION",
                "displayName": "Test Destination",
                "version": "1.0",
                "fallbackVersion": 1,
                "config": {
                    "supportedSourceTypes": ["web"],
                    "destConfig": {"defaultConfig": ["apiKey"]},
                },
            },
        )
        write_json(os.path.join(destination_dir, "schema.json"), {"configSchema": {}})
        write_json(os.path.join(destination_dir, "ui-config.json"), {"uiConfig": {}})

        return destination_dir

    def test_build_versions_archive_returns_empty_map_when_directory_missing(self):
        destination_dir = self._create_destination_root("test_destination")
        archive = deployToDB.build_versions_archive(destination_dir)
        self.assertEqual(archive, {})

    def test_build_versions_archive_reads_versions_directory(self):
        destination_dir = self._create_destination_root("test_destination")
        version_dir = os.path.join(destination_dir, "versions", "1")
        os.makedirs(version_dir, exist_ok=True)

        write_json(
            os.path.join(version_dir, "db-config.json"),
            {
                "version": {
                    "number": "1.3",
                    "status": "retired",
                    "retirementDate": "2026-10-01",
                    "migrationDocsUrl": "https://example.test/migrate",
                },
                "config": {
                    "supportedSourceTypes": ["web"],
                    "destConfig": {"defaultConfig": ["apiKey"]},
                },
            },
        )
        write_json(
            os.path.join(version_dir, "schema.json"),
            {"configSchema": {"type": "object"}},
        )
        write_json(
            os.path.join(version_dir, "ui-config.json"),
            {"uiConfig": {"type": "tabs", "tabs": []}},
        )

        archive = deployToDB.build_versions_archive(destination_dir)

        self.assertEqual(
            archive,
            {
                "1": {
                    "number": "1.3",
                    "status": "retired",
                    "retirementDate": "2026-10-01",
                    "migrationDocsUrl": "https://example.test/migrate",
                    "config": {
                        "supportedSourceTypes": ["web"],
                        "destConfig": {"defaultConfig": ["apiKey"]},
                    },
                    "configSchema": {"type": "object"},
                    "uiConfig": {"type": "tabs", "tabs": []},
                }
            },
        )

    def test_update_diff_db_emits_versions_and_clears_removed_major(self):
        self._create_destination_root("test_destination")

        persisted_by_name = {
            "TEST_DESTINATION": {
                "name": "TEST_DESTINATION",
                "displayName": "Test Destination",
                "version": "1.0",
                "fallbackVersion": 1,
                "config": {
                    "supportedSourceTypes": ["web"],
                    "destConfig": {"defaultConfig": ["apiKey"]},
                },
                "configSchema": {},
                "uiConfig": {},
                "versions": {
                    "1": {
                        "number": "1.0",
                        "status": "supported",
                        "config": {
                            "supportedSourceTypes": ["web"],
                            "destConfig": {"defaultConfig": ["apiKey"]},
                        },
                        "configSchema": {},
                        "uiConfig": {},
                    }
                },
            }
        }

        captured_payload = {}

        def mock_update(*_args, **kwargs):
            payload = kwargs.get("fileData", _args[3] if len(_args) > 3 else {})
            captured_payload.update(payload)
            return "DRY RUN - Would update", {}

        with patch.object(
            deployToDB, "update_config_definition", side_effect=mock_update
        ):
            report = deployToDB.update_diff_db(
                selector="destination",
                persisted_by_name=persisted_by_name,
                item_name="test_destination",
                dry_run=True,
                verbose=False,
            )

        self.assertEqual(report[0]["action"], "update")
        self.assertIn("versions", report[0]["diff"])
        self.assertEqual(captured_payload["versions"], {})
        self.assertEqual(captured_payload["version"], "1.0")
        self.assertEqual(captured_payload["fallbackVersion"], 1)


if __name__ == "__main__":
    unittest.main()
