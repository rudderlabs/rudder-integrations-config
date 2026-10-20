import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from validate_account_definitions import validate_account_field_coverage


class TestAccountFieldCoverage(unittest.TestCase):
    def _write_destination(
        self, root, default_config, secret_keys, credential_delivery=None
    ):
        destination = Path(root) / "test_destination"
        account = destination / "accounts" / "api_key"
        account.mkdir(parents=True)
        (destination / "db-config.json").write_text(
            json.dumps(
                {
                    "config": {
                        "destConfig": {"defaultConfig": default_config},
                        "secretKeys": secret_keys,
                    }
                }
            )
        )
        account_config = {
            "optionFields": ["apiKeyName"],
            "secretFields": ["apiKeyValue"],
        }
        if credential_delivery:
            account_config["credentialDelivery"] = credential_delivery
        (account / "db-config.json").write_text(
            json.dumps(
                {
                    "name": "DESTINATION_TEST_API_KEY",
                    "authenticationType": "api_key",
                    "config": account_config,
                }
            )
        )
        return destination

    def test_accepts_explicit_delivery_account_credentials_without_mirroring(self):
        with tempfile.TemporaryDirectory() as root:
            destination = self._write_destination(
                root, [], [], credential_delivery="deliveryAccount"
            )

            self.assertTrue(validate_account_field_coverage(destination))

    def test_requires_mirroring_without_explicit_delivery_account_contract(self):
        with tempfile.TemporaryDirectory() as root:
            destination = self._write_destination(root, [], [])

            self.assertFalse(validate_account_field_coverage(destination))

    def test_rejects_partially_mirrored_account_fields(self):
        with tempfile.TemporaryDirectory() as root:
            destination = self._write_destination(root, ["apiKeyName"], [])

            self.assertFalse(validate_account_field_coverage(destination))

    def test_accepts_mirrored_account_fields_in_destination_metadata(self):
        with tempfile.TemporaryDirectory() as root:
            destination = self._write_destination(
                root,
                ["apiKeyName", "apiKeyValue"],
                ["apiKeyValue"],
            )

            self.assertTrue(validate_account_field_coverage(destination))


if __name__ == "__main__":
    unittest.main()
