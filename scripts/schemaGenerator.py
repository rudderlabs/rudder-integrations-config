import os
import sys
import warnings
import json
from jsondiff import diff
from enum import Enum

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
    if not dbConfig:
        return False
    for sourceType in dbConfig["supportedSourceTypes"]:
        if sourceType in dbConfig["destConfig"] and field[schema_field_name] in dbConfig["destConfig"][sourceType]:
            return True
    return False


def generate_schema_for_default_checkbox(field, dbConfig, schema_field_name):
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
    isSourceDependent = is_dest_field_dependent_on_source(field, dbConfig, schema_field_name)
    checkboxSchemaObj = {}
    if isSourceDependent:
        checkboxSchemaObj["type"] = FieldTypeEnum.OBJECT.value
        checkboxSchemaObj["properties"] = {}
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
    textInputSchemaObj = {}
    isSourceDependent = is_dest_field_dependent_on_source(field, dbConfig, schema_field_name)
    if isSourceDependent:
        textInputSchemaObj["type"] = FieldTypeEnum.OBJECT.value
        textInputSchemaObj["properties"] = {}
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
    textareaInputObj = {"type": FieldTypeEnum.STRING.value}
    if 'regex' in field:
        textareaInputObj["pattern"] = generalize_regex_pattern(field)
    return textareaInputObj


def generate_schema_for_single_select(field, dbConfig, schema_field_name):
    singleSelectObj = {"type": FieldTypeEnum.STRING.value}
    singleSelectObj["pattern"] = generalize_regex_pattern(field)
    if "defaultOption" in field:
        singleSelectObj["default"] = field["defaultOption"]["value"]

    isSourceDependent = is_dest_field_dependent_on_source(field, dbConfig, schema_field_name)
    if isSourceDependent:
        newSingleSelectObj = {"type": FieldTypeEnum.OBJECT.value}
        newSingleSelectObj["properties"] = {}
        for sourceType in dbConfig["supportedSourceTypes"]:
            if sourceType in dbConfig["destConfig"] and field[schema_field_name] in dbConfig["destConfig"][sourceType]:
                newSingleSelectObj["properties"][sourceType] = singleSelectObj
        singleSelectObj = newSingleSelectObj
    return singleSelectObj


def generate_schema_for_dynamic_custom_form(field, dbConfig, schema_field_name):
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
        if isCustomFieldDependentOnSource:
            for sourceType in dbConfig["supportedSourceTypes"]:
                if sourceType in dbConfig["destConfig"] and field[schema_field_name] in dbConfig["destConfig"][sourceType]:
                    customeFieldSchemaObj = customeFieldSchemaObj["properties"][sourceType]
                    break
        dynamicCustomFormItemObj["properties"][customField[schema_field_name]] =  customeFieldSchemaObj

    dynamicCustomFormObj["items"] = dynamicCustomFormItemObj
    isSourceDependent = is_dest_field_dependent_on_source(field, dbConfig, schema_field_name)
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
        return an schema object corresponding to dynamicForm
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
    return generate_schema_for_dynamic_form_schema(field, dbConfig, schema_field_name)


def generate_schema_for_tag_input(field, dbConfig, schema_field_name):
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
    return {
        "type": FieldTypeEnum.STRING.value
    }

def compare_pre_requisite_fields(fieldA, fieldB):
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
    allOfItemList = generate_schema_for_anyOf(allOfItemList, schema_field_name)
    return allOfItemList

def get_common_and_opposite_fields(propertiesA, propertiesB, schema_field_name):
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
    for ifProp in ifPropsA:
        if ifProp["key"] not in ifObjectB:
            return False
        if ifProp[schema_field_name] != ifObjectB[ifProp["key"]]["const"]:
            return False
    return True

def find_index_to_place_anyOf(ifProp, allOfItemList, schema_field_name):
    if not ifProp:
        return -1
    length = len(allOfItemList)
    for index in range(length):
        if "if" in allOfItemList[index] and check_if_conditions_match(ifProp, allOfItemList[index]["if"]["properties"], schema_field_name):
            return index
    return -1

def generate_schema_for_anyOf(allOfItemList, schema_field_name):
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
            
            schemaObject['properties']['useNativeSDK'] = generate_schema_for_checkbox({"type":"checkbox", 
                                                                           "value":"useNativeSDK"}, dbConfig, "value")
            schemaObject['properties']['connectionMode'] = generate_connection_mode(dbConfig)
        else:
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
        if len(allOfSchemaObj) == 1:
            schemaObject['anyOf'] = allOfSchemaObj[0]
        else:
            schemaObject['allOf'] = allOfSchemaObj
    generate_schema_properties(uiConfig, dbConfig, schemaObject,
                       schemaObject['properties'], name, selector)
    newSchema['configSchema'] = schemaObject
    return newSchema

def generate_warnings_for_each_type(uiConfig, dbConfig, schema, curUiType):
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
    if len(sys.argv) < 3:
        print("Please provide selector and name")
    else:
        selector = sys.argv[1]
        name = sys.argv[2]
        get_schema_diff(name, selector)