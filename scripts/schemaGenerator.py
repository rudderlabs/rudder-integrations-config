import json
from jsondiff import diff
import warnings

def checkIsOldFormat(uiConfig):
    if isinstance(uiConfig, dict):
        return False
    return True

def typeGenerator(fieldType):
    if fieldType == "checkbox":
        return "boolean"
    elif fieldType == "defaultCheckbox":
        return "object"
    elif fieldType == "dynamicCustomForm":
        return "array"
    else:
        return "string"


def patternGenerator(field):
    pattern = ""
    fieldType = field["type"]
    # for singleSelect
    if fieldType == "singleSelect":
        pattern += "^("
        for i in range(0, len(field["options"])):
            pattern += field["options"][i]["value"]
            if i == len(field["options"])-1:
                break
            pattern += "|"
        pattern += ")$"
    # for text Input
    elif fieldType == "textInput":
        pattern += field["regex"]
    # default pattern
    else:
        pattern +=  "(^\\{\\{.*\\|\\|(.*)\\}\\}$)|(^env[.].+)|^(.{0,100})$"
    return pattern

def defaultCheckboxSchemaGenerator(field):
    fieldType = typeGenerator(field["type"])
    schema = {
        "type": fieldType,
        "properties": {
            "web": {
                "type": "boolean"
            }
        }
    }
    return schema

def checkboxSchemaGenerator(field):
    fieldType = typeGenerator(field["type"])
    schema = {
        "type": fieldType
    }
    return schema

def textInputSchemaGenerator(field):
    fieldType = typeGenerator(field["type"])
    schema = {
        "type": fieldType,
    }
    if 'regex' in field:
        schema["pattern"] = patternGenerator(field)
    return schema

def textareaInputSchemaGenerator(field):
    fieldType = typeGenerator(field["type"])
    schema = {
        "type": fieldType,
    }    
    if 'regex' in field:
        schema["pattern"] = field["regex"]
    return schema

def singleSelectSchemaGenerator(field):
    fieldType = typeGenerator(field["type"])
    schema = {
        "type": fieldType,
    }
    schema["pattern"] = patternGenerator(field)
    if "defaultOption" in field:
        schema["default"] = field["defaultOption"]["value"]
    return schema

def dynamicCustomFormSchemaGenerator(field):
    fieldType = typeGenerator(field["type"])
    schema = {
        "type": fieldType,
        "items": {
            "type": "object",
            "properties": {

            }
        } 
    }
    for customField in field["customFields"]:
        customeFieldSchema = uiTypetoSchemaType.get(customField["type"])(customField)
        schema["items"]["properties"][customField["value"]] = customeFieldSchema
    return schema

def generateDynamicFormSchema(field):
    '''
        return an schema object corresponding to dynamicForm
    '''
    def generateFromAndTo():
        obj = {
            "type": typeGenerator(field["type"]),
            "pattern": patternGenerator(field)
        }
        return obj

    dynamicFormSchemaObject = {}
    dynamicFormSchemaObject['type'] = "array"
    dynamicFormItemObject = {}
    dynamicFormItemObject["type"] = "object"
    dynamicFormItemObject['properties'] = {}
    dynamicFormItemObjectProps = [
        ('from', generateFromAndTo), ('to', generateFromAndTo)]
    for dynamicFromItemObjectProp in dynamicFormItemObjectProps:
        dynamicFormItemObject['properties'][dynamicFromItemObjectProp[0]
                                            ] = dynamicFromItemObjectProp[1]()
    dynamicFormSchemaObject['items'] = dynamicFormItemObject
    return dynamicFormSchemaObject

def generateDynamicSelectForm(field):
    return generateDynamicFormSchema(field)

def generateTagInput(field):
    tagObject = {}
    tagObject["type"] = "array"
    tagItem = {}
    tagItem['type'] = "object"
    tagItemProps = {
        str(field['tagKey']): {
            "type": typeGenerator(field["type"]),
            "pattern": patternGenerator(field)
        }
    }
    tagItem['properties'] = tagItemProps
    tagObject["items"] = tagObject
    return tagObject

def generateTimeRangePicker(field):
    timeRangeObj = {}
    timeRangeObj['type'] = "object"
    timeRangeProps = {
        field['startTime']['value']: {'type': typeGenerator(field["type"])},
        field['endTime']['value']: {'type': typeGenerator(field["type"])}
    }
    timeRangeObj['properties'] = timeRangeProps
    timeRangeObj['required'] = list(timeRangeProps.keys())
    return timeRangeObj

def generateTimePicker(field):
    return {
        "type": typeGenerator(field["type"])
    }


def generateProperties(uiConfig, schemaObject, properties):
    if checkIsOldFormat(uiConfig):
        for group in uiConfig:
            fields = group.get('fields', [])
            for field in fields:
                generateFunction = uiTypetoSchemaType.get(field['type'], None)
                if generateFunction:
                    properties[field['value']] = generateFunction(field)
                if field.get('required', False) == True:
                    schemaObject['required'].append(field['value'])
    else:
        pass


def generateSchema(uiConfig):
    newSchema = {}
    schemaObject = {}
    schemaObject['$schema'] = 'http://json-schema.org/draft-07/schema#'
    schemaObject['required'] = []
    schemaObject['type'] = "object"
    schemaObject['properties'] = {}

    generateProperties(uiConfig, schemaObject, schemaObject['properties'])
    newSchema['configSchema'] = schemaObject
    return newSchema


def testIndividualType(uiConfig, schema, curType):
    for uiConfigItem in uiConfig:
        for field in uiConfigItem["fields"]:
            if field["type"] == curType:
                if field["value"] not in schema["properties"]:
                    warnings.warn(f'{field["value"]} field is not in schema',  UserWarning)
                else:
                    curSchemaField = schema["properties"][field["value"]]
                    newSchemaField = uiTypetoSchemaType.get(curType)(field)
                    schemaDiff = diff(newSchemaField,curSchemaField)
                    if schemaDiff:
                        warnings.warn("Difference is : {}".format(schemaDiff), UserWarning)

uiTypetoSchemaType = {
    "defaultCheckbox": defaultCheckboxSchemaGenerator,
    "checkbox": checkboxSchemaGenerator,
    "textInput": textInputSchemaGenerator,
    "textareaInput": textareaInputSchemaGenerator,
    "singleSelect": singleSelectSchemaGenerator,
    "dynamicCustomForm": dynamicCustomFormSchemaGenerator,
    'dynamicForm': generateDynamicFormSchema,
    'dynamicSelectForm': generateDynamicSelectForm,
    'tagInput': generateTagInput,
    'timeRangePicker': generateTimeRangePicker,
    'timePicker': generateTimePicker
}


def validateSchema(uiConfig, schema):
    if schema == None:
        warnings.warn("Schema in null")
        return
    if uiConfig == None:
        warnings.warn("Ui-Config in null")
        return
    if not checkIsOldFormat(uiConfig):
        warnings.warn("Ui-Config is of new type")
        return
    generatedSchema = generateSchema(uiConfig)
    schemaDiff = diff(schema, generatedSchema)
    if schemaDiff:
        # call for individual warnings
        for uiType in uiTypetoSchemaType.keys():
            testIndividualType(uiConfig, schema, uiType)
    return









