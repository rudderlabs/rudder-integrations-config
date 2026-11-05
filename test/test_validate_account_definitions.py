import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from scripts import validate_account_definitions as validation


class AccountFieldCoverageTests(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory()
        self.addCleanup(self.workspace.cleanup)
        self.destination = Path(self.workspace.name) / "destination"
        self.destination.mkdir()
        self.account_dir = self.destination / "accounts" / "api_key"
        self.account_dir.mkdir(parents=True)
        self.root = {
            "version": "2.0",
            "config": {
                "destConfig": {"defaultConfig": ["rudderAccountId"]},
                "secretKeys": [],
            },
        }
        self.predecessor = {
            "version": "1.0",
            "config": {
                "destConfig": {"defaultConfig": ["apiKeyName", "apiKeyValue"]},
                "secretKeys": ["apiKeyValue"],
            },
        }
        self.account = {
            "name": "DESTINATION_EXAMPLE_API_KEY",
            "authenticationType": "api_key",
            "config": {
                "optionFields": ["apiKeyName"],
                "secretFields": ["apiKeyValue"],
            },
        }
        self._write(self.destination / "db-config.json", self.root)
        self._write(self.account_dir / "db-config.json", self.account)
        self._write(
            self.destination / "versions" / "1" / "db-config.json", self.predecessor
        )

    @staticmethod
    def _write(path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data))

    def validate(self):
        with contextlib.redirect_stdout(io.StringIO()):
            return validation.validate_account_field_coverage(self.destination)

    def test_account_only_major_with_mirrored_predecessor(self):
        self.assertTrue(self.validate())

    def test_mirrored_fields_still_valid_without_version_archive(self):
        self.root["version"] = "1.0"
        self.root["config"] = self.predecessor["config"]
        self._write(self.destination / "db-config.json", self.root)
        self.assertTrue(self.validate())

    def test_unversioned_or_first_major_cannot_omit_fields(self):
        for version in (None, "1.0", "invalid"):
            with self.subTest(version=version):
                if version is None:
                    self.root.pop("version", None)
                else:
                    self.root["version"] = version
                self._write(self.destination / "db-config.json", self.root)
                self.assertFalse(self.validate())

    def test_missing_or_mismatched_predecessor_is_rejected(self):
        archive = self.destination / "versions" / "1" / "db-config.json"
        archive.unlink()
        self.assertFalse(self.validate())
        self.predecessor["version"] = "3.0"
        self._write(archive, self.predecessor)
        self.assertFalse(self.validate())

    def test_predecessor_must_retain_all_fields_and_secrets(self):
        for key, field in (
            ("defaultConfig", "apiKeyName"),
            ("secretKeys", "apiKeyValue"),
        ):
            with self.subTest(key=key):
                old = self.predecessor["config"]
                section = old["destConfig"] if key == "defaultConfig" else old
                section[key].remove(field)
                self._write(
                    self.destination / "versions" / "1" / "db-config.json",
                    self.predecessor,
                )
                self.assertFalse(self.validate())
                section[key].append(field)

    def test_partial_mirroring_is_not_account_only(self):
        for field in ("apiKeyName", "apiKeyValue"):
            with self.subTest(field=field):
                fields = self.root["config"]["destConfig"]["defaultConfig"]
                fields.append(field)
                self._write(self.destination / "db-config.json", self.root)
                self.assertFalse(self.validate())
                fields.remove(field)

    def test_account_only_requires_account_reference_and_empty_secret_keys(self):
        cfg = self.root["config"]
        cfg["destConfig"]["defaultConfig"].remove("rudderAccountId")
        self._write(self.destination / "db-config.json", self.root)
        self.assertFalse(self.validate())
        cfg["destConfig"]["defaultConfig"].append("rudderAccountId")
        for secret_keys in (None, ["apiKeyValue"]):
            with self.subTest(secret_keys=secret_keys):
                if secret_keys is None:
                    cfg.pop("secretKeys", None)
                else:
                    cfg["secretKeys"] = secret_keys
                self._write(self.destination / "db-config.json", self.root)
                self.assertFalse(self.validate())

    def test_mirrored_mode_rejects_missing_secret_keys(self):
        self.root["config"]["destConfig"]["defaultConfig"].extend(
            ["apiKeyName", "apiKeyValue"]
        )
        self._write(self.destination / "db-config.json", self.root)
        self.assertFalse(self.validate())


if __name__ == "__main__":
    unittest.main()
