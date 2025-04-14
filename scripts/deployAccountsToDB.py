import json
import os
import jsondiff
from constants import CONFIG_DIR
from utils import (
    get_config_definition,
    get_file_content,
    update_config_definition,
    create_config_definition,
)


def update_account_db(baseUrl, auth, item_name):
    final_report = []
    persisted_data = get_config_definition(baseUrl, "accounts", "", auth)
    if persisted_data.status_code == 200:
        accountDefinitions = json.loads(persisted_data.text)
    else:
        print(f"Error: Unable to fetch account definitions from the control plane.")
        return
    supported_categories = ["destinations", "sources"]
    for category in supported_categories:
        if item_name:
            current_items = [item_name]
        else:
            current_items = os.listdir(f"./{CONFIG_DIR}/{category}")
        for item in current_items:
            if not os.path.isdir(f"./{CONFIG_DIR}/{category}/{item}/accounts"):
                continue
            authentication_types = os.listdir(
                f"./{CONFIG_DIR}/{category}/{item}/accounts"
            )
            for authentication_type in authentication_types:
                if not os.path.isdir(
                    f"./{CONFIG_DIR}/{category}/{item}/accounts/{authentication_type}"
                ):
                    continue
                directory = (
                    f"./{CONFIG_DIR}/{category}/{item}/accounts/{authentication_type}"
                )
                updated_data = get_file_content(directory)
                flag = False
                for accountDefinition in accountDefinitions:
                    if accountDefinition["name"] == updated_data["name"]:
                        flag = True
                        diff = jsondiff.diff(
                            accountDefinition,
                            updated_data,
                            marshal=True,
                        )
                        if len(diff.keys()) > 0:
                            # changes exist
                            status, _ = update_config_definition(
                                "accounts", updated_data["name"], updated_data
                            )
                            final_report.append(
                                {
                                    "name": updated_data["name"],
                                    "action": "update",
                                    "status": status,
                                }
                            )
                        else:
                            final_report.append(
                                {
                                    "name": updated_data["name"],
                                    "action": "N/A",
                                    "status": "",
                                }
                            )
                if flag == False:
                    status, _ = create_config_definition(
                        baseUrl, "accounts", updated_data, auth
                    )
                    final_report.append(
                        {
                            "name": updated_data["name"],
                            "action": "create",
                            "status": status,
                        }
                    )
    return final_report
