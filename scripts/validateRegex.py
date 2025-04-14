import os
import json
import re
from collections import defaultdict


def validate_ui_config_file(file_path):
    try:
        with open(file_path, "r") as f:
            data = json.load(f)

        # Ensure the root data is always an object
        if not isinstance(data, dict):
            raise ValueError("Root data should be an object")

        # Check if uiConfig is an array
        ui_config = data.get("uiConfig", {})
        if isinstance(ui_config, list):
            return {"status": "old", "regexes": []}  # Mark as old config

        # If uiConfig is an object, validate the structure
        if isinstance(ui_config, dict):
            base_template = ui_config.get("baseTemplate", [])
            if not isinstance(base_template, list) or not base_template:
                raise ValueError("'baseTemplate' is missing or invalid")

            sections = base_template[0].get("sections", [])
            if not isinstance(sections, list):
                raise ValueError("'sections' should be a list")

            regexes = []
            invalid_fields = []
            # Iterate over each section
            for section in sections:
                if not isinstance(section, dict):
                    raise ValueError("Section should be a dictionary")

                groups = section.get("groups", [])
                if not isinstance(groups, list):
                    raise ValueError("'groups' in a section should be a list")

                # Iterate over each group's fields
                for group in groups:
                    if not isinstance(group, dict):
                        raise ValueError("Group should be a dictionary")

                    fields = group.get("fields", [])
                    if not isinstance(fields, list):
                        raise ValueError("'fields' in a group should be a list")

                    for field in fields:
                        if not isinstance(field, dict):
                            raise ValueError("Field should be a dictionary")

                        if field.get("type") == "textInput":
                            regex = field.get("regex")
                            regex_error_message = field.get("regexErrorMessage")
                            config_key = field.get("configKey", "unknown")

                            # Check if regex and regexErrorMessage are defined
                            if not regex or not regex_error_message:
                                invalid_fields.append(
                                    {
                                        "configKey": config_key,
                                        "error": "'regex' or 'regexErrorMessage' missing",
                                    }
                                )

                            # Check if the regex allows an empty string
                            elif re.fullmatch(regex, ""):
                                invalid_fields.append(
                                    {
                                        "configKey": config_key,
                                        "error": "'regex' allows empty string",
                                    }
                                )

                            # Collect regex for reporting if valid
                            else:
                                regexes.append(regex)

            if invalid_fields:
                return {"status": "fail", "invalidFields": invalid_fields}

            return {"status": "pass", "regexes": regexes}  # Validation passed

    except Exception as e:
        return {"status": "fail", "error": str(e)}  # Return error message


def validate_all_configs(base_path):
    invalid_directories = defaultdict(list)
    valid_directories = []
    old_configs = []

    if not os.path.exists(base_path):
        raise FileNotFoundError(
            f"The base path '{base_path}' does not exist. Please provide a valid path."
        )

    for root, dirs, files in os.walk(base_path):
        if "ui-config.json" in files:
            file_path = os.path.join(root, "ui-config.json")
            validation_result = validate_ui_config_file(file_path)

            directory_name = os.path.basename(root)

            # Separate passed, failed, and old configurations
            if validation_result["status"] == "fail":
                if "invalidFields" in validation_result:
                    for field in validation_result["invalidFields"]:
                        invalid_directories[field["error"]].append(
                            {
                                "directory": directory_name,
                                "configKey": field["configKey"],
                            }
                        )
                else:
                    invalid_directories[validation_result["error"]].append(
                        {"directory": directory_name}
                    )
            elif validation_result["status"] == "old":
                old_configs.append(directory_name)
            else:
                valid_directories.append(
                    {
                        "directory": directory_name,
                        "regexes": validation_result["regexes"],
                    }
                )

    return valid_directories, invalid_directories, old_configs


if __name__ == "__main__":
    # Define the base path where the 'destinations' folder is located
    base_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../src/configurations/destinations")
    )

    # Validate base path
    try:
        valid_dirs, invalid_dirs, old_configs = validate_all_configs(base_path)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        exit(1)

    # Output results
    print("\nValidation Summary:\n")
    print(f"Valid Directories: {len(valid_dirs)}")
    print(f"Invalid Directories: {sum(len(v) for v in invalid_dirs.values())}")
    print(f"Old Configs: {len(old_configs)}\n")

    if valid_dirs:
        print("Details of Valid Directories:")
        for entry in valid_dirs:
            print(
                f"Destination: {entry['directory']}, Regexes: {', '.join(entry['regexes'])}"
            )
        print()

    if invalid_dirs:
        print("Details of Invalid Directories:")
        for error, directories in invalid_dirs.items():
            print(f"Error: {error}")
            for entry in directories:
                print(
                    f"  - Destination: {entry['directory']}, ConfigKey: {entry.get('configKey', 'N/A')}"
                )
        print()

    if old_configs:
        print("Details of Old Configs:")
        for directory in old_configs:
            print(f"Destination: {directory}")
        print()
