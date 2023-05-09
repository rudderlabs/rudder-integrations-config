import json
from jsondiff import diff
import warnings
from enum import Enum

class TypeString(Enum):
    STRING = "string"
    OBJECT = "object"
    BOOLEAN = "boolean"
    ARRAY = "array"

def checkIsOldFormat(uiConfig):
    if isinstance(uiConfig, dict):
        return False
    return True

def generatePattern(field):
    pattern = ""
    fieldType = field["type"]
    # for singleSelect
    if fieldType == "singleSelect":
        pattern = "^("
        for i in range(0, len(field["options"])):
            pattern += field["options"][i]["value"]
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

def generateDefaultCheckbox(field, dbConfig):
    defaultCheckboxObj = {
        "type": TypeString.OBJECT.value,
        "properties": {
            "web": {
                "type": TypeString.BOOLEAN.value
            }
        }
    }
    return defaultCheckboxObj

def generateCheckbox(field, dbConfig):
    isSourceDependent = False
    for sourceType in dbConfig["supportedSourceTypes"]:
            if sourceType in dbConfig["destConfig"] and field["value"] in dbConfig["destConfig"][sourceType]:
                isSourceDependent = True
                break
    checkboxSchemaObj = {}
    if isSourceDependent:
        checkboxSchemaObj["type"] = TypeString.OBJECT.value
        checkboxSchemaObj["properties"] = {}
        for sourceType in dbConfig["supportedSourceTypes"]:
            if sourceType in dbConfig["destConfig"] and field["value"] in dbConfig["destConfig"][sourceType]:
                checkboxSchemaObj["properties"][sourceType] = { "type": TypeString.BOOLEAN.value}
    else:
        checkboxSchemaObj["type"] = TypeString.BOOLEAN.value
        if "default" in field:
            checkboxSchemaObj["default"] = field["default"]
    return checkboxSchemaObj

def generateTextInput(field, dbConfig):
    textInputSchemaObj = {"type": TypeString.STRING.value}
    if 'regex' in field:
        textInputSchemaObj["pattern"] = generatePattern(field)
    return textInputSchemaObj

def generateTextareaInput(field, dbConfig):
    textareaInputObj = {"type": TypeString.STRING.value}
    if 'regex' in field:
        textareaInputObj["pattern"] = generatePattern(field)
    return textareaInputObj

def generateSingleSelect(field, dbConfig):
    singleSelectObj = {"type": TypeString.STRING.value}
    singleSelectObj["pattern"] = generatePattern(field)
    if "defaultOption" in field:
        singleSelectObj["default"] = field["defaultOption"]["value"]
    return singleSelectObj

def generateDynamicCustomForm(field, dbConfig):
    dynamicCustomFormObj = {"type": TypeString.ARRAY.value}
    dynamicCustomFormItemObj = {"type": TypeString.OBJECT.value}
    dynamicCustomFormItemObj["properties"] = {}
    for customField in field["customFields"]:
        customeFieldSchemaObj = uiTypetoSchemaFn.get(customField["type"])(customField, dbConfig)
        if 'pattern' not in customeFieldSchemaObj:
            customeFieldSchemaObj["pattern"] = generatePattern(customField)
        dynamicCustomFormItemObj["properties"][customField["value"]] =  customeFieldSchemaObj

    dynamicCustomFormObj["items"] = dynamicCustomFormItemObj
    return dynamicCustomFormObj

def generateDynamicFormSchema(field, dbConfig):
    '''
        return an schema object corresponding to dynamicForm
    '''
    def generateKeyLeft():
        obj = {
            "type": TypeString.STRING.value,
            "pattern": generatePattern(field)
        }
        return obj

    dynamicFormSchemaObject = {}
    dynamicFormSchemaObject['type'] = TypeString.ARRAY.value
    dynamicFormItemObject = {}
    dynamicFormItemObject["type"] = TypeString.OBJECT.value
    dynamicFormItemObject['properties'] = {}
    dynamicFormItemObjectProps = [
        (field['keyLeft'], generateKeyLeft), (field['keyRight'], generateKeyLeft)]
    for dynamicFromItemObjectProp in dynamicFormItemObjectProps:
        dynamicFormItemObject['properties'][dynamicFromItemObjectProp[0]
                                            ] = dynamicFromItemObjectProp[1]()
    dynamicFormSchemaObject['items'] = dynamicFormItemObject
    return dynamicFormSchemaObject

def generateDynamicSelectForm(field, dbConfig):
    return generateDynamicFormSchema(field, dbConfig)

def generateTagInput(field, dbConfig):
    tagObject = {}
    tagObject["type"] = TypeString.ARRAY.value
    tagItem = {}
    tagItem['type'] = TypeString.OBJECT.value
    tagItemProps = {
        str(field['tagKey']): {
            "type": TypeString.STRING.value,
            "pattern": generatePattern(field)
        }
    }
    tagItem['properties'] = tagItemProps
    tagObject["items"] = tagObject
    return tagObject

def generateTimeRangePicker(field, dbConfig):
    timeRangeObj = {}
    timeRangeObj['type'] = TypeString.OBJECT.value
    timeRangeProps = {
        field['startTime']['value']: {'type': TypeString.STRING.value},
        field['endTime']['value']: {'type': TypeString.STRING.value}
    }
    timeRangeObj['properties'] = timeRangeProps
    timeRangeObj['required'] = list(timeRangeProps.keys())
    return timeRangeObj

def generateTimePicker(field, dbConfig):
    return {
        "type": TypeString.STRING.value
    }


def generateProperties(uiConfig, dbConfig, schemaObject, properties):
    if checkIsOldFormat(uiConfig):
        for group in uiConfig:
            fields = group.get('fields', [])
            for field in fields:
                generateFunction = uiTypetoSchemaFn.get(field['type'], None)
                if generateFunction:
                    properties[field['value']] = generateFunction(field, dbConfig)
                if field.get('required', False) == True:
                    schemaObject['required'].append(field['value'])
    else:
        pass


def generateSchema(uiConfig, dbConfig):
    newSchema = {}
    schemaObject = {}
    schemaObject['$schema'] = 'http://json-schema.org/draft-07/schema#'
    schemaObject['required'] = []
    schemaObject['type'] = "object"
    schemaObject['properties'] = {}

    generateProperties(uiConfig, dbConfig, schemaObject, schemaObject['properties'])
    newSchema['configSchema'] = schemaObject
    return newSchema


def testIndividualType(uiConfig, dbConfig, schema, curUiType):
    for uiConfigItem in uiConfig:
        for field in uiConfigItem["fields"]:
            if field["type"] == curUiType:
                if field["value"] not in schema["properties"]:
                    warnings.warn(f'{field["value"]} field is not in schema',  UserWarning)
                else:
                    curSchemaField = schema["properties"][field["value"]]
                    newSchemaField = uiTypetoSchemaFn.get(curUiType)(field, dbConfig)
                    schemaDiff = diff(newSchemaField,curSchemaField)
                    if schemaDiff:
                        warnings.warn("For type:{} field:{} Difference is : {}".format(curUiType, field["value"],schemaDiff), UserWarning)

uiTypetoSchemaFn = {
    "defaultCheckbox": generateDefaultCheckbox,
    "checkbox": generateCheckbox,
    "textInput": generateTextInput,
    "textareaInput": generateTextareaInput,
    "singleSelect": generateSingleSelect,
    "dynamicCustomForm": generateDynamicCustomForm,
    'dynamicForm': generateDynamicFormSchema,
    'dynamicSelectForm': generateDynamicSelectForm,
    'tagInput': generateTagInput,
    'timeRangePicker': generateTimeRangePicker,
    'timePicker': generateTimePicker
}


def validateSchema(uiConfig, dbConfig, schema):
    if schema == None:
        warnings.warn("Schema is null")
        return
    if uiConfig == None:
        warnings.warn("Ui-Config is null")
        return
    if not checkIsOldFormat(uiConfig):
        warnings.warn("Ui-Config is of new type")
        return
    generatedSchema = generateSchema(uiConfig, dbConfig)
    schemaDiff = diff(schema, generatedSchema["configSchema"])
    if schemaDiff:
        # call for individual warnings
        for uiType in uiTypetoSchemaFn.keys():
            testIndividualType(uiConfig, dbConfig, schema, uiType)
    return

