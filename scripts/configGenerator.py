from typing import TypedDict

import json
import os
import sys

ConfigData = TypedDict("ConfigData", {"db_config": str, "ui_config": str})


def generateConfigs(data) -> ConfigData:
    # Read the content of template-db-config.json
    with open("scripts/template-db-config.json", "r") as file:
        template_db_config = json.load(file)

    # Read the content of template-ui-config.json
    with open("scripts/template-ui-config.json", "r") as file:
        template_ui_config = json.load(file)

    # Create db-config object with the same content
    db_config = template_db_config

    db_config["displayName"] = data["displayName"]
    db_config["name"] = data["displayName"]
    formFields = data["formFields"]

    # Create db-config object with the same content
    ui_config = template_ui_config

    # Access the necessary location and update the fields array

    def appendFieldsInGroups(settings, field):
        if "sections" in settings and settings["sections"]:
            groups = settings["sections"][0]["groups"]
            if groups:
                first_group = groups[0]
                if "fields" in first_group:
                    del field["required"]
                    first_group["fields"].append(field)

    def updateUiConfig(field):
        if "uiConfig" in ui_config and "baseTemplate" in ui_config["uiConfig"]:
            base_template = ui_config["uiConfig"]["baseTemplate"]
            if base_template and field["required"] == True:
                connection_settings = base_template[0]
                appendFieldsInGroups(connection_settings, field)
            elif base_template:
                configuration_settings = base_template[1]
                appendFieldsInGroups(configuration_settings, field)
            return ui_config

    # Iterate over JSON objects in the array
    for obj in formFields:
        # update field in ui-config
        ui_config = updateUiConfig(obj)
        # update db-config
        for key, value in obj.items():
            if key == "configKey":
                db_config["config"]["destConfig"]["defaultConfig"].append(value)
            if key == "secret" and value == True:
                db_config["config"]["secretKeys"].append(
                    db_config["config"]["destConfig"]["defaultConfig"][-1]
                )

    db_config = json.dumps(db_config)
    ui_config = json.dumps(ui_config)
    return {"db_config": db_config, "ui_config": ui_config}


if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else "test/configData/inputData.json"
    with open(file_path, "r") as file:
        # Load the JSON data
        data = json.load(file)

    configData = generateConfigs(data)
    file_path = f'src/configurations/destinations/{data["displayName"]}/db-config.json'
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(file_path, "w") as file:
        # Write the new content
        file.write(configData["db_config"])

    file_path = f'src/configurations/destinations/{data["displayName"]}/ui-config.json'
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(file_path, "w") as file:
        # Write the new content
        file.write(configData["ui_config"])
