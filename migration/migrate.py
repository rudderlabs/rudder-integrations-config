#!/usr/bin/env python3
import json
import os

DEST_WEBAPP_FILE_PATH = "rudder-webapp/src/components/destinations/schemas/"
DEST_CONFIG_BE_FILE_PATH = "rudder-config-backend/src/scripts/destinationConfigs/"
DEST_SCHEMA_FILE_PATH = "rudder-config-backend/src/scripts/schemaList/destinations/"

SOURCE_WEBAPP_FILE_PATH = (
    "rudder-webapp/src/components/sources/source/warehouseSource/warehouseSourceList/"
)
SOURCE_CONFIG_BE_FILE_PATH = "rudder-config-backend/src/scripts/sourceConfigs/"
# SOURCE_SCHEMA_FILE_PATH = 'rudder-config-backend/src/scripts/schemaList/destinations/'

CONFIGURATIONS_DIR_PATH = "../src/configurations"
DEST_CONFIG_PATH = f"{CONFIGURATIONS_DIR_PATH}/destinations"
SRC_CONFIG_PATH = f"{CONFIGURATIONS_DIR_PATH}/sources"


def update_destination():
    dest_list = [
        d[:-5].lower() for d in os.listdir(f"../../{DEST_CONFIG_BE_FILE_PATH}")
    ]
    for dest in dest_list:
        final_data = []
        # read db_config
        with open(f"../../{DEST_CONFIG_BE_FILE_PATH}{dest.upper()}.json", "r") as f:
            db_config = json.loads(f.read())
        print(db_config)
        final_data.append(db_config)
        print("========================")
        # read ui_config
        with open(f"../../{DEST_WEBAPP_FILE_PATH}{dest.upper()}.json", "r") as f:
            ui_config = {"uiConfig": json.loads(f.read())}
        print(ui_config)
        final_data.append(ui_config)
        print("========================")
        # read schema
        if f"{dest.upper()}.json" in os.listdir(f"../../{DEST_SCHEMA_FILE_PATH}"):
            with open(f"../../{DEST_SCHEMA_FILE_PATH}{dest.upper()}.json", "r") as f:
                schema = {"schema": json.loads(f.read())}
        else:
            schema = {"schema": None}
        print(schema)
        final_data.append(schema)
        print("========================")
        # metadata
        with open("dest_meta_template.json", "r") as f:
            metadata = json.loads(f.read())
        print(metadata)
        final_data.append(metadata)
        print("========================")

        ########################
        ## write new files
        ########################
        if dest not in os.listdir(DEST_CONFIG_PATH):
            os.system(f"mkdir {DEST_CONFIG_PATH}/{dest}")
            print(f"created directory for {dest}")

        file_names = ["db-config", "ui-config", "schema", "metadata"]
        for index, f_name in enumerate(file_names):
            print(f"writing {f_name} for {dest}...")
            with open(f"{DEST_CONFIG_PATH}/{dest}/{f_name}.json", "w") as f:
                f.write(json.dumps(final_data[index], indent=2))

        print(f"complete for {dest}...")
        print("------------------------------------------------")


def update_source():
    source_list = [
        d[:-5].lower() for d in os.listdir(f"../../{SOURCE_CONFIG_BE_FILE_PATH}")
    ]
    for source in source_list:
        final_data = []
        # read db_config
        with open(f"../../{SOURCE_CONFIG_BE_FILE_PATH}{source.upper()}.json", "r") as f:
            db_config = json.loads(f.read())
        print(db_config)
        final_data.append(db_config)
        print("========================")
        # read ui_config
        if f"{source.upper()}.json" in os.listdir(f"../../{SOURCE_WEBAPP_FILE_PATH}"):
            with open(
                f"../../{SOURCE_WEBAPP_FILE_PATH}{source.upper()}.json", "r"
            ) as f:
                ui_config = {"uiConfig": json.loads(f.read())}
        else:
            ui_config = {"uiConfig": None}
        print(ui_config)
        final_data.append(ui_config)
        print("========================")
        # read schema (we don't need schema for sources)
        # if f'{source.upper()}.json' in os.listdir(f'../../{SOURCE_SCHEMA_FILE_PATH}'):
        #     with open(f'../../{SOURCE_SCHEMA_FILE_PATH}{source.upper()}.json', 'r') as f:
        #         schema = {"schema": json.loads(f.read())}
        # else:
        schema = {"schema": None}
        print(schema)
        final_data.append(schema)
        print("========================")
        # metadata
        with open("source_meta_template.json", "r") as f:
            metadata = json.loads(f.read())
        print(metadata)
        final_data.append(metadata)
        print("========================")

        ########################
        ## write new files
        ########################
        if source not in os.listdir(SRC_CONFIG_PATH):
            os.system(f"mkdir {SRC_CONFIG_PATH}/{source}")
            print(f"created directory for {source}")

        file_names = ["db_config", "ui_config", "schema", "metadata"]
        for index, f_name in enumerate(file_names):
            print(f"writing {f_name} for {source}...")
            with open(f"{SRC_CONFIG_PATH}/{source}/{f_name}.json", "w") as f:
                f.write(json.dumps(final_data[index], indent=2))

        print(f"complete for {source}...")
        print("------------------------------------------------")


if __name__ == "__main__":
    update_destination()
    update_source()
