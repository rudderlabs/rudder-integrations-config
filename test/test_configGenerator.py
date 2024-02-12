import sys
import os
import unittest
import json

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from scripts.configGenerator import generateConfigs

with open("test/configData/inputData.json", "r") as file:
    input_data = json.load(file)

with open("test/configData/db-config.json", "r") as file:
    db_config = json.load(file)
with open("test/configData/ui-config.json", "r") as file:
    ui_config = json.load(file)


class TestConfigGenerator(unittest.TestCase):

    def test_config_generator(self):
        result = generateConfigs(input_data)
        self.assertEqual(result["db_config"], json.dumps(db_config))
        self.assertEqual(result["ui_config"], json.dumps(ui_config))


if __name__ == "__main__":
    unittest.main()
