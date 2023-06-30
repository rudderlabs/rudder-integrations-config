'''
    Usage: schemaGenerator.py [-h] [-name name | -all] selector
        1. selector - “source” or “destination”
        2. all - runs the validator for all the selector.
        3. name - any particular source or destination name such as `google_analytics`
    Example:
        1. python3 scripts/schemaGenerator.py -name="adobe_analytics" destination
        2. python3 scripts/schemaGenerator.py -all source
'''
import os
import sys
import warnings
import json
from jsondiff import diff
from enum import Enum
import argparse

CONFIG_DIR = 'src/configurations'

class FieldTypeEnum(Enum):
    STRING = "string"
    OBJECT = "object"
    BOOLEAN = "boolean"
    ARRAY = "array"


def is_old_format(uiConfig):
    if isinstance(uiConfig, dict):
        return False
    return True

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
    if "defaultOption" not in field and field.get("required", False) == False:
            options_list.append("")
    return options_list

def generalize_regex_pattern(field):
    """Generates the pattern for schema based on the type of field.
        - If the field contains regex, then regex is the pattern; it gets prefixed with a default prefix if regex does not have it.
        - Else, the default prefix is appended with ^(.{0,100}).

    Args:
        field (object): Individual field in ui-config, includes properties such as label, type, name, regex etc.

    Returns:
        string: generated pattern for the field.
    """        
    defaultSubPattern = "(^\\{\\{.*\\|\\|(.*)\\}\\}$)"
    defaultEnvPattern = "(^env[.].+)"
    pattern = ""
    if "regex" in field:
        pattern = field["regex"]
        if defaultSubPattern not in pattern:
            pattern = "|".join([defaultSubPattern, pattern])
        if defaultEnvPattern not in pattern:
            indexToPlace = pattern.find(defaultSubPattern) + len(defaultSubPattern)
            pattern = pattern[:indexToPlace] + '|' + defaultEnvPattern + pattern[indexToPlace:]
    else:
        pattern = "|".join([defaultSubPattern, defaultEnvPattern, '^(.{0,100})$']) 
    return pattern


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
    for sourceType in dbConfig["supportedSourceTypes"]:
        if sourceType in dbConfig["destConfig"] and field[schema_field_name] in dbConfig["destConfig"][sourceType]:
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
    if "destConfig" in dbConfig and "defaultConfig" in dbConfig["destConfig"] and field[schema_field_name] in dbConfig["destConfig"]["defaultConfig"]:
        return True
    return False

def get_list_of_text_input_meta_fields(field):
    """Returns the meta fields for text input.

    Args:
        field (object): Individual field in ui-config.

    Returns:
        list: meta fields
    """    
    if "inputFieldType" in field and field['inputFieldType'] == "password":
        secret_value = field.get('secret',None)
        if secret_value == False:
            warnings.warn(f'secret and inputFieldType does not match')
    
    prop_list_for_text_input = ["default", "footerNote", "footerURL", "infoTooltip", "label", "labelNote", 
                                "options", "placeholder", "regexErrorMessage","secret"]
    return prop_list_for_text_input

def get_list_of_text_area_input_meta_fields(field):
    """Returns the meta fields for textarea input.

    Args:
        field (object): Individual field in ui-config.

    Returns:
        list: meta fields
    """
    prop_list_for_text_area_input = ["footerNote", "label", "labelNote", "placeholder", "regexErrorMessage", "secret"]
    return prop_list_for_text_area_input    

def get_list_of_default_checkbox_meta_fields(field):
    """Returns the meta fields for default checkbox.

    Args:
        field (object): Individual field in ui-config.

    Returns:
        list: meta fields
    """    
    prop_list_for_default_checkbox = ["default", "label"]
    return prop_list_for_default_checkbox

def get_list_of_checkbox_meta_fields(field):
    """Returns the meta fields for checkbox.

    Args:
        field (object): Individual field in ui-config.

    Returns:
        list: meta fields
    """
    prop_list_for_checkbox = ["footerNote", "label"]
    return prop_list_for_checkbox

def get_list_of_single_select_meta_fields(field):
    """Returns the meta fields for single select.

    Args:
        field (object): Individual field in ui-config.

    Returns:
        list: meta fields
    """
    prop_list_for_single_select = ["footerNote", "label", "mode", "options", 
                                   "placeholder", "regexErrorMessage"]
    return prop_list_for_single_select

def get_list_of_dynamic_custom_form_meta_fields(field):
    """Returns the meta fields for dynamic custom form.

    Args:
        field (object): Individual field in ui-config.

    Returns:
        list: meta fields
    """
    prop_list_for_dynamic_custom_form = ["footerNote", "label", "labelNote"]
    return prop_list_for_dynamic_custom_form

def get_list_of_dynamic_form_meta_fields(field):
    """Returns the meta fields for dynamic form.

    Args:
        field (object): Individual field in ui-config.

    Returns:
        list: meta fields
    """
    prop_list_for_dynamic_form = ["footerNote", "label", "labelLeft", "labelRight", "placeholderLeft", "placeholderRight"]
    return prop_list_for_dynamic_form

def get_list_of_dynamic_select_form_meta_fields(field):
    """Returns the meta fields for dynamic select form.

    Args:
        field (object): Individual field in ui-config.

    Returns:
        list: meta fields
    """
    prop_list_for_dynamic_select_form = ["footerNote", "label", "labelLeft", "labelRight", "options", "placeholderLeft", 
                                         "placeholderRight"]
    return prop_list_for_dynamic_select_form

def get_list_of_tag_input_meta_fields(field):
    """Returns the meta fields for tagInput.

    Args:
        field (object): Individual field in ui-config.

    Returns:
        list: meta fields
    """
    prop_list_for_tag_input = ["default", "label", "placeholder"]
    return prop_list_for_tag_input

def get_list_of_time_range_picker_meta_fields(field):
    """Returns the meta fields for time range picker.

    Args:
        field (object): Individual field in ui-config.

    Returns:
        list: meta fields
    """
    prop_list_for_time_range_picker = ["endTime", "footerNote", "label", "options", "startTime"]
    return prop_list_for_time_range_picker

def get_list_of_time_picker_meta_fields(field):
    """Returns the meta fields for time picker.

    Args:
        field (object): Individual field in ui-config.

    Returns:
        list: meta fields
    """
    prop_list_for_time_picker = ["footerNote", "label", "options"]
    return prop_list_for_time_picker

uiTypetoMetaFn = {
    "defaultCheckbox": get_list_of_default_checkbox_meta_fields,
    "checkbox": get_list_of_checkbox_meta_fields,
    "textInput": get_list_of_text_input_meta_fields,
    "textareaInput": get_list_of_text_area_input_meta_fields,
    "singleSelect": get_list_of_single_select_meta_fields,
    "dynamicCustomForm": get_list_of_dynamic_custom_form_meta_fields,
    'dynamicForm': get_list_of_dynamic_form_meta_fields,
    'dynamicSelectForm': get_list_of_dynamic_select_form_meta_fields,
    'tagInput': get_list_of_tag_input_meta_fields,
    'timeRangePicker': get_list_of_time_range_picker_meta_fields,
    'timePicker': get_list_of_time_picker_meta_fields
}

def generate_meta(schemaObj, field):
    """Takes in the schemaObj of the field and adds the meta field into schemaObj.

    Args:
        schemaObj (object): schema object for the field
        field (object): Individual field in ui-config.

    Returns:
        object: schema object with meta fields
    """    
    meta_prop = {}
    # For dynamicForm and dynamicSelectForm, keyLeft and keyRight meta properties
    meta_prop_right = {}
    meta_prop_left = {}
    # For timeRangePicker, startTime and endTime meta properties
    meta_prop_start = {}
    meta_prop_end = {}

    meta_fn = uiTypetoMetaFn.get(field['type'],None)

    if meta_fn:
        prop_list_for_field = meta_fn(field)
        for prop in prop_list_for_field:
            if prop in field:
                if prop == 'startTime' or prop == 'endTime':
                    if prop == 'startTime':
                        meta_prop_start = field[prop].copy()
                        del meta_prop_start["value"]
                    else:
                        meta_prop_end = field[prop].copy()
                        del meta_prop_end["value"]
                elif prop == "options" and (field["type"]=='singleSelect' or field["type"]=='dynamicSelectForm'):
                    meta_prop["helperStrings"]={}
                    for option in field["options"]:
                        if isinstance(option, int) or isinstance(option, str):
                            continue
                        if "name" in option and "value" in option:
                            meta_prop["helperStrings"][option["value"]] = option["name"]
                        elif "label" in option and "value" in option:
                            meta_prop["helperStrings"][option["value"]] = option["label"]
                elif prop.endswith("Left") and "keyLeft" in field:
                    meta_prop_left[prop[:-4]] = field[prop]
                elif prop.endswith("Right") and "keyRight" in field:
                    meta_prop_right[prop[:-5]] = field[prop]
                else:
                    meta_prop[prop] = field[prop]
        if meta_prop_left:
            schemaObj["items"]["properties"][field["keyLeft"]]["meta"]=meta_prop_left
        if meta_prop_right:
            schemaObj["items"]["properties"][field["keyRight"]]["meta"]=meta_prop_right
        if meta_prop_start:
            schemaObj["properties"][field["startTime"]["value"]]["meta"]=meta_prop_start
        if meta_prop_end:
            schemaObj["properties"][field["endTime"]["value"]]["meta"]=meta_prop_end
        if meta_prop:
            schemaObj['meta'] = meta_prop
    return schemaObj


def generate_schema_for_default_checkbox(field, dbConfig, schema_field_name):
    """Creates an schema object of defaultCheckbox.

    Args:
        field (object): Individual field in ui-config.
        dbConfig (object): Configurations of db-config.json.
        schema_field_name (string): Specifies which key has the field's name in schema. 
            For old schema types, it is 'value' else 'configKey'.

    Returns:
        object
    """
    defaultCheckboxObj = {
        "type": FieldTypeEnum.OBJECT.value,
        "properties": {
            "web": {
                "type": FieldTypeEnum.BOOLEAN.value
            }
        }
    }
    defaultCheckboxObj = generate_meta(defaultCheckboxObj, field)
    return defaultCheckboxObj

def generate_schema_for_checkbox(field, dbConfig, schema_field_name):
    """Creates an schema object of checkbox.

    Args:
        field (object): Individual field in ui-config.
        dbConfig (object): Configurations of db-config.json.
        schema_field_name (string): Specifies which key has the field's name in schema. 
            For old schema types, it is 'value' else 'configKey'.

    Returns:
        object
    """
    isSourceDependent = is_dest_field_dependent_on_source(field, dbConfig, schema_field_name)
    checkboxSchemaObj = {}
    if isSourceDependent:
        checkboxSchemaObj["type"] = FieldTypeEnum.OBJECT.value
        checkboxSchemaObj["properties"] = {}
        # iterates over supported sources and sets the field for that source if field is present inside that source
        for sourceType in dbConfig["supportedSourceTypes"]:
            if sourceType in dbConfig["destConfig"] and field[schema_field_name] in dbConfig["destConfig"][sourceType]:
                checkboxSchemaObj["properties"][sourceType] = {
                    "type": FieldTypeEnum.BOOLEAN.value}
    else:
        checkboxSchemaObj["type"] = FieldTypeEnum.BOOLEAN.value
        if "default" in field:
            checkboxSchemaObj["default"] = field["default"]
    checkboxSchemaObj = generate_meta(checkboxSchemaObj, field)
    return checkboxSchemaObj

def generate_schema_for_textinput(field, dbConfig, schema_field_name):
    """Creates an schema object of textinput.

    Args:
        field (object): Individual field in ui-config.
        dbConfig (object): Configurations of db-config.json.
        schema_field_name (string): Specifies which key has the field's name in schema. 
            For old schema types, it is 'value' else 'configKey'.

    Returns:
        object
    """
    textInputSchemaObj = {}
    isSourceDependent = is_dest_field_dependent_on_source(field, dbConfig, schema_field_name)
    if isSourceDependent:
        textInputSchemaObj["type"] = FieldTypeEnum.OBJECT.value
        textInputSchemaObj["properties"] = {}
        # iterates over supported sources and sets the field for that source if field is present inside that source
        for sourceType in dbConfig["supportedSourceTypes"]:
            if sourceType in dbConfig["destConfig"] and field[schema_field_name] in dbConfig["destConfig"][sourceType]:
                textInputSchemaObj["properties"][sourceType] = {
                    "type": FieldTypeEnum.STRING.value}
                if 'regex' in field:
                    textInputSchemaObj["properties"][sourceType]["pattern"] = field["regex"]
    else:
        textInputSchemaObj = {"type": FieldTypeEnum.STRING.value}
        if 'regex' in field:
            textInputSchemaObj["pattern"] = generalize_regex_pattern(field)
    textInputSchemaObj = generate_meta(textInputSchemaObj, field)
    return textInputSchemaObj

def generate_schema_for_textarea_input(field, dbConfig, schema_field_name):
    """Creates an schema object of textareaInput.

    Args:
        field (object): Individual field in ui-config.
        dbConfig (object): Configurations of db-config.json.
        schema_field_name (string): Specifies which key has the field's name in schema. 
            For old schema types, it is 'value' else 'configKey'.

    Returns:
        object
    """
    textareaInputObj = {"type": FieldTypeEnum.STRING.value}
    if 'regex' in field:
        textareaInputObj["pattern"] = generalize_regex_pattern(field)
    textareaInputObj = generate_meta(textareaInputObj, field)
    return textareaInputObj

def generate_schema_for_single_select(field, dbConfig, schema_field_name):
    """Creates an schema object of singleSelect.

    Args:
        field (object): Individual field in ui-config.
        dbConfig (object): Configurations of db-config.json.
        schema_field_name (string): Specifies which key has the field's name in schema. 
            For old schema types, it is 'value' else 'configKey'.

    Returns:
        object
    """
    singleSelectObj = {}
    if "mode" in field and field["mode"] == 'multiple':
        singleSelectObj = {"type": FieldTypeEnum.ARRAY.value} 
        singleSelectObj["items"] = {
            "type": FieldTypeEnum.STRING.value,
            "enum": get_options_list_for_enum(field)
        }
        if "defaultOption" in field:
            if isinstance(field["defaultOption"]["value"], list):
                singleSelectObj["default"] = field["defaultOption"]["value"]
            else:
                singleSelectObj["default"] = [field["defaultOption"]["value"]]
    else:
        singleSelectObj = {"type": FieldTypeEnum.STRING.value}
        singleSelectObj["enum"] = get_options_list_for_enum(field)
        if "defaultOption" in field:
            singleSelectObj["default"] = field["defaultOption"]["value"]

    isSourceDependent = is_dest_field_dependent_on_source(field, dbConfig, schema_field_name)
    if isSourceDependent:
        newSingleSelectObj = {"type": FieldTypeEnum.OBJECT.value}
        newSingleSelectObj["properties"] = {}
        # iterates over supported sources and sets the field for that source if field is present inside that source
        for sourceType in dbConfig["supportedSourceTypes"]:
            if sourceType in dbConfig["destConfig"] and field[schema_field_name] in dbConfig["destConfig"][sourceType]:
                newSingleSelectObj["properties"][sourceType] = singleSelectObj
        singleSelectObj = newSingleSelectObj
    singleSelectObj = generate_meta(singleSelectObj, field)
    return singleSelectObj

def generate_schema_for_dynamic_custom_form(field, dbConfig, schema_field_name):
    """Creates an schema object of dynamicCustomForm.

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
    for customField in field["customFields"]:
        customeFieldSchemaObj = uiTypetoSchemaFn.get(customField["type"])(customField, dbConfig, schema_field_name)
        isCustomFieldDependentOnSource = is_dest_field_dependent_on_source(customField, dbConfig, schema_field_name)
        if 'pattern' not in customeFieldSchemaObj and not isCustomFieldDependentOnSource and customeFieldSchemaObj["type"]==FieldTypeEnum.STRING.value:
            customeFieldSchemaObj["pattern"] = generalize_regex_pattern(customField)
        # If the custom field is source dependent, we remove the source keys as it's not required inside custom fields, rather they need to be moved to top.
        if isCustomFieldDependentOnSource:
            for sourceType in dbConfig["supportedSourceTypes"]:
                if sourceType in dbConfig["destConfig"] and field[schema_field_name] in dbConfig["destConfig"][sourceType]:
                    customeFieldSchemaObj = customeFieldSchemaObj["properties"][sourceType]
                    break
        dynamicCustomFormItemObj["properties"][customField[schema_field_name]] =  customeFieldSchemaObj

    dynamicCustomFormObj["items"] = dynamicCustomFormItemObj
    isSourceDependent = is_dest_field_dependent_on_source(field, dbConfig, schema_field_name)
    # If the field is source dependent, new schema object is created by setting the fields inside the source.
    if isSourceDependent:
        newDynamicCustomFormObj = {"type": FieldTypeEnum.OBJECT.value}
        newDynamicCustomFormObj["properties"] = {}
        for sourceType in dbConfig["supportedSourceTypes"]:
            if sourceType in dbConfig["destConfig"] and field[schema_field_name] in dbConfig["destConfig"][sourceType]:
                newDynamicCustomFormObj["properties"][sourceType] = dynamicCustomFormObj
        dynamicCustomFormObj = newDynamicCustomFormObj
    dynamicCustomFormObj = generate_meta(dynamicCustomFormObj, field)
    return dynamicCustomFormObj

def generate_schema_for_dynamic_form(field, dbConfig, schema_field_name):
    """Creates an schema object of dynamicForm.

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
        if(field["type"] == 'dynamicSelectForm'):
            if (forFieldWithTo != (field.get("reverse", False)==False)):
                obj["pattern"] = generalize_regex_pattern(field)
            else:
                if "defaultOption" in field:
                    obj["default"] = field["defaultOption"]["value"]
                obj["enum"] = get_options_list_for_enum(field)
        else:
            obj["pattern"] = generalize_regex_pattern(field)
        return obj

    dynamicFormSchemaObject = {}
    dynamicFormSchemaObject['type'] = FieldTypeEnum.ARRAY.value
    dynamicFormItemObject = {}
    dynamicFormItemObject["type"] = FieldTypeEnum.OBJECT.value
    dynamicFormItemObject['properties'] = {}
    dynamicFormItemObjectProps = [
        (field['keyLeft'], generate_key), (field['keyRight'], generate_key)]
    for dynamicFromItemObjectProp in dynamicFormItemObjectProps:
        dynamicFormItemObject['properties'][dynamicFromItemObjectProp[0]
                                            ] = dynamicFromItemObjectProp[1](dynamicFromItemObjectProp[0] == "to")
    dynamicFormSchemaObject['items'] = dynamicFormItemObject
    dynamicFormSchemaObject = generate_meta(dynamicFormSchemaObject, field)
    return dynamicFormSchemaObject

def generate_schema_for_dynamic_select_form(field, dbConfig, schema_field_name):
    """Creates an schema object of dynamicSelectForm.

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
    """Creates an schema object of tagInput.

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
    tagItem['type'] = FieldTypeEnum.OBJECT.value
    tagItemProps = {
        str(field['tagKey']): {
            "type": FieldTypeEnum.STRING.value,
            "pattern": generalize_regex_pattern(field)
        }
    }
    tagItem['properties'] = tagItemProps
    tagObject["items"] = tagItem
    tagObject = generate_meta(tagObject, field)
    return tagObject

def generate_schema_for_time_range_picker(field, dbConfig, schema_field_name):
    """Creates an schema object of timeRangePicker.

    Args:
        field (object): Individual field in ui-config.
        dbConfig (object): Configurations of db-config.json.
        schema_field_name (string): Specifies which key has the field's name in schema. 
            For old schema types, it is 'value' else 'configKey'.

    Returns:
        object
    """
    timeRangeObj = {}
    timeRangeObj['type'] = FieldTypeEnum.OBJECT.value
    timeRangeProps = {
        field['startTime']['value']: {'type': FieldTypeEnum.STRING.value},
        field['endTime']['value']: {'type': FieldTypeEnum.STRING.value}
    }
    timeRangeObj['properties'] = timeRangeProps
    timeRangeObj['required'] = list(timeRangeProps.keys())
    timeRangeObj = generate_meta(timeRangeObj, field)
    return timeRangeObj

def generate_schema_for_time_picker(field, dbConfig, schema_field_name):
    """Creates an schema object of timePicker.

    Args:
        field (object): Individual field in ui-config.
        dbConfig (object): Configurations of db-config.json.
        schema_field_name (string): Specifies which key has the field's name in schema. 
            For old schema types, it is 'value' else 'configKey'.

    Returns:
        object
    """
    timePickerObj = {
        "type": FieldTypeEnum.STRING.value
    }
    timePickerObj = generate_meta(timePickerObj, field)
    return timePickerObj

def compare_pre_requisite_fields(fieldA, fieldB):
    """Compares two preRequisiteFields fieldA and fieldB for each property and checks if there "selectedValue" match. 

    Args:
        fieldA (list or object): contains two properties, 'name' and 'selectedValue'.
        fieldB (list or object):

    Returns:
        boolean: If all the properties have the same 'name' and 'selectedValue', then it returns True else False.
    """    
    if type(fieldA) != type(fieldB):
        return False
    elif type(fieldA) == list:
        if len(fieldA) != len(fieldB):
            return False
        for i in range(0, len(fieldA)):
            if fieldA[i]['name'] != fieldB[i]['name'] or fieldA[i]['selectedValue'] != fieldB[i]['selectedValue']:
                return False
    else:
        if fieldA['name'] != fieldB['name'] or fieldA['selectedValue'] != fieldB['selectedValue']:
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
        fields = group.get('fields', [])
        for field in fields:
            if "preRequisiteField" not in field:
                continue
            isPresent = False
            for preRequisiteField in preRequisiteFieldsList:
                if compare_pre_requisite_fields(preRequisiteField, field["preRequisiteField"]):
                    isPresent = True
                    break
            if not isPresent:
                preRequisiteFieldsList.append(field["preRequisiteField"])
    return preRequisiteFieldsList


def generate_if_object(preRequisiteField):
    """Creates an if object for the given preRequisiteField. The preRequisiteField becomes an if condition in the schema.

    Args:
        preRequisiteField (list or object): contains two properties, 'name' and 'selectedValue'.

    Returns:
        object: if block for given preRequisiteField.
    """    
    ifObj = {"properties": {}, "required": []}
    if type(preRequisiteField) == list:
        for field in preRequisiteField:
            ifObj["properties"][field["name"]] = {
                "const": field["selectedValue"]
            }
            ifObj["required"].append(field["name"])
    else:
        ifObj["properties"][preRequisiteField["name"]] = {
            "const": preRequisiteField["selectedValue"]
        }
        ifObj["required"].append(preRequisiteField["name"])
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
            fields = group.get('fields', [])
            for field in fields:
                if "preRequisiteField" not in field:
                    continue
                if compare_pre_requisite_fields(field["preRequisiteField"], preRequisiteField):
                    thenObj["properties"][field[schema_field_name]] = uiTypetoSchemaFn.get(field["type"])(field, dbConfig, schema_field_name)
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
            commonProperties.append({"key": key, schema_field_name: propertiesA[key]["const"]})
        elif type(propertiesA[key]["const"]) == bool and propertiesA[key]["const"] != propertiesB[key]["const"]:
            oppositeProperties.append({"key": key, schema_field_name: propertiesA[key]["const"]})
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
        if "if" in allOfItemList[index] and check_if_conditions_match(ifProp, allOfItemList[index]["if"]["properties"], schema_field_name):
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
        for j in range(i+1, length):
            ifPropertiesA = allOfItemList[i]["if"]["properties"]
            thenPropertiesA = allOfItemList[i]["then"]
            ifPropertiesB = allOfItemList[j]["if"]["properties"]
            thenPropertiesB = allOfItemList[j]["then"]
            commonIfProp, oppositeIfProp = get_common_and_opposite_fields(ifPropertiesA, ifPropertiesB, schema_field_name)
            if oppositeIfProp:
                anyOfObj = [{}, {}]
                for k in range(0, len(oppositeIfProp)):
                    if ifPropertiesA[oppositeIfProp[k]["key"]]["const"] == True:
                        anyOfObj[1] = thenPropertiesA
                        anyOfObj[1]["properties"][oppositeIfProp[k]["key"]] = {"const": True}
                        anyOfObj[1]["required"].append(oppositeIfProp[k]["key"])
                        anyOfObj[0] = thenPropertiesB
                    else:
                        anyOfObj[1] = thenPropertiesB
                        anyOfObj[1]["properties"][oppositeIfProp[k]["key"]] = {"const": True}
                        anyOfObj[1]["required"].append(oppositeIfProp[k]["key"])
                        anyOfObj[0] = thenPropertiesA
                # AnyOf object is placed at index of "if-then" block having same if properties as of common properties else at end. 
                indexToPlace = find_index_to_place_anyOf(commonIfProp, allOfItemList, schema_field_name)
                if indexToPlace == -1:
                    allOfItemList.append(anyOfObj)
                else:
                    allOfItemList[indexToPlace]["then"]["anyOf"] = anyOfObj
                delIndices.append(i)
                delIndices.append(j)
    allOfItemList = [allOfItemList[index] for index in range(len(allOfItemList)) if index not in delIndices]
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
                pattern = "^("
                length = len(dbConfig["supportedConnectionModes"][sourceType])
                for i in range(0, length):
                    pattern += dbConfig["supportedConnectionModes"][sourceType][i]
                    if i != length - 1:
                        pattern += '|'
                pattern += ")$"
                connectionItemObj["pattern"] = pattern
                connectionObj["properties"][sourceType] = connectionItemObj
    return connectionObj


def generate_schema_properties(uiConfig, dbConfig, schemaObject, properties, name, selector):    
    """Generates corresponding schema properties by iterating over each of the ui-config fields.

    Args:
        uiConfig (object): file content of ui-config.json.
        dbConfig (object): Configurations of db-config.json.
        schemaObject (object): schema being generated
        properties (object): properties of schema
        name (string): name of the source or destination.
        selector (string): either 'source' or 'destination'
    """    
    if is_old_format(uiConfig):
        for group in uiConfig:
            fields = group.get('fields', [])
            for field in fields:
                if "preRequisiteField" in field:
                    continue
                generateFunction = uiTypetoSchemaFn.get(field['type'], None)
                if generateFunction:
                    properties[field['value']] = generateFunction(
                        field, dbConfig, 'value')
                if field.get('required', False) == True and is_field_present_in_default_config(field, dbConfig, "value"):
                    schemaObject['required'].append(field['value'])
    else:
        if selector == 'destination':
            baseTemplate = uiConfig.get('baseTemplate', [])
            sdkTemplate = uiConfig.get('sdkTemplate', {})
            for template in baseTemplate:
                for section in template.get('sections', []):
                    for group in section.get('groups', []):
                        for field in group.get('fields', []):
                            generateFunction = uiTypetoSchemaFn.get(
                                field['type'], None)
                            if generateFunction:
                                properties[field['configKey']] = generateFunction(
                                    field, dbConfig, 'configKey')
                            if template.get('title', "") == "Initial setup" and is_field_present_in_default_config(field, dbConfig, "configKey"):
                                schemaObject['required'].append(
                                    field['configKey'])

            for field in sdkTemplate.get('fields', []):
                generateFunction = uiTypetoSchemaFn.get(field['type'], None)
                if generateFunction:
                    properties[field['configKey']] = generateFunction(
                        field, dbConfig, 'configKey')
                if field.get('required', False) == True and is_field_present_in_default_config(field, dbConfig, "configKey"):
                    schemaObject['required'].append(field['configKey'])

            # default properties in new ui-config based schemas.
            schemaObject['properties']['useNativeSDK'] = generate_schema_for_checkbox({"type":"checkbox", 
                                                                           "value":"useNativeSDK"}, dbConfig, "value")
            schemaObject['properties']['connectionMode'] = generate_connection_mode(dbConfig)
        else:
            # for sources
            def generate_config_props(config):
                for group in config:
                    fields = group.get('fields', [])
                    for field in fields:
                        generateFunction = uiTypetoSchemaFn.get(
                            field["type"], None)
                        if generateFunction:
                            properties[field['value']] = generateFunction(
                                field, dbConfig, 'value')

            auth = uiConfig.get('auth', None)
            config = uiConfig.get('config', [])
            if auth:
                type = auth.get('type')
                if type == "form":
                    auth_config = auth.get('config', [])
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
    schemaObject['$schema'] = 'http://json-schema.org/draft-07/schema#'
    schemaObject['required'] = []
    schemaObject['type'] = "object"
    schemaObject['properties'] = {}
    allOfSchemaObj = {}
    if is_old_format(uiConfig):
        allOfSchemaObj = generate_schema_for_allOf(uiConfig, dbConfig, "value")
    if allOfSchemaObj:
        # AnyOf occuring separately, not inside of allOf.
        if len(allOfSchemaObj) == 1:
           if isinstance(allOfSchemaObj[0], list):
               schemaObject['anyOf'] = allOfSchemaObj[0]
           else:
               schemaObject['anyOf'] = allOfSchemaObj
        else:
            schemaObject['allOf'] = allOfSchemaObj
    generate_schema_properties(uiConfig, dbConfig, schemaObject,
                       schemaObject['properties'], name, selector)
    newSchema['configSchema'] = schemaObject
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
                    if field["value"] not in schema["properties"]:
                        warnings.warn(
                            f'{field["value"]} field is not in schema \n',  UserWarning)
                    else:
                        curSchemaField = schema["properties"][field["value"]]
                        newSchemaField = uiTypetoSchemaFn.get(
                            curUiType)(field, dbConfig, "value")
                        schemaDiff = diff(curSchemaField, newSchemaField)
                        if schemaDiff:
                            warnings.warn("For type:{} field:{} Difference is : \n\n {} \n".format(
                                curUiType, field["value"], schemaDiff), UserWarning)
    else:
        baseTemplate = uiConfig.get('baseTemplate', [])
        sdkTemplate = uiConfig.get('sdkTemplate', {})
        for template in baseTemplate:
            for section in template.get('sections', []):
                for group in section.get('groups', []):
                    if "preRequisites" in group:
                        continue
                    for field in group.get('fields', []):
                        if "preRequisites" in field:
                            continue
                        generateFunction = uiTypetoSchemaFn.get(
                            field['type'], None)
                        if generateFunction and field["type"] == curUiType:
                            if field["configKey"] not in schema["properties"]:
                                warnings.warn(
                                    f'{field["configKey"]} field is not in schema \n',  UserWarning)
                            else:
                                curSchemaField = schema["properties"][field["configKey"]]
                                newSchemaField = uiTypetoSchemaFn.get(
                                    curUiType)(field, dbConfig, "configKey")
                                schemaDiff = diff(curSchemaField, newSchemaField)
                                if schemaDiff:
                                    warnings.warn("For type:{} field:{} Difference is : \n\n {} \n".format(
                                        curUiType, field["configKey"], schemaDiff), UserWarning)
                        
        for field in sdkTemplate.get('fields', []):
            if "preRequisites" in field:
                continue
            generateFunction = uiTypetoSchemaFn.get(field['type'], None)
            if generateFunction:
                if generateFunction and field["type"] == curUiType:
                    if field["configKey"] not in schema["properties"]:
                        warnings.warn(
                            f'{field["configKey"]} field is not in schema \n',  UserWarning)
                    else:
                        curSchemaField = schema["properties"][field["configKey"]]
                        newSchemaField = uiTypetoSchemaFn.get(
                            curUiType)(field, dbConfig, "configKey")
                        schemaDiff = diff(curSchemaField, newSchemaField)
                        if schemaDiff:
                            warnings.warn("For type:{} field:{} Difference is : \n\n {} \n".format(
                                curUiType, field["configKey"], schemaDiff), UserWarning)


uiTypetoSchemaFn = {
    "defaultCheckbox": generate_schema_for_default_checkbox,
    "checkbox": generate_schema_for_checkbox,
    "textInput": generate_schema_for_textinput,
    "textareaInput": generate_schema_for_textarea_input,
    "singleSelect": generate_schema_for_single_select,
    "dynamicCustomForm": generate_schema_for_dynamic_custom_form,
    'dynamicForm': generate_schema_for_dynamic_form,
    'dynamicSelectForm': generate_schema_for_dynamic_select_form,
    'tagInput': generate_schema_for_tag_input,
    'timeRangePicker': generate_schema_for_time_range_picker,
    'timePicker': generate_schema_for_time_picker
}


def validate_config_consistency(name, selector, uiConfig, dbConfig, schema):
    """Generates a schema and compares it with an existing one. 
    If schemaDiff is present, it calls for individual warnings by iterating over each ui-type.

    Args:
        name (string): name of the source or destination.
        selector (string): either 'source' or 'destination'
        uiConfig (object): file content of ui-config.json.
        dbConfig (object): Configurations of db-config.json.
        schema (object): Existing schema in schema.json.
    """    
    if schema == None and uiConfig == None:
        return
    if uiConfig == None:
        print('-'*50)
        warnings.warn(f"Ui-Config is null for {name} in {selector} \n",UserWarning)
        print('-'*50)
        return
    generatedSchema = generate_schema(uiConfig, dbConfig, name, selector)
    if schema:
        schemaDiff = diff(schema, generatedSchema["configSchema"])
        if schemaDiff:
            print('-'*50)
            print(f'Schema diff for {name} in {selector}s')
            # call for individual warnings
            for uiType in uiTypetoSchemaFn.keys():
                generate_warnings_for_each_type(uiConfig, dbConfig, schema, uiType)
            # schema diff for "additionalProperties"
            if "additionalProperties" not in schema:
                print("\n Recommendation: Please set additionalProperties to False in schema.json. \n")
            # schema diff for "required"
            if "required" not in schema:
                warnings.warn('required field is not in schema \n',  UserWarning)
            else:
                curRequiredField = schema["required"]
                newRequiredField = generatedSchema["configSchema"]["required"]
                requiredFieldDiff = diff(curRequiredField, newRequiredField)
                if requiredFieldDiff:
                    warnings.warn("For required field Difference is :  \n\n {} \n".format(requiredFieldDiff), UserWarning)
            if "allOf" in generatedSchema["configSchema"]:
                curAllOfSchema = {}
                if "allOf" in schema:
                    curAllOfSchema = schema["allOf"]
                newAllOfSchema = generatedSchema["configSchema"]["allOf"]
                allOfSchemaDiff = diff(curAllOfSchema, newAllOfSchema)
                if allOfSchemaDiff:
                    warnings.warn("For allOf field Difference is :  \n\n {} \n".format(allOfSchemaDiff), UserWarning)
            if "anyOf" in generatedSchema["configSchema"]:
                curAnyOfSchema = {}
                if "anyOf" in schema:
                    curAnyOfSchema = schema["anyOf"]
                newAnyOfSchema = generatedSchema["configSchema"]["anyOf"]
                anyOfSchemaDiff = diff(curAnyOfSchema, newAnyOfSchema)
                if anyOfSchemaDiff:
                    warnings.warn("For anyOf field Difference is :  \n\n {} \n".format(anyOfSchemaDiff), UserWarning)
            print('-'*50)
    else:
        print('-'*50)
        print(f'Generated Schema for {name} in {selector}s')
        print(json.dumps(generatedSchema,indent=2))
        print('-'*50)

def get_schema_diff(name, selector):
    """ Validates the schema for the given name and selector.

    Args:
        name (string): name of the source or destination.
        selector (string): either 'source' or 'destination'.
    """    
    file_selectors = ['db-config.json', 'ui-config.json', 'schema.json']
    directory = f'./{CONFIG_DIR}/{selector}s/{name}'
    available_files = os.listdir(directory)
    file_content = {}
    for file_selector in file_selectors:
        if file_selector in available_files:
            with open (f'{directory}/{file_selector}', 'r') as f:
                file_content.update(json.loads(f.read()))
    uiConfig = file_content.get("uiConfig")
    schema = file_content.get("configSchema")
    dbConfig = file_content.get("config")
    validate_config_consistency(name, selector, uiConfig, dbConfig, schema)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generates schema.json from ui-cofing.json and db-config.json and validates against actual scheme.json')
    group = parser.add_mutually_exclusive_group()
    parser.add_argument('selector',metavar='selector',type=str,help='Enter wheather -name is a source or destination')
    group.add_argument('-name',metavar='name',type=str,help='Enter the folder name under selector')
    group.add_argument('-all',action='store_true', help='will run validation for all entites under selector')
    
    
    args = parser.parse_args()
    selector = args.selector
    if args.all:
        CONFIG_DIR = 'src/configurations'
        current_items = os.listdir(f'./{CONFIG_DIR}/{selector}s')
        for name in current_items:
            get_schema_diff(name,selector)
        
    else:
        name = args.name 
        get_schema_diff(name, selector)
    