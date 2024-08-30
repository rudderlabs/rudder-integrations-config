# THIS IS A TEMPORARY SCRIPT TO MIGRATE LEGACY CONSENT CONFIGURATION FIELDS
# IT NEEDS TO BE DELETED ONCE THE MIGRATION OF ALL THE DESTINATIONS IS DONE
import os
import json
from utils import get_json_from_file, get_formatted_json, is_old_format


def update_test_file(supported_source_types, name):
    test_file_path = f"./test/data/validation/destinations/{name}.json"
    test_data = []
    if os.path.exists(test_file_path):
        test_data = get_json_from_file(test_file_path)

    # Clean up the test cases with existing consent management fields
    for test in test_data:
        if (
            "oneTrustCookieCategories" in test["config"]
            and type(test["config"]["oneTrustCookieCategories"]) != dict
        ):
            del test["config"]["oneTrustCookieCategories"]
            if "err" in test:
                test["err"] = [
                    err for err in test["err"] if "oneTrustCookieCategories" not in err
                ]
        if "ketchConsentPurposes" in test["config"] != dict:
            del test["config"]["ketchConsentPurposes"]
            if "err" in test:
                test["err"] = [
                    err for err in test["err"] if "ketchConsentPurposes" not in err
                ]

        if "err" in test and len(test["err"]) == 0:
            del test["err"]

    # Filter all the tests that have legacy consent management fields
    test_data = [
        test
        for test in test_data
        if "oneTrustCookieCategories" not in test["config"]
        and "ketchConsentPurposes" not in test["config"]
    ]

    # Filter invalid tests
    test_data = [
        test
        for test in test_data
        if ("result" in test and test["result"] is not False)
        or ("err" in test and len(test["err"]) > 0)
    ]

    success_test = {"config": {}}
    # Find a successful test case to clone
    for test in test_data:
        if test.get("result", False) and not test.get("err", None):
            success_test = test
            break

    # Positive test cases for oneTrustCookieCategories and ketchConsentPurposes
    # exploring different data formats and types
    one_trust_success_scenarios = [
        [{"oneTrustCookieCategory": "C0001"}, {"oneTrustCookieCategory": "C0002"}],
        [{"oneTrustCookieCategory": "C0003"}, {"oneTrustCookieCategory": "C0004"}],
        [{"oneTrustCookieCategory": ""}],
        [],
        [{"oneTrustCookieCategory": "env.ENVIRONMENT_VARIABLE"}],
        [
            {
                "oneTrustCookieCategory": "{"
                + "{"
                + " event.properties.prop1 || 'val' "
                + "}"
                + "}"
            }
        ],
    ]

    ketch_success_scenarios = [
        [{"purpose": "P1"}, {"purpose": "P2"}],
        [{"purpose": "P3"}, {"purpose": "P4"}],
        [{"purpose": ""}],
        [],
        [{"purpose": "env.ENVIRONMENT_VARIABLE"}],
        [{"purpose": "{" + "{" + " event.properties.prop1 || 'val' " + "}" + "}"}],
    ]

    # Prepare the test cases involving each source type
    s_idx = 0
    while s_idx < len(one_trust_success_scenarios):
        # Clone the successful test case and update the consent management fields
        success_test_clone = json.loads(json.dumps(success_test))

        success_test_clone["config"]["oneTrustCookieCategories"] = {}
        success_test_clone["config"]["ketchConsentPurposes"] = {}

        for source_type in supported_source_types:
            success_test_clone["config"]["oneTrustCookieCategories"][source_type] = (
                one_trust_success_scenarios[s_idx % len(one_trust_success_scenarios)]
            )
            success_test_clone["config"]["ketchConsentPurposes"][source_type] = (
                ketch_success_scenarios[s_idx % len(one_trust_success_scenarios)]
            )
            s_idx += 1

        success_test_clone["result"] = True
        test_data.append(success_test_clone)

    # Negative test case where oneTrustCookieCategories and ketchConsentPurposes are not objects
    # We don't want to repeat this scenario for each source type
    failure_test_1 = json.loads(json.dumps(success_test))
    failure_test_1["config"]["oneTrustCookieCategories"] = [
        {"oneTrustCookieCategory": "C0001"},
        {"oneTrustCookieCategory": "C0002"},
    ]
    failure_test_1["config"]["ketchConsentPurposes"] = [
        {"purpose": "P1"},
        {"purpose": "P2"},
    ]
    failure_test_1["result"] = False
    failure_test_1["err"] = [
        "oneTrustCookieCategories must be object",
        "ketchConsentPurposes must be object",
    ]

    test_data.append(failure_test_1)

    # Negative test cases for oneTrustCookieCategories and ketchConsentPurposes
    one_trust_failure_scenarios = [
        {
            "input": [
                {
                    "oneTrustCookieCategory": "more than 100 characters string - AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
                },
                {"oneTrustCookieCategory": "C0004"},
            ],
            "error": [
                'oneTrustCookieCategories.ASDF.0.oneTrustCookieCategory must match pattern "(^\\{\\{.*\\|\\|(.*)\\}\\}$)|(^env[.].+)|^(.{0,100})$"',
            ],
        },
        {
            "input": [
                {"oneTrustCookieCategory": {"not": "a string"}},
                {"oneTrustCookieCategory": "C0004"},
            ],
            "error": [
                "oneTrustCookieCategories.ASDF.0.oneTrustCookieCategory must be string"
            ],
        },
        {
            "input": {"not": "an array"},
            "error": ["oneTrustCookieCategories.ASDF must be array"],
        },
        {
            "input": ["not an object", {"oneTrustCookieCategory": "C0004"}],
            "error": ["oneTrustCookieCategories.ASDF.0 must be object"],
        },
    ]

    ketch_failure_scenarios = [
        {
            "input": [
                {
                    "purpose": "more than 100 characters string - AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
                },
                {"purpose": "P4"},
            ],
            "error": [
                'ketchConsentPurposes.ASDF.0.purpose must match pattern "(^\\{\\{.*\\|\\|(.*)\\}\\}$)|(^env[.].+)|^(.{0,100})$"',
            ],
        },
        {
            "input": [{"purpose": {"not": "a string"}}, {"purpose": "P4"}],
            "error": ["ketchConsentPurposes.ASDF.0.purpose must be string"],
        },
        {
            "input": {"not": "an array"},
            "error": ["ketchConsentPurposes.ASDF must be array"],
        },
        {
            "input": ["not an object", {"purpose": "P4"}],
            "error": ["ketchConsentPurposes.ASDF.0 must be object"],
        },
    ]

    s_idx = 0
    failure_tcs = []
    while s_idx < len(one_trust_failure_scenarios):
        failure_test_clone = json.loads(json.dumps(success_test))
        failure_tcs.append(failure_test_clone)

        failure_test_clone["err"] = []
        failure_test_clone["config"]["oneTrustCookieCategories"] = {}

        for source_type in supported_source_types:
            if s_idx >= len(one_trust_failure_scenarios):
                break
            failure_test_clone["config"]["oneTrustCookieCategories"][source_type] = (
                one_trust_failure_scenarios[s_idx]["input"]
            )
            failure_test_clone["err"].extend(
                [
                    x.replace("ASDF", source_type)
                    for x in one_trust_failure_scenarios[s_idx]["error"]
                ]
            )

            s_idx += 1

        failure_test_clone["result"] = False

    s_idx = 0
    tc_idx = 0
    while s_idx < len(ketch_failure_scenarios):
        failure_test_clone = failure_tcs[tc_idx]
        tc_idx += 1

        failure_test_clone["config"]["ketchConsentPurposes"] = {}

        for source_type in supported_source_types:
            if s_idx >= len(ketch_failure_scenarios):
                break
            failure_test_clone["config"]["ketchConsentPurposes"][source_type] = (
                ketch_failure_scenarios[s_idx]["input"]
            )
            failure_test_clone["err"].extend(
                [
                    x.replace("ASDF", source_type)
                    for x in ketch_failure_scenarios[s_idx]["error"]
                ]
            )

            s_idx += 1

        failure_test_clone["result"] = False

        test_data.append(failure_test_clone)

    # write to file
    with open(test_file_path, "w") as f:
        f.write(get_formatted_json(test_data))


def update_schema_file(supported_source_types, name, dir_path):
    schema_file = f"./{dir_path}/{name}/schema.json"
    schema = {}

    if os.path.exists(schema_file):
        schema = get_json_from_file(schema_file)

    config_schema = None
    if "configSchema" in schema:
        config_schema = schema["configSchema"]

    if not config_schema:
        config_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {},
        }

    one_trust_cookie_categories_schema = {}
    one_trust_cookie_categories_schema["type"] = "object"
    one_trust_cookie_categories_schema["properties"] = {}
    for source_type in supported_source_types:
        one_trust_cookie_categories_schema["properties"][source_type] = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "oneTrustCookieCategory": {
                        "type": "string",
                        "pattern": "(^\\{\\{.*\\|\\|(.*)\\}\\}$)|(^env[.].+)|^(.{0,100})$",
                    }
                },
            },
        }
    config_schema["properties"][
        "oneTrustCookieCategories"
    ] = one_trust_cookie_categories_schema

    ketch_consent_schema = {}
    ketch_consent_schema["type"] = "object"
    ketch_consent_schema["properties"] = {}
    for source_type in supported_source_types:
        ketch_consent_schema["properties"][source_type] = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "purpose": {
                        "type": "string",
                        "pattern": "(^\\{\\{.*\\|\\|(.*)\\}\\}$)|(^env[.].+)|^(.{0,100})$",
                    }
                },
            },
        }
    config_schema["properties"]["ketchConsentPurposes"] = ketch_consent_schema

    schema["configSchema"] = config_schema

    with open(schema_file, "w") as f:
        f.write(get_formatted_json(schema))


def update_ui_config_file(name, dir_path):
    ui_config_file = f"./{dir_path}/{name}/ui-config.json"
    ui_config = get_json_from_file(ui_config_file)

    if is_old_format(ui_config["uiConfig"]):
        # Search for existing consent settings section
        consent_settings = None
        for section in ui_config["uiConfig"]:
            if "title" in section and section["title"] == "Consent Settings":
                consent_settings = section
                break

        gcm_config = None
        conf_index = -1
        if consent_settings:
            # Search for existing GCM settings
            conf_index = ui_config["uiConfig"].index(consent_settings)
            for group in consent_settings["fields"]:
                if "label" in group and group["label"] == "Consent management settings":
                    gcm_config = group
                    break

            # and remove the existing consent settings section
            ui_config["uiConfig"].remove(consent_settings)

        # Standard consent settings section with legacy fields
        consent_settings = {
            "title": "Consent Settings",
            "fields": [
                {
                    "type": "dynamicCustomForm",
                    "value": "oneTrustCookieCategories",
                    "label": "OneTrust Consent Category IDs",
                    "footerNote": "The support for category names is deprecated. We recommend using the category IDs instead of the names as IDs are unique and less likely to change over time, making them a more reliable choice.",
                    "customFields": [
                        {
                            "type": "textInput",
                            "placeholder": "C0001",
                            "value": "oneTrustCookieCategory",
                            "regex": "(^\\{\\{.*\\|\\|(.*)\\}\\}$)|(^env[.].+)|^(.{0,100})$",
                            "label": "Category ID",
                            "required": False,
                        }
                    ],
                    "preRequisites": {
                        "featureFlags": [
                            {"configKey": "AMP_enable-gcm", "value": False},
                            {"configKey": "AMP_enable-gcm"},
                        ],
                        "featureFlagsCondition": "or",
                    },
                },
                {
                    "type": "dynamicCustomForm",
                    "value": "ketchConsentPurposes",
                    "label": "Ketch Consent Purpose IDs",
                    "customFields": [
                        {
                            "type": "textInput",
                            "placeholder": "marketing",
                            "value": "purpose",
                            "label": "Purpose ID",
                            "regex": "(^\\{\\{.*\\|\\|(.*)\\}\\}$)|(^env[.].+)|^(.{0,100})$",
                            "required": False,
                        }
                    ],
                    "preRequisites": {
                        "featureFlags": [
                            {"configKey": "AMP_enable-gcm", "value": False},
                            {"configKey": "AMP_enable-gcm"},
                        ],
                        "featureFlagsCondition": "or",
                    },
                },
            ],
        }

        # Restore the GCM settings if it was present
        if gcm_config:
            consent_settings["fields"].append(gcm_config)

        # Restore the new consent settings in the same position
        # or append it to the end of the uiConfig
        if conf_index != -1:
            ui_config["uiConfig"].insert(conf_index, consent_settings)
        else:
            ui_config["uiConfig"].append(consent_settings)

    else:
        configuration_settings = None
        one_trust_consent_settings_found = False
        ketch_consent_settings_found = False
        one_trust_consent_settings = False
        ketch_consent_settings = False
        other_settings = None
        consent_settings = None
        consent_settings_template = None
        base_template = ui_config["uiConfig"]["baseTemplate"]

        for key in ui_config["uiConfig"]:
            if key == "baseTemplate":
                for template_entry in base_template:
                    # Search for existing consent settings sections
                    if (
                        "title" in template_entry
                        and template_entry["title"] == "Configuration settings"
                    ):
                        configuration_settings = template_entry
                        for section in template_entry["sections"]:
                            if (
                                not other_settings
                                and "title" in section
                                and section["title"] == "Other settings"
                            ):
                                other_settings = section
                                for group in section["groups"]:
                                    if "title" in group and (
                                        group["title"] == "OneTrust consent settings"
                                        or group["title"]
                                        == "OneTrust cookie consent settings"
                                    ):
                                        one_trust_consent_settings_found = True
                                        one_trust_consent_settings = group
                                    elif (
                                        "title" in group
                                        and group["title"] == "Ketch consent settings"
                                    ):
                                        ketch_consent_settings_found = True
                                        ketch_consent_settings = group

                            if (
                                not consent_settings
                                and "title" in section
                                and section["title"] == "Consent settings"
                            ):
                                consent_settings = section

                        # Remove the existing consent settings sections
                        if (
                            one_trust_consent_settings_found
                            and one_trust_consent_settings
                        ):
                            other_settings["groups"].remove(one_trust_consent_settings)

                        # Remove the existing consent settings sections
                        if ketch_consent_settings_found and ketch_consent_settings:
                            other_settings["groups"].remove(ketch_consent_settings)
            elif not consent_settings_template and key == "consentSettingsTemplate":
                consent_settings_template = ui_config["uiConfig"][key]

                for field in consent_settings_template["fields"]:
                    if (
                        "label" in field
                        and field["label"] == "OneTrust consent category IDs"
                    ):
                        one_trust_consent_settings = field
                        one_trust_consent_settings_found = True
                    elif (
                        "label" in field
                        and field["label"] == "Ketch consent purpose IDs"
                    ):
                        ketch_consent_settings = field
                        ketch_consent_settings_found = True

                # delete onetrust and ketch consent settings from the template
                if one_trust_consent_settings_found and one_trust_consent_settings:
                    consent_settings_template["fields"].remove(
                        one_trust_consent_settings
                    )
                if ketch_consent_settings_found and ketch_consent_settings:
                    consent_settings_template["fields"].remove(ketch_consent_settings)

        # Standard consent settings section with legacy fields
        new_consent_settings_section = {
            "id": "consentSettings",
            "title": "Consent settings",
            "note": "Configure consent settings for each provider here",
            "icon": "settings",
            "groups": [],
        }

        if not configuration_settings:
            configuration_settings = {
                "title": "Configuration settings",
                "note": "Manage the settings for your destination",
                "sections": [new_consent_settings_section],
            }
            base_template.append(configuration_settings)
        else:
            if consent_settings:
                configuration_settings["sections"].remove(consent_settings)

            if other_settings:
                # Insert the new consent settings section before the other settings section
                other_settings_idx = configuration_settings["sections"].index(
                    other_settings
                )
                configuration_settings["sections"].insert(
                    other_settings_idx, new_consent_settings_section
                )

                # Remove the other settings section if it's empty
                if len(other_settings["groups"]) == 0:
                    configuration_settings["sections"].remove(other_settings)
            else:
                configuration_settings["sections"].append(new_consent_settings_section)

        legacy_fields = [
            {
                "type": "tagInput",
                "label": "OneTrust consent category IDs",
                "note": "Input your OneTrust category IDs by pressing 'Enter' after each entry. The support for category names is deprecated. We recommend using the category IDs instead of the names as IDs are unique and less likely to change over time, making them a more reliable choice.",
                "configKey": "oneTrustCookieCategories",
                "tagKey": "oneTrustCookieCategory",
                "placeholder": "e.g: C0001",
                "default": [{"oneTrustCookieCategory": ""}],
                "preRequisites": {
                    "featureFlags": [
                        {"configKey": "AMP_enable-gcm", "value": False},
                        {"configKey": "AMP_enable-gcm"},
                    ],
                    "featureFlagsCondition": "or",
                },
            },
            {
                "type": "tagInput",
                "label": "Ketch consent purpose IDs",
                "note": "Input your Ketch consent purpose IDs by pressing 'Enter' after each entry.",
                "configKey": "ketchConsentPurposes",
                "tagKey": "purpose",
                "placeholder": "e.g: marketing",
                "default": [{"purpose": ""}],
                "preRequisites": {
                    "featureFlags": [
                        {"configKey": "AMP_enable-gcm", "value": False},
                        {"configKey": "AMP_enable-gcm"},
                    ],
                    "featureFlagsCondition": "or",
                },
            },
        ]

        if not consent_settings_template:
            consent_settings_template = {
                "title": "Consent settings",
                "note": "not visible in the ui",
                "fields": legacy_fields,
            }
            ui_config["uiConfig"]["consentSettingsTemplate"] = consent_settings_template
        else:
            legacy_fields.reverse()
            for field in legacy_fields:
                consent_settings_template["fields"].insert(0, field)

    with open(ui_config_file, "w") as f:
        f.write(get_formatted_json(ui_config))


def update_db_config_file(name, dir_path):
    db_config_file = f"./{dir_path}/{name}/db-config.json"

    db_config = get_json_from_file(db_config_file)
    supported_source_types = db_config["config"]["supportedSourceTypes"]

    default_config = db_config["config"]["destConfig"]["defaultConfig"]
    if "ketchConsentPurposes" in default_config:
        default_config.remove("ketchConsentPurposes")

    if "oneTrustCookieCategories" in default_config:
        default_config.remove("oneTrustCookieCategories")

    db_config["config"]["destConfig"]["defaultConfig"] = default_config

    device_mode_supported = False
    if "supportedConnectionModes" in db_config["config"]:
        for source_type in db_config["config"]["supportedConnectionModes"]:
            if (
                "device" in db_config["config"]["supportedConnectionModes"][source_type]
                or "hybrid"
                in db_config["config"]["supportedConnectionModes"][source_type]
            ):
                device_mode_supported = True
                break

    for source_type in db_config["config"]["destConfig"]:
        source_type_config = db_config["config"]["destConfig"][source_type]
        if (
            "useNativeSDK" in source_type_config
            or "useNativeSDKToSend" in source_type_config
        ):
            device_mode_supported = True
            break

    if device_mode_supported:
        include_keys = []
        if "includeKeys" in db_config["config"]:
            include_keys = db_config["config"]["includeKeys"]
        if "oneTrustCookieCategories" not in include_keys:
            include_keys.append("oneTrustCookieCategories")
        if "ketchConsentPurposes" not in include_keys:
            include_keys.append("ketchConsentPurposes")

        db_config["config"]["includeKeys"] = include_keys

    for source_type in supported_source_types:
        source_type_config = []
        if source_type in db_config["config"]["destConfig"]:
            source_type_config = db_config["config"]["destConfig"][source_type]
        else:
            print(f"Warning: {source_type} not found in destConfig for {name}")

        if "oneTrustCookieCategories" not in source_type_config:
            source_type_config.append("oneTrustCookieCategories")

        if "ketchConsentPurposes" not in source_type_config:
            source_type_config.append("ketchConsentPurposes")

        db_config["config"]["destConfig"][source_type] = source_type_config

    # update the file with new config
    with open(db_config_file, "w") as f:
        f.write(get_formatted_json(db_config))


def get_supported_source_types(name, dir_path):
    db_config_file = f"./{dir_path}/{name}/db-config.json"
    supported_source_types = []
    db_config = get_json_from_file(db_config_file)
    supported_source_types = db_config["config"]["supportedSourceTypes"]
    return supported_source_types


def restructure_legacy_consent_fields(dest_names, dir_path):
    for name in dest_names:
        # check if name is a directory
        if not os.path.isdir(f"./{dir_path}/{name}"):
            continue

        update_db_config_file(name, dir_path)
        supported_source_types = get_supported_source_types(name, dir_path)
        update_schema_file(supported_source_types, name, dir_path)
        update_test_file(supported_source_types, name)
        update_ui_config_file(name, dir_path)
