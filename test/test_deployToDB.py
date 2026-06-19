import os
import sys
import unittest

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


if __name__ == "__main__":
    unittest.main()
