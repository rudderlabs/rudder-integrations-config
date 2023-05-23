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


def generalize_regex_pattern(field):
    '''
        Returns generated pattern based on the field type.
        For singleSelect, the pattern is generated by iterating over options.
        A default pattern is present for others, which gets appended with regex if regex is present in the field, 
        else with ^(.{0,100}).
    '''
    pattern = ""
    fieldType = field["type"]
    # for singleSelect
    if fieldType == "singleSelect":
        pattern = "^("
        for i in range(0, len(field["options"])):
            if isinstance(field["options"][i], int) or isinstance(field["options"][i], str):
                pattern += str(field["options"][i])
            else:
                pattern += str(field["options"][i]["value"])
            if i == len(field["options"])-1:
                break
            pattern += "|"
        pattern += ")$"
    # for others
    else:
        pattern = "(^\\{\\{.*\\|\\|(.*)\\}\\}$)|(^env[.].+)|"
        if "regex" in field:
            pattern += field["regex"]
        else:
            pattern += '^(.{0,100})$'
    return pattern


def is_dest_field_dependent_on_source(field, dbConfig, schema_field_name):
    '''
        Checks if the given field is source-specific by using db-config.
        All the sources are listed in supportedSourceTypes, 
        and their fields are listed inside destConfig with the key as the sourceType.
    ''' 
    if not dbConfig:
        return False
    for sourceType in dbConfig["supportedSourceTypes"]:
        if sourceType in dbConfig["destConfig"] and field[schema_field_name] in dbConfig["destConfig"][sourceType]:
            return True
    return False


def generate_schema_for_default_checkbox(field, dbConfig, schema_field_name):
    '''
        Returns an schema object corresponding to defaultCheckbox.
    '''
    defaultCheckboxObj = {
        "type": FieldTypeEnum.OBJECT.value,
        "properties": {
            "web": {
                "type": FieldTypeEnum.BOOLEAN.value
            }
        }
    }
    return defaultCheckboxObj


def generate_schema_for_checkbox(field, dbConfig, schema_field_name):
    '''
        Returns an schema object corresponding to checkbox.
    '''
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
    return checkboxSchemaObj


def generate_schema_for_textinput(field, dbConfig, schema_field_name):
    '''
        Returns an schema object corresponding to textInput.
    '''
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
    return textInputSchemaObj


def generate_schema_for_textarea_input(field, dbConfig, schema_field_name):
    '''
        Returns an schema object corresponding to textareaInput.
    '''
    textareaInputObj = {"type": FieldTypeEnum.STRING.value}
    if 'regex' in field:
        textareaInputObj["pattern"] = generalize_regex_pattern(field)
    return textareaInputObj


def generate_schema_for_single_select(field, dbConfig, schema_field_name):
    '''
        Returns an schema object corresponding to singleSelect.
    '''
    singleSelectObj = {"type": FieldTypeEnum.STRING.value}
    singleSelectObj["pattern"] = generalize_regex_pattern(field)
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
    return singleSelectObj


def generate_schema_for_dynamic_custom_form(field, dbConfig, schema_field_name):
    '''
        Returns an schema object corresponding to dynamicCustomForm.
    '''
    dynamicCustomFormObj = {}
    dynamicCustomFormObj["type"] = FieldTypeEnum.ARRAY.value
    dynamicCustomFormItemObj = {}
    dynamicCustomFormItemObj["type"] = FieldTypeEnum.OBJECT.value
    dynamicCustomFormItemObj["properties"] = {}
    for customField in field["customFields"]:
        customeFieldSchemaObj = uiTypetoSchemaFn.get(customField["type"])(customField, dbConfig, schema_field_name)
        isCustomFieldDependentOnSource = is_dest_field_dependent_on_source(customField, dbConfig, schema_field_name)
        if 'pattern' not in customeFieldSchemaObj and not isCustomFieldDependentOnSource:
            customeFieldSchemaObj["pattern"] = generalize_regex_pattern(customField)
        # If the custom field is source dependent, we remove the source keys as it's not required inside custom fields, rather they need to moved to top.
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
    return dynamicCustomFormObj


def generate_schema_for_dynamic_form_schema(field, dbConfig, schema_field_name):
    '''
        Returns an schema object corresponding to dynamicForm.
    '''
    def generate_key_left():
        obj = {
            "type": FieldTypeEnum.STRING.value,
            "pattern": generalize_regex_pattern(field)
        }
        return obj

    dynamicFormSchemaObject = {}
    dynamicFormSchemaObject['type'] = FieldTypeEnum.ARRAY.value
    dynamicFormItemObject = {}
    dynamicFormItemObject["type"] = FieldTypeEnum.OBJECT.value
    dynamicFormItemObject['properties'] = {}
    dynamicFormItemObjectProps = [
        (field['keyLeft'], generate_key_left), (field['keyRight'], generate_key_left)]
    for dynamicFromItemObjectProp in dynamicFormItemObjectProps:
        dynamicFormItemObject['properties'][dynamicFromItemObjectProp[0]
                                            ] = dynamicFromItemObjectProp[1]()
    dynamicFormSchemaObject['items'] = dynamicFormItemObject
    return dynamicFormSchemaObject


def generate_schema_for_dynamic_select_form(field, dbConfig, schema_field_name):
    '''
        Returns an schema object corresponding to dynamicSelectForm.
    '''
    return generate_schema_for_dynamic_form_schema(field, dbConfig, schema_field_name)


def generate_schema_for_tag_input(field, dbConfig, schema_field_name):
    '''
        Returns an schema object corresponding to tagInput.
    '''
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
    return tagObject


def generate_schema_for_time_range_picker(field, dbConfig, schema_field_name):
    '''
        Returns an schema object corresponding to timeRangePicker.
    '''
    timeRangeObj = {}
    timeRangeObj['type'] = FieldTypeEnum.OBJECT.value
    timeRangeProps = {
        field['startTime']['value']: {'type': FieldTypeEnum.STRING.value},
        field['endTime']['value']: {'type': FieldTypeEnum.STRING.value}
    }
    timeRangeObj['properties'] = timeRangeProps
    timeRangeObj['required'] = list(timeRangeProps.keys())
    return timeRangeObj


def generate_schema_for_time_picker(field, dbConfig, schema_field_name):
    '''
        Returns an schema object corresponding to timePicker.
    '''
    return {
        "type": FieldTypeEnum.STRING.value
    }

def compare_pre_requisite_fields(fieldA, fieldB):
    '''
        Compares two preRequisiteFields and checks if they match.
        If all fields have the same 'name' and 'selectedValue', then it returns True.
    '''
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
    '''
        Returns the list of unique preRequisiteFields present in a uiConfig.
    '''
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
    '''
        Returns the if object for the given preRequisiteField. 
        The preRequisiteField becomes an if condition in the schema.
    '''
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
    '''
        Returns the allOf structure of schema, empty if not required.
        
        Finds the list of unique preRequisiteFields.
        For each of the preRequisiteField, the properties are found by matching the current preRequisiteField.
        preRequisiteField becomes if block and corresponding properties become then block.
    '''
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
    '''
        Takes properties of two if Objects and returns a list of common and opposite properties.
        Common properties have same value in both A and B.
        Returns None if a property is absent in A or B or If a property has a different value (not opposite).
        
        Example:
            schema_field_name = 'value'
            propertiesA = { 'storage' : {'const' : 'S3'}, 'useStorage' : {'const': True}}
            propertiesB = { 'storage' : {'const' : 'S3'}, 'useStorage' : {'const': False}}

            Returns 
            commonProperties = [{'key': 'storage', 'value':'S3'}]
            oppositeProperties = [{'key': 'useStorage', 'value': 'True'}]

    '''
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
    '''
        Compares the ifPropsA and ifObjectB, if they have same properties and values.
     
        Example:
        schema_field_name = 'value' 
        ifPropsA = [{'key': 'storage', 'value': 'S3'}, {'key': 'deploy', 'value': 'web'}]
        ifObjectA  = {'storage': {'const': 'S3'}, 'deploy': {'const': 'web'}}
        
        Returns: True
    '''
    for ifProp in ifPropsA:
        if ifProp["key"] not in ifObjectB:
            return False
        if ifProp[schema_field_name] != ifObjectB[ifProp["key"]]["const"]:
            return False
    return True

def find_index_to_place_anyOf(ifProp, allOfItemList, schema_field_name):
    '''
        Returns the index of the item in allOfItemList having same if properties as that of ifProp, -1 if no match found.

        Example:
        schema_field_name = 'value'
        ifProp = [{'key': 'storage', 'value': 'S3'}, {'key': 'deploy', 'value': 'web'}]
        allOfItemList = [
            {'if': {'properties': {'storage': { const: 'GCS' }}},'then': { ... }},
            {'if': {'properties': {'storage': { const: 'S3' },'deploy': { const: 'web' }}},'then': { ... }}
        ]

        Returns: 1
    '''
    if not ifProp:
        return -1
    length = len(allOfItemList)
    for index in range(length):
        if "if" in allOfItemList[index] and check_if_conditions_match(ifProp, allOfItemList[index]["if"]["properties"], schema_field_name):
            return index
    return -1

def generate_schema_for_anyOf(allOfItemList, schema_field_name):
    '''
        Takes in two parameters allOfItemList and schema_field_name and returns updated allOf Items list.
        It checks for all pairs of allOf Items, if their "if" conditions have a "if-else" based structure rather than "if-if". 
        Both the items are deleted and replaced by a anyOf structure. 
    '''
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
                # AnyOf object is placed at index of if-then block having same if properties as of common properties else at end. 
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
    '''
        Returns the connection mode object present in new schema types.
    '''
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
    '''
        Generates corresponding schema properties by iterating over each of the ui-config fields.
    '''
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
                if field.get('required', False) == True:
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
                            if template.get('title', "") == "Initial setup":
                                schemaObject['required'].append(
                                    field['configKey'])

            for field in sdkTemplate.get('fields', []):
                generateFunction = uiTypetoSchemaFn.get(field['type'], None)
                if generateFunction:
                    properties[field['configKey']] = generateFunction(
                        field, dbConfig, 'configKey')
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
    '''
        Returns the generated schema from uiConfig and dbConfig.
    '''
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
            schemaObject['anyOf'] = allOfSchemaObj[0]
        else:
            schemaObject['allOf'] = allOfSchemaObj
    generate_schema_properties(uiConfig, dbConfig, schemaObject,
                       schemaObject['properties'], name, selector)
    newSchema['configSchema'] = schemaObject
    return newSchema

def generate_warnings_for_each_type(uiConfig, dbConfig, schema, curUiType):
    '''
        Generates warning for schema difference in each ui-type individually.
    '''
    if is_old_format(uiConfig):
        for uiConfigItem in uiConfig:
            for field in uiConfigItem["fields"]:
                if field["type"] == curUiType:
                    if field["value"] not in schema["properties"]:
                        warnings.warn(
                            f'{field["value"]} field is not in schema \n',  UserWarning)
                    else:
                        curSchemaField = schema["properties"][field["value"]]
                        newSchemaField = uiTypetoSchemaFn.get(
                            curUiType)(field, dbConfig, "value")
                        schemaDiff = diff(newSchemaField, curSchemaField)
                        if schemaDiff:
                            warnings.warn("For type:{} field:{} Difference is : \n\n {} \n".format(
                                curUiType, field["value"], schemaDiff), UserWarning)
    else:
        baseTemplate = uiConfig.get('baseTemplate', [])
        sdkTemplate = uiConfig.get('sdkTemplate', {})
        for template in baseTemplate:
            for section in template.get('sections', []):
                for group in section.get('groups', []):
                    for field in group.get('fields', []):
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
                                schemaDiff = diff(newSchemaField, curSchemaField)
                                if schemaDiff:
                                    warnings.warn("For type:{} field:{} Difference is : \n\n {} \n".format(
                                        curUiType, field["configKey"], schemaDiff), UserWarning)
                        
        for field in sdkTemplate.get('fields', []):
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
                        schemaDiff = diff(newSchemaField, curSchemaField)
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
    'dynamicForm': generate_schema_for_dynamic_form_schema,
    'dynamicSelectForm': generate_schema_for_dynamic_select_form,
    'tagInput': generate_schema_for_tag_input,
    'timeRangePicker': generate_schema_for_time_range_picker,
    'timePicker': generate_schema_for_time_picker
}


def validate_config_consistency(name, selector, uiConfig, dbConfig, schema):
    '''
        Generates a schema and compares it with an existing one. 
        If schemaDiff is there, it calls for individual warnings.
    '''
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
            if "allOf" in schema:
                curAllOfSchema = schema["allOf"]
                newAllOfSchema = generate_schema_for_allOf(uiConfig, dbConfig, "value")
                allOfSchemaDiff = diff(newAllOfSchema, curAllOfSchema)
                if allOfSchemaDiff:
                    warnings.warn("For allOf field Difference is :  \n\n {} \n".format(allOfSchemaDiff), UserWarning)
            if "anyOf" in schema:
                curAnyOfSchema = schema["anyOf"]
                newAnyOfSchema = generate_schema_for_allOf(uiConfig, dbConfig, "value")
                anyOfSchemaDiff = diff(newAnyOfSchema, curAnyOfSchema)
                if anyOfSchemaDiff:
                    warnings.warn("For anyOf field Difference is :  \n\n {} \n".format(anyOfSchemaDiff), UserWarning)
            print('-'*50)
    else:
        print('-'*50)
        print(f'Generated Schema for {name} in {selector}s')
        print(json.dumps(generatedSchema,indent=2))
        print('-'*50)

def get_schema_diff(name, selector):
    '''
        Generates individual warnings for a given name and selector.
    '''
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