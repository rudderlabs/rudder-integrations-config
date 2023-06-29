import json
import os

# Open the JSON file
with open('scripts/data.json', 'r') as file:
    # Load the JSON data
    data = json.load(file)

# Read the content of template-db-config.json
with open('scripts/template-db-config.json', 'r') as file:
    template_db_config = json.load(file)

# Read the content of template-ui-config.json
with open('scripts/template-ui-config.json', 'r') as file:
    template_ui_config = json.load(file)

# Create db-config object with the same content
db_config = template_db_config

db_config['displayName'] = data['displayName']
formFields = data['formFields']

# Create db-config object with the same content
ui_config = template_ui_config

# Access the necessary location and update the fields array


def updateUiConfig(field):
    if "uiConfig" in ui_config and "baseTemplate" in ui_config["uiConfig"]:
        base_template = ui_config["uiConfig"]["baseTemplate"]
        if base_template and field['required'] == True:
            connection_settings = base_template[0]
            if "sections" in connection_settings and connection_settings["sections"]:
                groups = connection_settings["sections"][0]["groups"]
                if groups:
                    first_group = groups[0]
                    if "fields" in first_group:
                        first_group["fields"].append(field)
        elif base_template:
            configuration_settings = base_template[1]
            if "sections" in configuration_settings and configuration_settings["sections"]:
                groups = configuration_settings["sections"][0]["groups"]
                if groups:
                    first_group = groups[0]
                    if "fields" in first_group:
                        first_group["fields"].append(field)

        return ui_config


# Iterate over JSON objects in the array
for obj in formFields:
    # update field in ui-config
    ui_config = updateUiConfig(obj)
    # update db-config
    for key, value in obj.items():
        if key == 'configKey':
            db_config['config']['destConfig']['defaultConfig'].append(
                value)
        if key == 'secret' and value == True:
            db_config['config']['secretKeys'].append(
                db_config['config']['destConfig']['defaultConfig'][-1])


file_path = f'src/configurations/destinations/{data["displayName"]}/db-config.json'
db_config = json.dumps(db_config)
directory = os.path.dirname(file_path)
if not os.path.exists(directory):
    os.makedirs(directory)

with open(file_path, 'w') as file:
    # Write the new content
    file.write(db_config)


file_path = f'src/configurations/destinations/{data["displayName"]}/ui-config.json'
ui_config = json.dumps(ui_config)
directory = os.path.dirname(file_path)
if not os.path.exists(directory):
    os.makedirs(directory)

with open(file_path, 'w') as file:
    # Write the new content
    file.write(ui_config)
