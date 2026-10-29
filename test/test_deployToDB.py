import json
import os
import sys
import tempfile
import unittest
from unittest import mock

# Import the deploy script as a top-level module: it resolves its sibling
# modules (`constants`, `utils`) relative to the scripts directory, so that
# directory must be on the path.
SCRIPTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"
)
sys.path.insert(0, SCRIPTS_DIR)

import deployToDB


class TestDeployBlackList(unittest.TestCase):
    """The test destination must never reach production but should deploy
    everywhere else; the gate keys off the propagated environment, not the URL."""

    def test_black_listed_skipped_only_on_production(self):
        # Directory name is compared case-insensitively against the black list.
        self.assertTrue(deployToDB.is_black_listed("test_destination", "production"))
        self.assertTrue(deployToDB.is_black_listed("TEST_DESTINATION", "production"))

    def test_black_listed_deploys_on_non_production(self):
        # Only an exact "production" match skips; anything else deploys it.
        for environment in ("development", "staging", None, "PRODUCTION", "prod"):
            self.assertFalse(
                deployToDB.is_black_listed("test_destination", environment),
                f"should not skip on environment={environment!r}",
            )

    def test_regular_destination_never_black_listed(self):
        for environment in ("development", "staging", "production"):
            self.assertFalse(deployToDB.is_black_listed("active_campaign", environment))


class TestEnvironmentValidation(unittest.TestCase):
    """`--environment` is required and validated, so a missing or misspelled
    value fails loudly rather than silently bypassing the production skip."""

    def _parse(self, *extra):
        argv = ["deployToDB.py", "http://localhost:5050", "user", "pass", *extra]
        with mock.patch.object(sys, "argv", argv):
            return deployToDB.get_command_line_arguments()

    def test_valid_environment_is_returned(self):
        # environment is the last element of the returned tuple.
        self.assertEqual(self._parse("--environment", "production")[-1], "production")

    def test_missing_environment_exits(self):
        with self.assertRaises(SystemExit):
            self._parse()

    def test_invalid_environment_exits(self):
        with self.assertRaises(SystemExit):
            self._parse("--environment", "prod")


class TestVersionsArchive(unittest.TestCase):
    """The archive is how a retired major reaches the control plane, so every field the advisory
    is built from has to survive the trip — not just the ones the schema requires."""

    def _write_major(self, root, major, **overrides):
        directory = os.path.join(root, "versions", str(major))
        os.makedirs(directory)
        payload = {
            "version": f"{major}.0",
            "status": "supported",
            "config": {"destConfig": {"defaultConfig": []}},
            **overrides,
        }
        with open(os.path.join(directory, "db-config.json"), "w") as handle:
            json.dump(payload, handle)
        with open(os.path.join(directory, "schema.json"), "w") as handle:
            json.dump({"configSchema": {"type": "object"}}, handle)
        with open(os.path.join(directory, "ui-config.json"), "w") as handle:
            json.dump({"uiConfig": {"baseTemplate": []}}, handle)

    def test_carries_the_retirement_advisory_fields(self):
        with tempfile.TemporaryDirectory() as root:
            self._write_major(
                root,
                1,
                status="retired",
                retirementDate="2026-06-01",
                migrationDocsUrl="https://example.com/versions",
            )

            archive = deployToDB.build_versions_archive(root)

            self.assertEqual(archive["1"]["status"], "retired")
            self.assertEqual(archive["1"]["retirementDate"], "2026-06-01")
            self.assertEqual(
                archive["1"]["migrationDocsUrl"], "https://example.com/versions"
            )

    def test_omits_advisory_fields_the_major_does_not_declare(self):
        # Absence is meaningful downstream: no retirement date means none is scheduled yet, which is
        # different from one the deploy quietly dropped.
        with tempfile.TemporaryDirectory() as root:
            self._write_major(root, 2)

            archive = deployToDB.build_versions_archive(root)

            self.assertNotIn("retirementDate", archive["2"])
            self.assertNotIn("migrationDocsUrl", archive["2"])

    def test_rejects_a_status_outside_the_lifecycle(self):
        with tempfile.TemporaryDirectory() as root:
            self._write_major(root, 3, status="deprecated")

            with self.assertRaises(ValueError):
                deployToDB.build_versions_archive(root)

    def test_no_archive_directory_yields_an_empty_archive(self):
        # Matches what the control plane stores for a definition that has never been versioned, so a
        # definition without an archive does not diff against the database on every deploy.
        with tempfile.TemporaryDirectory() as root:
            self.assertEqual(deployToDB.build_versions_archive(root), {})


if __name__ == "__main__":
    unittest.main()
