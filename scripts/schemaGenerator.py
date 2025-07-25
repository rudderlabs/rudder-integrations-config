"""
Usage: schemaGenerator.py [-h] [-name name | -all] [-update] selector
    1. selector - “source” or “destination”
    2. all - runs the validator for all the selector.
    3. name - any particular source or destination name such as `google_analytics`
    3. update - updates existing schema with detected changes
Example:
    1. python3 scripts/schemaGenerator.py -name="adobe_analytics" destination
    2. python3 scripts/schemaGenerator.py -all source
"""

import os
import warnings
from enum import Enum
import argparse
from utils import (
    get_json_from_file,
    get_json_diff,
    apply_json_diff,
    get_formatted_json,
    is_old_format,
    should_add_dynamic_config_pattern,
    should_add_env_pattern,
    is_generic_fallback,
    has_explicit_dynamic_config_pattern,
    has_explicit_env_pattern,
    DEFAULT_GENERIC_FALLBACK,
    GENERIC_FALLBACK_PATTERN,
    DYNAMIC_CONFIG_REGEX_PATTERN,
    ENV_VAR_REGEX_PATTERN,
    DYNAMIC_CONFIG_SCHEMA_PATTERN,
    ENV_VAR_SCHEMA_PATTERN,
)
from constants import CONFIG_DIR
import re
import sys
import json
from pathlib import Path

EXCLUDED_DEST = ["postgres", "bq", "azure_synapse", "clickhouse", "deltalake", "kafka"]


class FieldTypeEnum(Enum):
    STRING = "string"
    OBJECT = "object"
    BOOLEAN = "boolean"
    ARRAY = "array"


def add_immutable_property(field, schema_obj):
    """If 'immutable' is set in the field, add 'rs-immutable' to the schema object."""
    if field.get("immutable", False):
        schema_obj["rs-immutable"] = True
    return schema_obj


def get_options_list_for_enum(field):
    """Creates the list of options given in field and return the list
    Args:
        field (object): Individual field in ui-config.
    Returns:
        list: list of options
    """
    options_list = []
    for i in range(0, len(field["options"])):
        if isinstance(field["options"][i], int) or isinstance(field["options"][i], str):
            options_list.append(field["options"][i])
        else:
            options_list.append(field["options"][i]["value"])
    # allow empty field in enum if field in not required.
    if (
        "default" not in field
        and "defaultOption" not in field
        and field.get("required", False) == False
    ):
        options_list.append("")
    return options_list


def generalize_regex_pattern(field):
    """Generates the pattern for schema based on the type of field.
    
    Args:
        field (object): Individual field in ui-config, includes properties such as label, type, name, regex etc.

    Returns:
        string: generated pattern for the field.
    """
    def extract_generic_fallback(regex):
        # Split on |, return the part that matches ^(.{N,M})$ for any N, M
        parts = [p.strip() for p in regex.split('|')]
        for part in parts:
            if re.match(GENERIC_FALLBACK_PATTERN, part):
                return part
        # fallback to default if not found
        return DEFAULT_GENERIC_FALLBACK

    if "regex" in field and field["regex"] and field["regex"].strip():
        existing_pattern = field["regex"].strip()
        generic_fallback = extract_generic_fallback(existing_pattern)
        # Check if the pattern already contains redundant parts
        # If it has both dynamic config/env patterns AND a generic fallback, it's redundant
        has_dynamic_config = has_explicit_dynamic_config_pattern(existing_pattern)
        has_env = has_explicit_env_pattern(existing_pattern)
        has_generic_fallback = is_generic_fallback(existing_pattern)
        # return just the generic fallback since it captures everything
        if (has_dynamic_config or has_env) and has_generic_fallback:
            return generic_fallback
        # If the existing pattern is already a generic fallback that captures everything,
        # return it as-is to avoid redundancy
        if is_generic_fallback(existing_pattern):
            return existing_pattern
        # Build the pattern based on what's needed
        pattern_parts = []
        # Add dynamic config pattern if needed
        if should_add_dynamic_config_pattern(existing_pattern):
            pattern_parts.append(DYNAMIC_CONFIG_SCHEMA_PATTERN)
        # Add environment variable pattern if needed
        if should_add_env_pattern(existing_pattern):
            pattern_parts.append(ENV_VAR_SCHEMA_PATTERN)
        # Add the existing pattern if it's not empty and not a generic fallback
        if existing_pattern and not is_generic_fallback(existing_pattern):
            pattern_parts.append(existing_pattern)
        # If no parts were added, use generic fallback
        if not pattern_parts:
            return generic_fallback
        # Join patterns with alternation
        return "|".join(pattern_parts)
    # Special case for purpose fields
    if ("value" in field and field["value"] == "purpose") or (
        "configKey" in field and field["configKey"] == "purpose"
    ):
        return DEFAULT_GENERIC_FALLBACK
    # Default fallback pattern - this already captures dynamic config and env vars
    return DEFAULT_GENERIC_FALLBACK


def is_dest_field_dependent_on_source(field, dbConfig, schema_field_name):
    """Checks if the given field is source-specific by using dbConfig.
    In dbConfig all the sources are listed in 'supportedSourceTypes',
    and their fields are listed inside 'destConfig' with the key as the source.

    Args:
        field (object): Individual field in ui-config.
        dbConfig (object): Configurations of db-config.json.
        schema_field_name (string): Specifies which key has the field's name in schema.
            For old schema types, it is 'value' else 'configKey'.

    Returns:
        boolean: True if the field is source dependent else, False.
    """
    if not dbConfig:
        return False
    # Use the correct key for the field
    key = field.get(schema_field_name, field.get('configKey', field.get('value')))
    for sourceType in dbConfig["supportedSourceTypes"]:
        if (
            sourceType in dbConfig["destConfig"]
            and key in dbConfig["destConfig"][sourceType]
        ):
            return True
    return False


def is_key_present_in_dest_config(dbConfig, key):
    """Checks if the given key is present in destConfig across all source types.

    Args:
        dbConfig (object): Destination configuration in db-config.json.
        key (string): key to be searched in destConfig tree.

    Returns:
        boolean: True if the key is present in destConfig else, False.
    """
    if not dbConfig:
        return False

    if "destConfig" in dbConfig:
        for configSection in dbConfig["destConfig"]:
            if key in dbConfig["destConfig"][configSection]:
                return True
    return False


def is_field_present_in_default_config(field, dbConfig, schema_field_name):
    """Checks if the given field is present in defaultConfig list present in dbConfig.

    Args:
        field (object): Individual field in ui-config.
        dbConfig (object): Configurations of db-config.json.
        schema_field_name (string): Specifies which key has the field's name in schema.
            For old schema types, it is 'value' else 'configKey'.

    Returns:
        boolean: True if field is in defaultConfig else False.
    """
    if not dbConfig:
        return False
    key = field.get(schema_field_name, field.get('configKey', field.get('value')))
    if (
        "destConfig" in dbConfig
        and "defaultConfig" in dbConfig["destConfig"]
        and key in dbConfig["destConfig"]["defaultConfig"]
    ):
        return True
    return False


def generate_schema_for_default_checkbox(field, dbConfig, schema_field_name):
    """Creates a schema object of defaultCheckbox.

    Args:
        field (object): Individual field in ui-config.
        dbConfig (object): Configurations of db-config.json.
        schema_field_name (string): Specifies which key has the field's name in schema.
            For old schema types, it is 'value' else 'configKey'.

    Returns:
        object
    """
    isSourceDependent = is_dest_field_dependent_on_source(
        field, dbConfig, schema_field_name
    )
    defaultCheckboxSchemaObj = {}
    if isSourceDependent:
        defaultCheckboxSchemaObj["type"] = FieldTypeEnum.OBJECT.value
        defaultCheckboxSchemaObj["properties"] = {}
        # iterates over supported sources and sets the field for that source if field is present inside that source
        for sourceType in dbConfig["supportedSourceTypes"]:
            if (
                sourceType in dbConfig["destConfig"]
                and field[schema_field_name] in dbConfig["destConfig"][sourceType]
            ):
                defaultCheckboxSchemaObj["properties"][sourceType] = {
                    "type": FieldTypeEnum.BOOLEAN.value
                }
    else:
        defaultCheckboxSchemaObj["type"] = FieldTypeEnum.BOOLEAN.value
        if "default" in field:
            defaultCheckboxSchemaObj["default"] = field["default"]
    return defaultCheckboxSchemaObj


def generate_schema_for_checkbox(field, dbConfig, schema_field_name):
    """Creates a schema object of checkbox.

    Args:
        field (object): Individual field in ui-config.
        dbConfig (object): Configurations of db-config.json.
        schema_field_name (string): Specifies which key has the field's name in schema.
            For old schema types, it is 'value' else 'configKey'.

    Returns:
        object
    """
    isSourceDependent = is_dest_field_dependent_on_source(
        field, dbConfig, schema_field_name
    )
    checkboxSchemaObj = {}
    if isSourceDependent:
        checkboxSchemaObj["type"] = FieldTypeEnum.OBJECT.value
        checkboxSchemaObj["properties"] = {}
        # iterates over supported sources and sets the field for that source if field is present inside that source
        for sourceType in dbConfig["supportedSourceTypes"]:
            if (
                sourceType in dbConfig["destConfig"]
                and field[schema_field_name] in dbConfig["destConfig"][sourceType]
            ):
                checkboxSchemaObj["properties"][sourceType] = {
                    "type": FieldTypeEnum.BOOLEAN.value
                }
    else:
        checkboxSchemaObj["type"] = FieldTypeEnum.BOOLEAN.value
        if "default" in field:
            checkboxSchemaObj["default"] = field["default"]
    add_immutable_property(field, checkboxSchemaObj)
    return checkboxSchemaObj


def generate_schema_for_textinput(field, dbConfig, schema_field_name):
    """Creates a schema object of textinput.

    Args:
        field (object): Individual field in ui-config.
        dbConfig (object): Configurations of db-config.json.
        schema_field_name (string): Specifies which key has the field's name in schema.
            For old schema types, it is 'value' else 'configKey'.

    Returns:
        object
    """
    textInputSchemaObj = {}
    isSourceDependent = is_dest_field_dependent_on_source(
        field, dbConfig, schema_field_name
    )
    if isSourceDependent:
        textInputSchemaObj["type"] = FieldTypeEnum.OBJECT.value
        textInputSchemaObj["properties"] = {}
        # iterates over supported sources and sets the field for that source if field is present inside that source
        for sourceType in dbConfig["supportedSourceTypes"]:
            if (
                sourceType in dbConfig["destConfig"]
                and field[schema_field_name] in dbConfig["destConfig"][sourceType]
            ):
                textInputSchemaObj["properties"][sourceType] = {
                    "type": FieldTypeEnum.STRING.value
                }
                if "regex" in field:
                    textInputSchemaObj["properties"][sourceType]["pattern"] = (
                        generalize_regex_pattern(field)
                    )
    else:
        textInputSchemaObj = {"type": FieldTypeEnum.STRING.value}
        if "regex" in field:
            textInputSchemaObj["pattern"] = generalize_regex_pattern(field)
    add_immutable_property(field, textInputSchemaObj)
    return textInputSchemaObj


def generate_schema_for_textarea_input(field, dbConfig, schema_field_name):
    """Creates a schema object of textareaInput.

    Args:
        field (object): Individual field in ui-config.
        dbConfig (object): Configurations of db-config.json.
        schema_field_name (string): Specifies which key has the field's name in schema.
            For old schema types, it is 'value' else 'configKey'.

    Returns:
        object
    """
    textareaInputObj = {"type": FieldTypeEnum.STRING.value}
    if "regex" in field:
        textareaInputObj["pattern"] = generalize_regex_pattern(field)
    return textareaInputObj


def generate_schema_for_single_select(field, dbConfig, schema_field_name):
    """Creates a schema object of singleSelect.

    Args:
        field (object): Individual field in ui-config.
        dbConfig (object): Configurations of db-config.json.
        schema_field_name (string): Specifies which key has the field's name in schema.
            For old schema types, it is 'value' else 'configKey'.

    Returns:
        object
    """
    singleSelectObj = {}
    if "mode" in field and field["mode"] == "multiple":
        singleSelectObj = {"type": FieldTypeEnum.ARRAY.value}
        singleSelectObj["items"] = {
            "type": FieldTypeEnum.STRING.value,
            "enum": get_options_list_for_enum(field),
        }
        if "default" or "defaultOption" in field:
            if isinstance(field["defaultOption"]["value"], list):
                singleSelectObj["default"] = field["defaultOption"]["value"]
            elif field["defaultOption"]["value"]:
                singleSelectObj["default"] = [field["defaultOption"]["value"]]
            elif "default" in field:
                singleSelectObj["default"] = field["default"]
    else:
        singleSelectObj = {"type": FieldTypeEnum.STRING.value}
        singleSelectObj["enum"] = get_options_list_for_enum(field)
        if "default" or "defaultOption" in field:
            if "defaultOption" in field:
                singleSelectObj["default"] = field["defaultOption"]["value"]
            elif "default" in field:
                singleSelectObj["default"] = field["default"]

    isSourceDependent = is_dest_field_dependent_on_source(
        field, dbConfig, schema_field_name
    )
    if isSourceDependent:
        newSingleSelectObj = {"type": FieldTypeEnum.OBJECT.value}
        newSingleSelectObj["properties"] = {}
        # iterates over supported sources and sets the field for that source if field is present inside that source
        for sourceType in dbConfig["supportedSourceTypes"]:
            if (
                sourceType in dbConfig["destConfig"]
                and field[schema_field_name] in dbConfig["destConfig"][sourceType]
            ):
                newSingleSelectObj["properties"][sourceType] = singleSelectObj
        singleSelectObj = newSingleSelectObj
    return singleSelectObj


def generate_schema_for_dynamic_custom_form(field, dbConfig, schema_field_name):
    """Creates a schema object of dynamicCustomForm.

    Args:
        field (object): Individual field in ui-config.
        dbConfig (object): Configurations of db-config.json.
        schema_field_name (string): Specifies which key has the field's name in schema.
            For old schema types, it is 'value' else 'configKey'.

    Returns:
        object
    """
    dynamicCustomFormObj = {}
    dynamicCustomFormObj["type"] = FieldTypeEnum.ARRAY.value
    dynamicCustomFormItemObj = {}
    dynamicCustomFormItemObj["type"] = FieldTypeEnum.OBJECT.value
    dynamicCustomFormItemObj["properties"] = {}
    allOfSchemaObj = {}

    # For old schema types customFields contains the children, for v2 its is rowFields
    customFieldsKey = "customFields"
    if "rowFields" in field:
        customFieldsKey = "rowFields"

    allOfSchemaObj = generate_schema_for_dynamic_custom_form_allOf(
        field[customFieldsKey], dbConfig, schema_field_name
    )

    for customField in field[customFieldsKey]:
        customFieldSchemaObj = uiTypetoSchemaFn.get(customField["type"])(
            customField, dbConfig, schema_field_name
        )
        isCustomFieldDependentOnSource = is_dest_field_dependent_on_source(
            customField, dbConfig, schema_field_name
        )

        if "preRequisites" in customField:
            continue

        if (
            "pattern" not in customFieldSchemaObj
            and not isCustomFieldDependentOnSource
            and customFieldSchemaObj["type"] == FieldTypeEnum.STRING.value
            and customField["type"] != "singleSelect"
            and customField["type"] != "dynamicSelectForm"
        ):
            customFieldSchemaObj["pattern"] = generalize_regex_pattern(customField)

        # If the custom field is source dependent, we remove the source keys as it's not required inside custom fields, rather they need to be moved to top.
        if isCustomFieldDependentOnSource:
            for sourceType in dbConfig["supportedSourceTypes"]:
                if (
                    sourceType in dbConfig["destConfig"]
                    and field[schema_field_name] in dbConfig["destConfig"][sourceType]
                ):
                    customFieldSchemaObj = customFieldSchemaObj["properties"][
                        sourceType
                    ]
                    break
        dynamicCustomFormItemObj["properties"][
            customField[schema_field_name]
        ] = customFieldSchemaObj

    if allOfSchemaObj:
        dynamicCustomFormItemObj["allOf"] = allOfSchemaObj

    dynamicCustomFormObj["items"] = dynamicCustomFormItemObj
    isSourceDependent = is_dest_field_dependent_on_source(
        field, dbConfig, schema_field_name
    )

    # If the field is source dependent, new schema object is created by setting the fields inside the source.
    if isSourceDependent:
        newDynamicCustomFormObj = {"type": FieldTypeEnum.OBJECT.value}
        newDynamicCustomFormObj["properties"] = {}
        for sourceType in dbConfig["supportedSourceTypes"]:
            if (
                sourceType in dbConfig["destConfig"]
                and field[schema_field_name] in dbConfig["destConfig"][sourceType]
            ):
                newDynamicCustomFormObj["properties"][sourceType] = dynamicCustomFormObj
        dynamicCustomFormObj = newDynamicCustomFormObj

    return dynamicCustomFormObj


def generate_schema_for_dynamic_custom_form_allOf(
    customFields, dbConfig, schema_field_name
):
    """Creates the allOf structure of schema, empty if not required.
    - Finds the list of unique preRequisites.
    - For each unique preRequisites, the properties are found by matching the current preRequisites.
    - preRequisites becomes if block and corresponding properties become then block.

    Args:
        customFields (collection): child fields from file content of ui-config.json.
        dbConfig (object): Configurations of db-config.json.
        schema_field_name (string): Specifies which key has the field's name in schema.
            For old schema types, it is 'value' else 'configKey'.

    Returns:
        object: allOf object of schema
    """
    allOfItemList = []
    preRequisitesList = []

    for field in customFields:
        if "preRequisites" not in field:
            continue
        isPresent = False
        for preRequisites in preRequisitesList:
            if compare_pre_requisite_fields(
                preRequisites, field["preRequisites"]["fields"], True
            ):
                isPresent = True
                break
        if not isPresent:
            preRequisitesList.append(field["preRequisites"]["fields"])

    for preRequisites in preRequisitesList:
        ifObj = generate_if_object(preRequisites, True)
        thenObj = {"properties": {}, "required": []}
        allOfItemObj = {"if": ifObj}

        for field in customFields:
            if "preRequisites" not in field:
                continue
            if compare_pre_requisite_fields(
                field["preRequisites"]["fields"], preRequisites, True
            ):
                fn = uiTypetoSchemaFn.get(field["type"])
                if fn is not None:
                    thenObj["properties"][field[schema_field_name]] = fn(
                        field, dbConfig, schema_field_name
                    )
                else:
                    warnings.warn(
                        f'Unknown field type: {field["type"]} in generate_schema_for_allOf, skipping.',
                        UserWarning,
                        stacklevel=2,
                    )
                if "required" in field and field["required"] == True:
                    thenObj["required"].append(field[schema_field_name])
        allOfItemObj["then"] = thenObj
        allOfItemList.append(allOfItemObj)

    # Calling anyOf to check if two conditions can be grouped as anyOf.
    allOfItemList = generate_schema_for_anyOf(allOfItemList, schema_field_name)
    return allOfItemList


def generate_schema_for_dynamic_form(field, dbConfig, schema_field_name):
    """Creates a schema object of dynamicForm.

    Args:
        field (object): Individual field in ui-config.
        dbConfig (object): Configurations of db-config.json.
        schema_field_name (string): Specifies which key has the field's name in schema.
            For old schema types, it is 'value' else 'configKey'.

    Returns:
        object
    """

    def generate_key(forFieldWithTo):
        obj = {
            "type": FieldTypeEnum.STRING.value,
        }
        if field["type"] == "dynamicSelectForm":
            if forFieldWithTo != (field.get("reverse", False) == False):
                obj["pattern"] = generalize_regex_pattern(field)
            else:
                if "defaultOption" in field:
                    obj["default"] = field["defaultOption"]["value"]
                obj["enum"] = get_options_list_for_enum(field)
        else:
            obj["pattern"] = generalize_regex_pattern(field)
        return obj

    dynamicFormSchemaObject = {}
    dynamicFormSchemaObject["type"] = FieldTypeEnum.ARRAY.value
    dynamicFormItemObject = {}
    dynamicFormItemObject["type"] = FieldTypeEnum.OBJECT.value
    dynamicFormItemObject["properties"] = {}
    dynamicFormItemObjectProps = [
        (field["keyLeft"], generate_key),
        (field["keyRight"], generate_key),
    ]
    for dynamicFromItemObjectProp in dynamicFormItemObjectProps:
        dynamicFormItemObject["properties"][dynamicFromItemObjectProp[0]] = (
            dynamicFromItemObjectProp[1](dynamicFromItemObjectProp[0] == "to")
        )
    dynamicFormSchemaObject["items"] = dynamicFormItemObject

    isSourceDependent = is_dest_field_dependent_on_source(
        field, dbConfig, schema_field_name
    )
    # If the field is source dependent, new schema object is created by setting the fields inside the source.
    if isSourceDependent:
        newDynamicFormFormObj = {"type": FieldTypeEnum.OBJECT.value}
        newDynamicFormFormObj["properties"] = {}
        for sourceType in dbConfig["supportedSourceTypes"]:
            if (
                sourceType in dbConfig["destConfig"]
                and field[schema_field_name] in dbConfig["destConfig"][sourceType]
            ):
                newDynamicFormFormObj["properties"][
                    sourceType
                ] = dynamicFormSchemaObject
        dynamicFormSchemaObject = newDynamicFormFormObj
    return dynamicFormSchemaObject


def generate_schema_for_dynamic_select_form(field, dbConfig, schema_field_name):
    """Creates a schema object of dynamicSelectForm.

    Args:
        field (object): Individual field in ui-config.
        dbConfig (object): Configurations of db-config.json.
        schema_field_name (string): Specifies which key has the field's name in schema.
            For old schema types, it is 'value' else 'configKey'.

    Returns:
        object
    """
    return generate_schema_for_dynamic_form(field, dbConfig, schema_field_name)


def generate_schema_for_mapping(field, dbConfig, schema_field_name):
    """Creates a schema object of mapping.

    Args:
        field (object): Individual field in ui-config.
        dbConfig (object): Configurations of db-config.json.
        schema_field_name (string): Specifies which key has the field's name in schema.
            For old schema types, it is 'value' else 'configKey'.

    Returns:
        object
    """
    return generate_schema_for_dynamic_form(field, dbConfig, schema_field_name)


def generate_schema_for_tag_input(field, dbConfig, schema_field_name):
    """Creates a schema object of tagInput.

    Args:
        field (object): Individual field in ui-config.
        dbConfig (object): Configurations of db-config.json.
        schema_field_name (string): Specifies which key has the field's name in schema.
            For old schema types, it is 'value' else 'configKey'.

    Returns:
        object
    """
    tagObject = {}
    tagObject["type"] = FieldTypeEnum.ARRAY.value
    tagItem = {}
    tagItem["type"] = FieldTypeEnum.OBJECT.value
    tagItemProps = {
        str(field["tagKey"]): {
            "type": FieldTypeEnum.STRING.value,
            "pattern": generalize_regex_pattern(field),
        }
    }
    tagItem["properties"] = tagItemProps
    tagObject["items"] = tagItem
    isSourceDependent = is_dest_field_dependent_on_source(
        field, dbConfig, schema_field_name
    )
    if isSourceDependent:
        tagObjectCopy = tagObject
        tagObject = {}
        tagObject = {"type": FieldTypeEnum.OBJECT.value}
        tagObject["properties"] = {}
        for sourceType in dbConfig["supportedSourceTypes"]:
            if (
                sourceType in dbConfig["destConfig"]
                and field[schema_field_name] in dbConfig["destConfig"][sourceType]
            ):
                tagObject["properties"][sourceType] = tagObjectCopy
    return tagObject


def generate_schema_for_time_range_picker(field, dbConfig, schema_field_name):
    """Creates a schema object of timeRangePicker.

    Args:
        field (object): Individual field in ui-config.
        dbConfig (object): Configurations of db-config.json.
        schema_field_name (string): Specifies which key has the field's name in schema.
            For old schema types, it is 'value' else 'configKey'.

    Returns:
        object
    """
    timeRangeObj = {}
    timeRangeObj["type"] = FieldTypeEnum.OBJECT.value
    timeRangeProps = {
        field["startTime"]["value"]: {"type": FieldTypeEnum.STRING.value},
        field["endTime"]["value"]: {"type": FieldTypeEnum.STRING.value},
    }
    timeRangeObj["properties"] = timeRangeProps
    timeRangeObj["required"] = list(timeRangeProps.keys())
    return timeRangeObj


def generate_schema_for_time_picker(field, dbConfig, schema_field_name):
    """Creates a schema object of timePicker.

    Args:
        field (object): Individual field in ui-config.
        dbConfig (object): Configurations of db-config.json.
        schema_field_name (string): Specifies which key has the field's name in schema.
            For old schema types, it is 'value' else 'configKey'.

    Returns:
        object
    """
    return {"type": FieldTypeEnum.STRING.value}


def compare_pre_requisite_fields(fieldA, fieldB, isV2=False):
    """Compares two preRequisiteFields fieldA and fieldB for each property and checks if their value matches.

    Args:
        fieldA (list or object): contains two properties representing 'name' and 'selectedValue'.
        fieldB (list or object): contains two properties representing 'name' and 'selectedValue'.
        isV2 (bool): determines if new property names should be used

    Returns:
        boolean: If all the properties have the same 'name' and 'selectedValue', then it returns True else False.
    """
    valueKey = "selectedValue"
    nameKey = "name"

    if isV2:
        valueKey = "value"
        nameKey = "configKey"

    if type(fieldA) != type(fieldB):
        return False
    elif type(fieldA) == list:
        if len(fieldA) != len(fieldB):
            return False
        for i in range(0, len(fieldA)):
            if (
                fieldA[i][nameKey] != fieldB[i][nameKey]
                or fieldA[i][valueKey] != fieldB[i][valueKey]
            ):
                return False
    else:
        if fieldA[nameKey] != fieldB[nameKey] or fieldA[valueKey] != fieldB[valueKey]:
            return False
    return True


def get_unique_pre_requisite_fields(uiConfig):
    """Returns the list of unique preRequisiteFields present in a uiConfig.

    Args:
        uiConfig (object): file content of ui-config.json.

    Returns:
        list: containing unique preRequisiteFields.
    """
    preRequisiteFieldsList = []
    for group in uiConfig:
        fields = group.get("fields", [])
        for field in fields:
            if "preRequisiteField" not in field:
                continue
            isPresent = False
            for preRequisiteField in preRequisiteFieldsList:
                if compare_pre_requisite_fields(
                    preRequisiteField, field["preRequisiteField"]
                ):
                    isPresent = True
                    break
            if not isPresent:
                preRequisiteFieldsList.append(field["preRequisiteField"])
    return preRequisiteFieldsList


def generate_if_object(preRequisiteField, isV2=False):
    """Creates an if object for the given preRequisiteField. The preRequisiteField becomes an if condition in the schema.

    Args:
        preRequisiteField (list or object): contains two properties, 'name' and 'selectedValue'.
        isV2 (bool): if it should use the v2 or the legacy property key names

    Returns:
        object: if block for given preRequisiteField.
    """
    ifObj = {"properties": {}, "required": []}
    valueKey = "selectedValue"
    nameKey = "name"

    if isV2:
        valueKey = "value"
        nameKey = "configKey"

    if type(preRequisiteField) == list:
        for field in preRequisiteField:
            ifObj["properties"][field[nameKey]] = {"const": field[valueKey]}
            ifObj["required"].append(field[nameKey])
    else:
        ifObj["properties"][preRequisiteField[nameKey]] = {
            "const": preRequisiteField[valueKey]
        }
        ifObj["required"].append(preRequisiteField[nameKey])
    return ifObj


def generate_schema_for_allOf(uiConfig, dbConfig, schema_field_name):
    """Creates the allOf structure of schema, empty if not required.
    - Finds the list of unique preRequisiteFields.
    - For each unique preRequisiteField, the properties are found by matching the current preRequisiteField.
    - preRequisiteField becomes if block and corresponding properties become then block.


    Args:
        uiConfig (object): file content of ui-config.json.
        dbConfig (object): Configurations of db-config.json.
        schema_field_name (string): Specifies which key has the field's name in schema.
            For old schema types, it is 'value' else 'configKey'.

    Returns:
        object: allOf object of schema
    """
    allOfItemList = []
    preRequisiteFieldsList = get_unique_pre_requisite_fields(uiConfig)
    for preRequisiteField in preRequisiteFieldsList:
        ifObj = generate_if_object(preRequisiteField)
        thenObj = {"properties": {}, "required": []}
        allOfItemObj = {"if": ifObj}
        for group in uiConfig:
            fields = group.get("fields", [])
            for field in fields:
                if "preRequisiteField" not in field:
                    continue
                if compare_pre_requisite_fields(
                    field["preRequisiteField"], preRequisiteField
                ):
                    fn = uiTypetoSchemaFn.get(field["type"])
                    if fn is not None:
                        thenObj["properties"][field[schema_field_name]] = fn(
                            field, dbConfig, schema_field_name
                        )
                    else:
                        warnings.warn(
                            f'Unknown field type: {field["type"]} in generate_schema_for_allOf, skipping.',
                            UserWarning,
                            stacklevel=2,
                        )
                    if "required" in field and field["required"] == True:
                        thenObj["required"].append(field[schema_field_name])
        allOfItemObj["then"] = thenObj
        allOfItemList.append(allOfItemObj)
    # Calling anyOf to check if two conditions can be grouped as anyOf.
    allOfItemList = generate_schema_for_anyOf(allOfItemList, schema_field_name)
    return allOfItemList


def get_common_and_opposite_fields(propertiesA, propertiesB, schema_field_name):
    """Takes properties of two if Objects and returns a list of common and opposite properties.
    Common properties have the same value in both A and B.

    Args:
        propertiesA (object): if block
        propertiesB (object):
        schema_field_name (string): Specifies which key has the field's name in schema.
            For old schema types, it is 'value' else 'configKey'.

    Returns:
        list, list : list of common properties and opposite properties respectively.
        None, None : if a property is absent in A or B or If a property has a different value (not opposite).

    Example:
        schema_field_name = 'value'
        propertiesA = { 'storage' : {'const' : 'S3'}, 'useStorage' : {'const': True}}
        propertiesB = { 'storage' : {'const' : 'S3'}, 'useStorage' : {'const': False}}

        Returns
        commonProperties = [{'key': 'storage', 'value':'S3'}]
        oppositeProperties = [{'key': 'useStorage', 'value': 'True'}]
    """
    keysListA = list(propertiesA.keys())
    keysListB = list(propertiesB.keys())
    commonProperties = []
    oppositeProperties = []
    for key in keysListA:
        if key not in keysListB:
            return None, None
        if propertiesA[key]["const"] == propertiesB[key]["const"]:
            commonProperties.append(
                {"key": key, schema_field_name: propertiesA[key]["const"]}
            )
        elif (
            type(propertiesA[key]["const"]) == bool
            and propertiesA[key]["const"] != propertiesB[key]["const"]
        ):
            oppositeProperties.append(
                {"key": key, schema_field_name: propertiesA[key]["const"]}
            )
        else:
            return None, None
    return commonProperties, oppositeProperties


def check_if_conditions_match(ifPropsA, ifObjectB, schema_field_name):
    """Compares the ifPropsA and ifObjectB if they have the same properties and values.

    Args:
        ifPropsA (list): consists of key and "schema_field_name" pairs.
        ifObjectB (object): if block consisting of multiple properties with the value.
        schema_field_name (string): Specifies which key has the field's name in schema.
            For old schema types, it is 'value' else 'configKey'.

    Returns:
        boolean: True if all the properties in IfPropsA are in ifObjectB with same value, else False.

    Example:
        schema_field_name = 'value'
        ifPropsA = [{'key': 'storage', 'value': 'S3'}, {'key': 'deploy', 'value': 'web'}]
        ifObjectA  = {'storage': {'const': 'S3'}, 'deploy': {'const': 'web'}}

        Returns: True
    """
    for ifProp in ifPropsA:
        if ifProp["key"] not in ifObjectB:
            return False
        if ifProp[schema_field_name] != ifObjectB[ifProp["key"]]["const"]:
            return False
    return True


def find_index_to_place_anyOf(ifProp, allOfItemList, schema_field_name):
    """Returns the index of the item in allOfItemList consisting of matching if conditions as that of ifProp.

    Args:
        ifProp (object): consists of key and "schema_field_name" pairs.
        allOfItemList (list): consists of a list of objects with "if-then" properties.
        schema_field_name (string): Specifies which key has the field's name in schema.
            For old schema types, it is 'value' else 'configKey'.

    Returns:
        int: index of if-block matching with ifProp else -1.

    Example:
        schema_field_name = 'value'
        ifProp = [{'key': 'storage', 'value': 'S3'}, {'key': 'deploy', 'value': 'web'}]
        allOfItemList = [
            {'if': {'properties': {'storage': { const: 'GCS' }}},'then': { ... }},
            {'if': {'properties': {'storage': { const: 'S3' },'deploy': { const: 'web' }}},'then': { ... }}
        ]

        Returns: 1
    """
    if not ifProp:
        return -1
    length = len(allOfItemList)
    for index in range(length):
        if "if" in allOfItemList[index] and check_if_conditions_match(
            ifProp, allOfItemList[index]["if"]["properties"], schema_field_name
        ):
            return index
    return -1


def generate_schema_for_anyOf(allOfItemList, schema_field_name):
    """Takes in two parameters allOfItemList and schema_field_name, and returns an updated allOf Items list.
    - It checks for all the pairs of allOf Items ("if-then" blocks), if their "if" conditions have an "if-else" based structure rather than "if-if".
    - Items following the "if-else" structure are deleted and replaced by an anyOf structure.

    Args:
        allOfItemList (list): consists of a list of objects with "if-then" properties.
        schema_field_name (string): Specifies which key has the field's name in schema.
            For old schema types, it is 'value' else 'configKey'.

    Returns:
        list: updated allOf Items list
    """
    length = len(allOfItemList)
    delIndices = []
    for i in range(0, length):
        for j in range(i + 1, length):
            ifPropertiesA = allOfItemList[i]["if"]["properties"]
            thenPropertiesA = allOfItemList[i]["then"]
            ifPropertiesB = allOfItemList[j]["if"]["properties"]
            thenPropertiesB = allOfItemList[j]["then"]
            commonIfProp, oppositeIfProp = get_common_and_opposite_fields(
                ifPropertiesA, ifPropertiesB, schema_field_name
            )
            if oppositeIfProp:
                anyOfObj = [{}, {}]
                for k in range(0, len(oppositeIfProp)):
                    if ifPropertiesA[oppositeIfProp[k]["key"]]["const"] == True:
                        anyOfObj[1] = thenPropertiesA
                        anyOfObj[1]["properties"][oppositeIfProp[k]["key"]] = {
                            "const": True
                        }
                        anyOfObj[1]["required"].append(oppositeIfProp[k]["key"])
                        anyOfObj[0] = thenPropertiesB
                        anyOfObj[0]["properties"][oppositeIfProp[k]["key"]] = {
                            "const": False
                        }
                    else:
                        anyOfObj[1] = thenPropertiesB
                        anyOfObj[1]["properties"][oppositeIfProp[k]["key"]] = {
                            "const": True
                        }
                        anyOfObj[1]["required"].append(oppositeIfProp[k]["key"])
                        anyOfObj[0] = thenPropertiesA
                        anyOfObj[0]["properties"][oppositeIfProp[k]["key"]] = {
                            "const": False
                        }
                # AnyOf object is placed at index of "if-then" block having same if properties as of common properties else at end.
                indexToPlace = find_index_to_place_anyOf(
                    commonIfProp, allOfItemList, schema_field_name
                )
                if indexToPlace != -1:
                    allOfItemList[indexToPlace]["then"]["anyOf"] = anyOfObj
                    delIndices.append(i)
                    delIndices.append(j)
    allOfItemList = [
        allOfItemList[index]
        for index in range(len(allOfItemList))
        if index not in delIndices
    ]
    return allOfItemList


def generate_connection_mode(dbConfig):
    """Creates the connection mode object present in new schema types.

    Args:
        dbConfig (object): Configurations of db-config.json.

    Returns:
        object
    """
    connectionObj = {"type": FieldTypeEnum.OBJECT.value}
    connectionObj["properties"] = {}
    for sourceType in dbConfig["supportedSourceTypes"]:
        if sourceType in dbConfig["supportedConnectionModes"]:
            connectionItemObj = {"type": FieldTypeEnum.STRING.value}
            connectionModesEnum = []
            length = len(dbConfig["supportedConnectionModes"][sourceType])
            for i in range(0, length):
                connectionModesEnum.append(
                    dbConfig["supportedConnectionModes"][sourceType][i]
                )
            connectionItemObj["enum"] = connectionModesEnum
            connectionObj["properties"][sourceType] = connectionItemObj
    return connectionObj


def generate_schema_properties(uiConfig, dbConfig, schemaObject, properties, selector):
    """Generates corresponding schema properties by iterating over each of the ui-config fields.

    Args:
        uiConfig (object): file content of ui-config.json.
        dbConfig (object): Configurations of db-config.json.
        schemaObject (object): schema being generated
        properties (object): properties of schema
        selector (string): either 'source' or 'destination'
    """
    if is_old_format(uiConfig):
        for group in uiConfig:
            fields = group.get("fields", [])
            for field in fields:
                if "preRequisiteField" in field:
                    continue
                generateFunction = uiTypetoSchemaFn.get(field["type"], None)
                if generateFunction:
                    # Generate schema for the field if it is defined in the destination config
                    key = field.get("configKey", field.get("value"))
                    if key and is_key_present_in_dest_config(dbConfig, key):
                        properties[key] = generateFunction(
                            field, dbConfig, "value"
                        )
                    else:
                        warnings.warn(
                            f'The field {key} is defined in ui-config.json but not in db-config.json\n',
                            UserWarning,
                            stacklevel=2,
                        )
                if field.get(
                    "required", False
                ) == True and is_field_present_in_default_config(
                    field, dbConfig, "value"
                ):
                    key = field.get("configKey", field.get("value"))
                    if key:
                        schemaObject["required"].append(key)
    else:
        if selector == "destination":
            baseTemplate = uiConfig.get("baseTemplate", [])
            sdkTemplate = uiConfig.get("sdkTemplate", {})
            consentSettingsTemplate = uiConfig.get("consentSettingsTemplate", {})
            for template in baseTemplate:
                for section in template.get("sections", []):
                    for group in section.get("groups", []):
                        for field in group.get("fields", []):
                            generateFunction = uiTypetoSchemaFn.get(field["type"], None)
                            if generateFunction:
                                key = field.get("configKey", field.get("value"))
                                # Generate schema for the field if it is defined in the destination config
                                if key and is_key_present_in_dest_config(
                                    dbConfig, key
                                ):
                                    properties[key] = generateFunction(
                                        field, dbConfig, "configKey"
                                    )
                                else:
                                    warnings.warn(
                                        f'The field {key} is defined in ui-config.json but not in db-config.json\n',
                                        UserWarning,
                                        stacklevel=2,
                                    )
                            if (
                                template.get("title", "") == "Initial setup"
                                and is_field_present_in_default_config(
                                    field, dbConfig, "configKey"
                                )
                                and "preRequisites" not in field
                            ):
                                key = field.get("configKey", field.get("value"))
                                if key:
                                    schemaObject["required"].append(key)

            for field in sdkTemplate.get("fields", []):
                generateFunction = uiTypetoSchemaFn.get(field["type"], None)
                if generateFunction:
                    key = field.get("configKey", field.get("value"))
                    # Generate schema for the field if it is defined in the destination config
                    if key and is_key_present_in_dest_config(dbConfig, key):
                        properties[key] = generateFunction(
                            field, dbConfig, "configKey"
                        )
                    else:
                        warnings.warn(
                            f'The field {key} is defined in ui-config.json but not in db-config.json\n',
                            UserWarning,
                            stacklevel=2,
                        )

                if field.get(
                    "required", False
                ) == True and is_field_present_in_default_config(
                    field, dbConfig, "configKey"
                ):
                    key = field.get("configKey", field.get("value"))
                    if key:
                        schemaObject["required"].append(key)

            for field in consentSettingsTemplate.get("fields", []):
                generateFunction = uiTypetoSchemaFn.get(field["type"], None)
                if generateFunction:
                    key = field.get("configKey", field.get("value"))
                    properties[key] = generateFunction(
                        field, dbConfig, "configKey"
                    )
                if field.get(
                    "required", False
                ) == True and is_field_present_in_default_config(
                    field, dbConfig, "configKey"
                ):
                    key = field.get("configKey", field.get("value"))
                    if key:
                        schemaObject["required"].append(key)

            # default properties in new ui-config based schemas.
            if is_key_present_in_dest_config(dbConfig, "useNativeSDK"):
                schemaObject["properties"]["useNativeSDK"] = (
                    generate_schema_for_checkbox(
                        {"type": "checkbox", "value": "useNativeSDK"}, dbConfig, "value"
                    )
                )
            schemaObject["properties"]["connectionMode"] = generate_connection_mode(
                dbConfig
            )
        else:
            # for sources
            def generate_config_props(config):
                for group in config:
                    fields = group.get("fields", [])
                    for field in fields:
                        generateFunction = uiTypetoSchemaFn.get(field["type"], None)
                        if generateFunction:
                            key = field.get("configKey", field.get("value"))
                            properties[key] = generateFunction(
                                field, dbConfig, "value"
                            )

            auth = uiConfig.get("auth", None)
            config = uiConfig.get("config", [])
            if auth:
                type = auth.get("type")
                if type == "form":
                    auth_config = auth.get("config", [])
                    generate_config_props(auth_config)

            generate_config_props(config)


def generate_schema(uiConfig, dbConfig, name, selector):
    """Returns the schema generated from given uiConfig and dbConfig.

    Args:
        uiConfig (object): file content of ui-config.json.
        dbConfig (object): Configurations of db-config.json.
        name (string): name of the source or destination.
        selector (string): either 'source' or 'destination'

    Returns:
        object: schema
    """
    newSchema = {}
    schemaObject = {}
    schemaObject["$schema"] = "http://json-schema.org/draft-07/schema#"
    schemaObject["required"] = []
    schemaObject["type"] = "object"
    schemaObject["properties"] = {}
    allOfSchemaObj = {}
    print(f"Generating schema for {name} {selector}")
    if is_old_format(uiConfig):
        allOfSchemaObj = generate_schema_for_allOf(uiConfig, dbConfig, "value")
    if allOfSchemaObj:
        # AnyOf occurring separately, not inside allOf.
        if len(allOfSchemaObj) == 1:
            if isinstance(allOfSchemaObj[0], list):
                schemaObject["anyOf"] = allOfSchemaObj[0]
            else:
                schemaObject["anyOf"] = allOfSchemaObj
        else:
            schemaObject["allOf"] = allOfSchemaObj

    generate_schema_properties(
        uiConfig, dbConfig, schemaObject, schemaObject["properties"], selector
    )
    newSchema["configSchema"] = schemaObject

    return newSchema


def generate_warnings_for_each_type(uiConfig, dbConfig, schema, curUiType):
    """Generates warning for each schema difference created by the current ui-type.

    Args:
        uiConfig (object): file content of ui-config.json.
        dbConfig (object): Configurations of db-config.json.
        schema (object): Existing schema in schema.json
        curUiType (string): Ui-Type for which warnings are generated.
    """
    if is_old_format(uiConfig):
        for uiConfigItem in uiConfig:
            for field in uiConfigItem["fields"]:
                if "preRequisiteField" in field:
                    continue
                if field["type"] == curUiType:
                    key = field.get("configKey", field.get("value"))
                    if key not in schema["properties"]:
                        warnings.warn(
                            f'{key} field is not in schema \n', UserWarning
                        )
                    else:
                        curSchemaField = schema["properties"][key]
                        newSchemaField = uiTypetoSchemaFn.get(curUiType)(
                            field, dbConfig, "value"
                        )
                        schemaDiff = get_json_diff(curSchemaField, newSchemaField)
                        if schemaDiff:
                            warnings.warn(
                                "For type:{} field:{} Difference is : \n\n {} \n".format(
                                    curUiType,
                                    key,
                                    get_formatted_json(schemaDiff),
                                ),
                                UserWarning,
                            )
                    if (
                        curUiType == "textInput"
                        and (
                            schema.get("required", False) == True
                            and key in schema["required"]
                        )
                        and "regex" not in field
                    ):
                        warnings.warn(
                            "For type:{} field:{} regex in ui-config and pattern in schema are mandatory for a required textInput \n".format(
                                curUiType,
                                key,
                            ),
                            UserWarning,
                        )
    else:
        baseTemplate = uiConfig.get("baseTemplate", [])
        sdkTemplate = uiConfig.get("sdkTemplate", {})
        consentSettingsTemplate = uiConfig.get("consentSettingsTemplate", {})
        for template in baseTemplate:
            for section in template.get("sections", []):
                for group in section.get("groups", []):
                    if "preRequisites" in group:
                        continue
                    for field in group.get("fields", []):
                        if "preRequisites" in field:
                            continue
                        generateFunction = uiTypetoSchemaFn.get(field["type"], None)
                        if generateFunction and field["type"] == curUiType:
                            key = field.get("configKey", field.get("value"))
                            if key not in schema["properties"]:
                                warnings.warn(
                                    f'{key} field is not in schema \n',
                                    UserWarning,
                                )
                            else:
                                curSchemaField = schema["properties"][key]
                                newSchemaField = uiTypetoSchemaFn.get(curUiType)(
                                    field, dbConfig, "configKey"
                                )
                                schemaDiff = get_json_diff(
                                    curSchemaField, newSchemaField
                                )
                                if schemaDiff:
                                    warnings.warn(
                                        "For type:{} field:{} Difference is : \n\n {} \n".format(
                                            curUiType,
                                            key,
                                            get_formatted_json(schemaDiff),
                                        ),
                                        UserWarning,
                                    )
                            if (
                                curUiType == "textInput"
                                and (
                                    schema.get("required", False) == True
                                    and key in schema["required"]
                                )
                                and "regex" not in field
                            ):
                                warnings.warn(
                                    "For type:{} field:{} regex in ui-config and pattern in schema are mandatory for a required textInput \n".format(
                                        curUiType,
                                        key,
                                    ),
                                    UserWarning,
                                )

        for field in sdkTemplate.get("fields", []):
            if "preRequisites" in field:
                continue
            generateFunction = uiTypetoSchemaFn.get(field["type"], None)
            if generateFunction:
                if generateFunction and field["type"] == curUiType:
                    key = field.get("configKey", field.get("value"))
                    if key not in schema["properties"]:
                        warnings.warn(
                            f'{key} field is not in schema \n',
                            UserWarning,
                        )
                    else:
                        curSchemaField = schema["properties"][key]
                        newSchemaField = uiTypetoSchemaFn.get(curUiType)(
                            field, dbConfig, "configKey"
                        )
                        schemaDiff = get_json_diff(curSchemaField, newSchemaField)
                        if schemaDiff:
                            warnings.warn(
                                "For type:{} field:{} Difference is : \n\n {} \n".format(
                                    curUiType,
                                    key,
                                    get_formatted_json(schemaDiff),
                                ),
                                UserWarning,
                            )

        for field in sdkTemplate.get("fields", []):
            if "preRequisites" in field:
                continue
            generateFunction = uiTypetoSchemaFn.get(field["type"], None)
            if generateFunction:
                if generateFunction and field["type"] == curUiType:
                    key = field.get("configKey", field.get("value"))
                    if key not in schema["properties"]:
                        warnings.warn(
                            f'{key} field is not in schema \n',
                            UserWarning,
                        )
                    else:
                        curSchemaField = schema["properties"][key]
                        newSchemaField = uiTypetoSchemaFn.get(curUiType)(
                            field, dbConfig, "configKey"
                        )
                        schemaDiff = get_json_diff(newSchemaField, curSchemaField)
                        if schemaDiff:
                            warnings.warn(
                                "For type:{} field:{} Difference is : \n\n {} \n".format(
                                    curUiType, key, schemaDiff
                                ),
                                UserWarning,
                            )

        for field in consentSettingsTemplate.get("fields", []):
            if "preRequisites" in field:
                continue
            generateFunction = uiTypetoSchemaFn.get(field["type"], None)
            if generateFunction:
                if generateFunction and field["type"] == curUiType:
                    key = field.get("configKey", field.get("value"))
                    if key not in schema["properties"]:
                        warnings.warn(
                            f'{key} field is not in schema \n',
                            UserWarning,
                        )
                    else:
                        curSchemaField = schema["properties"][key]
                        newSchemaField = uiTypetoSchemaFn.get(curUiType)(
                            field, dbConfig, "configKey"
                        )
                        schemaDiff = get_json_diff(newSchemaField, curSchemaField)
                        if schemaDiff:
                            warnings.warn(
                                "For type:{} field:{} Difference is : \n\n {} \n".format(
                                    curUiType, key, schemaDiff
                                ),
                                UserWarning,
                            )


uiTypetoSchemaFn = {
    "defaultCheckbox": generate_schema_for_default_checkbox,
    "checkbox": generate_schema_for_checkbox,
    "textInput": generate_schema_for_textinput,
    "textareaInput": generate_schema_for_textarea_input,
    "singleSelect": generate_schema_for_single_select,
    "dynamicCustomForm": generate_schema_for_dynamic_custom_form,
    "dynamicForm": generate_schema_for_dynamic_form,
    "mapping": generate_schema_for_mapping,
    "dynamicSelectForm": generate_schema_for_dynamic_select_form,
    "tagInput": generate_schema_for_tag_input,
    "timeRangePicker": generate_schema_for_time_range_picker,
    "timePicker": generate_schema_for_time_picker,
}


def save_schema_to_file(selector, name, schema):
    # Get the parent directory (one level up)
    script_directory = os.path.dirname(os.path.abspath(__file__))
    directory = os.path.dirname(script_directory)

    # Define the relative path
    relative_path = f"{CONFIG_DIR}/{selector}s/{name}/schema.json"
    file_path = os.path.join(directory, relative_path)

    # Write the new content
    with open(file_path, "w") as file:
        file.write(get_formatted_json(schema))


def validate_config_consistency(
    name, selector, uiConfig, dbConfig, schema, shouldUpdateSchema
):
    """Generates a schema and compares it with an existing one.
    If schemaDiff is present, it calls for individual warnings by iterating over each ui-type.

    Args:
        name (string): name of the source or destination.
        selector (string): either 'source' or 'destination'
        uiConfig (object): file content of ui-config.json.
        dbConfig (object): Configurations of db-config.json.
        schema (object): Existing schema in schema.json.
        shouldUpdateSchema (boolean): if it should update the existing schema with generated one
    """
    if schema == None and uiConfig == None:
        return
    if uiConfig == None:
        print("-" * 50)
        warnings.warn(f"Ui-Config is null for {name} in {selector} \n", UserWarning)
        print("-" * 50)
        return
    generatedSchema = generate_schema(uiConfig, dbConfig, name, selector)

    if schema:
        print("-" * 50)
        print(f"Analyzing schema for {name} in {selector}s")
        schemaDiff = get_json_diff(schema, generatedSchema["configSchema"])
        if shouldUpdateSchema:
            finalSchema = {}
            finalSchema["configSchema"] = apply_json_diff(schema, schemaDiff)
            save_schema_to_file(selector, name, finalSchema)

        if schemaDiff:
            print("-" * 50)
            print(f"Schema diff for {name} in {selector}s")
            # call for individual warnings
            for uiType in uiTypetoSchemaFn.keys():
                generate_warnings_for_each_type(uiConfig, dbConfig, schema, uiType)
            # schema diff for "additionalProperties"
            if "additionalProperties" not in schema:
                print(
                    "\n Recommendation: Please set additionalProperties to False in schema.json. \n"
                )
            # schema diff for "required"
            if "required" not in schema:
                warnings.warn("required field is not in schema \n", UserWarning)
            else:
                curRequiredField = schema["required"]
                newRequiredField = generatedSchema["configSchema"]["required"]
                requiredFieldDiff = get_json_diff(curRequiredField, newRequiredField)
                if requiredFieldDiff:
                    warnings.warn(
                        "For required field Difference is :  \n\n {} \n".format(
                            get_formatted_json(requiredFieldDiff)
                        ),
                        UserWarning,
                    )
            if "allOf" in generatedSchema["configSchema"]:
                curAllOfSchema = {}
                if "allOf" in schema:
                    curAllOfSchema = schema["allOf"]
                newAllOfSchema = generatedSchema["configSchema"]["allOf"]
                allOfSchemaDiff = get_json_diff(curAllOfSchema, newAllOfSchema)
                if allOfSchemaDiff:
                    warnings.warn(
                        "For allOf field Difference is :  \n\n {} \n".format(
                            get_formatted_json(allOfSchemaDiff)
                        ),
                        UserWarning,
                    )
            if "anyOf" in generatedSchema["configSchema"]:
                curAnyOfSchema = {}
                if "anyOf" in schema:
                    curAnyOfSchema = schema["anyOf"]
                newAnyOfSchema = generatedSchema["configSchema"]["anyOf"]
                anyOfSchemaDiff = get_json_diff(curAnyOfSchema, newAnyOfSchema)
                if anyOfSchemaDiff:
                    warnings.warn(
                        "For anyOf field Difference is :  \n\n {} \n".format(
                            get_formatted_json(anyOfSchemaDiff)
                        ),
                        UserWarning,
                    )
            print("-" * 50)
    else:
        if shouldUpdateSchema:
            save_schema_to_file(selector, name, generatedSchema)

        print("-" * 50)
        print(f"Generated schema for {name} in {selector}s")
        print(get_formatted_json(generatedSchema))
        print("-" * 50)


def get_schema_diff(name, selector, shouldUpdateSchema=False):
    """Validates the schema for the given name and selector.

    Args:
        name (string): name of the source or destination.
        selector (string): either 'source' or 'destination'.
        shouldUpdateSchema (boolean): if it should update the existing schema with generated one
    """
    file_selectors = ["db-config.json", "ui-config.json", "schema.json"]
    directory = f"./{CONFIG_DIR}/{selector}s/{name}"
    if not os.path.isdir(directory):
        return

    if name not in EXCLUDED_DEST:
        available_files = os.listdir(directory)
        file_content = {}
        for file_selector in file_selectors:
            if file_selector in available_files:
                file_content.update(get_json_from_file(f"{directory}/{file_selector}"))
        uiConfig = file_content.get("uiConfig")
        schema = file_content.get("configSchema")
        dbConfig = file_content.get("config")

        validate_config_consistency(
            name, selector, uiConfig, dbConfig, schema, shouldUpdateSchema
        )


def fix_regexes_for_config(name, typ='destination'):
    """
    Fix regexes in schema.json and ui-config.json for the given destination/source using generalize_regex_pattern.
    """
    DEST_PATH = Path('src/configurations/destinations')
    SRC_PATH = Path('src/configurations/sources')
    base_dir = DEST_PATH / name if typ == 'destination' else SRC_PATH / name
    schema_path = base_dir / 'schema.json'
    ui_config_path = base_dir / 'ui-config.json'

    def fix_schema_patterns(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == 'pattern' and isinstance(v, str):
                    # Synthesize a fake field dict for generalize_regex_pattern
                    field = {'regex': v, 'type': 'textInput'}
                    new_pattern = generalize_regex_pattern(field)
                    if new_pattern != v:
                        obj[k] = new_pattern
                else:
                    fix_schema_patterns(v)
        elif isinstance(obj, list):
            for item in obj:
                fix_schema_patterns(item)

    def fix_ui_config_regexes(ui_config):
        """
        Recursively clean regex patterns in all textInput fields in ui-config.json, including nested customFields.
        """
        def process_fields(fields):
            if not isinstance(fields, list):
                return
            for field in fields:
                if not isinstance(field, dict):
                    continue
                if field.get("type") == "textInput":
                    regex = field.get("regex")
                    if regex:
                        new_regex = generalize_regex_pattern(field)
                        if new_regex != regex:
                            field["regex"] = new_regex
                # Recursively process nested fields
                if "fields" in field:
                    process_fields(field["fields"])
                if "customFields" in field:
                    process_fields(field["customFields"])
                if "groups" in field:
                    process_fields(field["groups"])

        # Handle both old and new uiConfig structures
        if isinstance(ui_config, list):
            for section in ui_config:
                if "fields" in section:
                    process_fields(section["fields"])
        elif isinstance(ui_config, dict):
            base_template = ui_config.get("baseTemplate", [])
            if base_template and isinstance(base_template, list):
                for section in base_template[0].get("sections", []):
                    for group in section.get("groups", []):
                        process_fields(group.get("fields", []))

    # Fix schema.json
    if schema_path.exists():
        with open(schema_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        before = json.dumps(data, indent=2)
        if 'configSchema' in data:
            fix_schema_patterns(data['configSchema'])
        after = json.dumps(data, indent=2)
        if before != after:
            with open(schema_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f'Updated regex patterns in {schema_path}')
        else:
            print(f'No regex changes needed in {schema_path}')
    else:
        print(f'File not found: {schema_path}')

    # Fix ui-config.json
    if ui_config_path.exists():
        with open(ui_config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        before = json.dumps(data, indent=2)
        if 'uiConfig' in data:
            fix_ui_config_regexes(data['uiConfig'])
        after = json.dumps(data, indent=2)
        if before != after:
            with open(ui_config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f'Updated regex patterns in {ui_config_path}')
        else:
            print(f'No regex changes needed in {ui_config_path}')
    else:
        print(f'File not found: {ui_config_path}')


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--fix-regex":
        if len(sys.argv) < 3:
            print("Usage: python3 scripts/schemaGenerator.py --fix-regex <destination_or_source_name> [--type destination|source]")
            sys.exit(1)
        name = sys.argv[2]
        typ = 'destination'
        if len(sys.argv) > 4 and sys.argv[3] == '--type':
            typ = sys.argv[4]
        fix_regexes_for_config(name, typ)
        sys.exit(0)
    parser = argparse.ArgumentParser(
        description="Generates schema.json from ui-config.json and db-config.json and validates against actual scheme.json"
    )
    group = parser.add_mutually_exclusive_group()
    parser.add_argument(
        "selector",
        metavar="selector",
        type=str,
        help="Enter whether -name is a source or destination",
    )
    parser.add_argument(
        "-update",
        action="store_true",
        help="Will update existing schema with any changes",
    )
    group.add_argument(
        "-name", metavar="name", type=str, help="Enter the folder name under selector"
    )
    group.add_argument(
        "-all",
        action="store_true",
        help="Will run validation for all entities under selector",
    )

    args = parser.parse_args()
    selector = args.selector
    shouldUpdateSchema = args.update

    dir_path = f"./{CONFIG_DIR}/{selector}s"
    if args.all:
        if not os.path.isdir(dir_path):
            print(f"No {selector}s folder found")
            exit(1)

        current_items = os.listdir(dir_path)
        for name in current_items:
            get_schema_diff(name, selector, shouldUpdateSchema)
    else:
        name = args.name
        get_schema_diff(name, selector, shouldUpdateSchema)
