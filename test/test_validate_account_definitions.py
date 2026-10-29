import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from scripts.validate_account_definitions import validate_account_field_coverage


class AccountFieldCoverageTest(unittest.TestCase):
    def check_coverage(self, authentication_type, default_fields=(), secret_keys=()):
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "sample_destination"
            account = destination / "accounts" / "sample_account"
            account.mkdir(parents=True)
            (destination / "db-config.json").write_text(
                json.dumps(
                    {
                        "config": {
                            "destConfig": {"defaultConfig": list(default_fields)},
                            "secretKeys": list(secret_keys),
                        }
                    }
                )
            )
            (account / "db-config.json").write_text(
                json.dumps(
                    {
                        "name": "DESTINATION_SAMPLE_ACCOUNT",
                        "authenticationType": authentication_type,
                        "config": {
                            "optionFields": ["clientId"],
                            "secretFields": ["clientSecret"],
                        },
                    }
                )
            )
            with redirect_stdout(StringIO()):
                return validate_account_field_coverage(destination)

    def test_ordinary_accounts_require_destination_fields_and_secret_keys(self):
        self.assertFalse(self.check_coverage("api_key"))
        self.assertFalse(
            self.check_coverage("api_key", ("clientId", "clientSecret"))
        )
        self.assertTrue(
            self.check_coverage(
                "api_key", ("clientId", "clientSecret"), ("clientSecret",)
            )
        )

    def test_oauth_token_accounts_do_not_require_destination_mirroring(self):
        for authentication_type in ("oauth", "machine_oauth"):
            with self.subTest(authentication_type=authentication_type):
                self.assertTrue(self.check_coverage(authentication_type))


if __name__ == "__main__":
    unittest.main()
