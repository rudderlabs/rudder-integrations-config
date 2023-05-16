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


def checkIsDependentOnSource(field, dbConfig, valueProp):
    if not dbConfig:
        return False
    for sourceType in dbConfig["supportedSourceTypes"]:
        if sourceType in dbConfig["destConfig"] and field[valueProp] in dbConfig["destConfig"][sourceType]:
            return True
    return False


def generateDefaultCheckbox(field, dbConfig, valueProp):
    defaultCheckboxObj = {
        "type": TypeString.OBJECT.value,
        "properties": {
            "web": {
                "type": TypeString.BOOLEAN.value
            }
        }
    }
    return defaultCheckboxObj


def generateCheckbox(field, dbConfig, valueProp):
    isSourceDependent = checkIsDependentOnSource(field, dbConfig, valueProp)
    checkboxSchemaObj = {}
    if isSourceDependent:
        checkboxSchemaObj["type"] = TypeString.OBJECT.value
        checkboxSchemaObj["properties"] = {}
        for sourceType in dbConfig["supportedSourceTypes"]:
            if sourceType in dbConfig["destConfig"] and field[valueProp] in dbConfig["destConfig"][sourceType]:
                checkboxSchemaObj["properties"][sourceType] = {
                    "type": TypeString.BOOLEAN.value}
    else:
        checkboxSchemaObj["type"] = TypeString.BOOLEAN.value
        if "default" in field:
            checkboxSchemaObj["default"] = field["default"]
    return checkboxSchemaObj


def generateTextInput(field, dbConfig, valueProp):
    textInputSchemaObj = {}
    isSourceDependent = checkIsDependentOnSource(field, dbConfig, valueProp)
    if isSourceDependent:
        textInputSchemaObj["type"] = TypeString.OBJECT.value
        textInputSchemaObj["properties"] = {}
        for sourceType in dbConfig["supportedSourceTypes"]:
            if sourceType in dbConfig["destConfig"] and field[valueProp] in dbConfig["destConfig"][sourceType]:
                textInputSchemaObj["properties"][sourceType] = {
                    "type": TypeString.STRING.value}
                if 'regex' in field:
                    textInputSchemaObj["properties"][sourceType]["pattern"] = field["regex"]
    else:
        textInputSchemaObj = {"type": TypeString.STRING.value}
        if 'regex' in field:
            textInputSchemaObj["pattern"] = generatePattern(field)
    return textInputSchemaObj


def generateTextareaInput(field, dbConfig, valueProp):
    textareaInputObj = {"type": TypeString.STRING.value}
    if 'regex' in field:
        textareaInputObj["pattern"] = generatePattern(field)
    return textareaInputObj


def generateSingleSelect(field, dbConfig, valueProp):
    singleSelectObj = {"type": TypeString.STRING.value}
    singleSelectObj["pattern"] = generatePattern(field)
    if "defaultOption" in field:
        singleSelectObj["default"] = field["defaultOption"]["value"]

    isSourceDependent = checkIsDependentOnSource(field, dbConfig, valueProp)
    if isSourceDependent:
        newSingleSelectObj = {"type": TypeString.OBJECT.value}
        newSingleSelectObj["properties"] = {}
        for sourceType in dbConfig["supportedSourceTypes"]:
            if sourceType in dbConfig["destConfig"] and field[valueProp] in dbConfig["destConfig"][sourceType]:
                newSingleSelectObj["properties"][sourceType] = singleSelectObj
        singleSelectObj = newSingleSelectObj
    return singleSelectObj


def generateDynamicCustomForm(field, dbConfig, valueProp):
    dynamicCustomFormObj = {}
    dynamicCustomFormObj["type"] = TypeString.ARRAY.value
    dynamicCustomFormItemObj = {}
    dynamicCustomFormItemObj["type"] = TypeString.OBJECT.value
    dynamicCustomFormItemObj["properties"] = {}
    for customField in field["customFields"]:
        customeFieldSchemaObj = uiTypetoSchemaFn.get(customField["type"])(customField, dbConfig, valueProp)
        isCustomFieldDependentOnSource = checkIsDependentOnSource(customField, dbConfig, valueProp)
        if 'pattern' not in customeFieldSchemaObj and not isCustomFieldDependentOnSource:
            customeFieldSchemaObj["pattern"] = generatePattern(customField)
        if isCustomFieldDependentOnSource:
            for sourceType in dbConfig["supportedSourceTypes"]:
                if sourceType in dbConfig["destConfig"] and field[valueProp] in dbConfig["destConfig"][sourceType]:
                    customeFieldSchemaObj = customeFieldSchemaObj["properties"][sourceType]
                    break
        dynamicCustomFormItemObj["properties"][customField[valueProp]] =  customeFieldSchemaObj

    dynamicCustomFormObj["items"] = dynamicCustomFormItemObj
    isSourceDependent = checkIsDependentOnSource(field, dbConfig, valueProp)
    if isSourceDependent:
        newDynamicCustomFormObj = {"type": TypeString.OBJECT.value}
        newDynamicCustomFormObj["properties"] = {}
        for sourceType in dbConfig["supportedSourceTypes"]:
            if sourceType in dbConfig["destConfig"] and field[valueProp] in dbConfig["destConfig"][sourceType]:
                newDynamicCustomFormObj["properties"][sourceType] = dynamicCustomFormObj
        dynamicCustomFormObj = newDynamicCustomFormObj
    return dynamicCustomFormObj


def generateDynamicFormSchema(field, dbConfig, valueProp):
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


def generateDynamicSelectForm(field, dbConfig, valueProp):
    return generateDynamicFormSchema(field, dbConfig, valueProp)


def generateTagInput(field, dbConfig, valueProp):
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
    tagObject["items"] = tagItem
    return tagObject


def generateTimeRangePicker(field, dbConfig, valueProp):
    timeRangeObj = {}
    timeRangeObj['type'] = TypeString.OBJECT.value
    timeRangeProps = {
        field['startTime']['value']: {'type': TypeString.STRING.value},
        field['endTime']['value']: {'type': TypeString.STRING.value}
    }
    timeRangeObj['properties'] = timeRangeProps
    timeRangeObj['required'] = list(timeRangeProps.keys())
    return timeRangeObj


def generateTimePicker(field, dbConfig, valueProp):
    return {
        "type": TypeString.STRING.value
    }

def comparePreRequisiteObject(fieldA, fieldB):
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

def getUniquePreRequisiteFields(uiConfig):
    preRequisiteFieldsList = []
    for group in uiConfig:
        fields = group.get('fields', [])
        for field in fields:
            if "preRequisiteField" not in field:
                continue
            isPresent = False
            for preRequisiteField in preRequisiteFieldsList:
                if comparePreRequisiteObject(preRequisiteField, field["preRequisiteField"]):
                    isPresent = True
                    break
            if not isPresent:
                preRequisiteFieldsList.append(field["preRequisiteField"])
    return preRequisiteFieldsList


def generateIfObject(preRequisiteField):
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


def generateAllOfSchema(uiConfig, dbConfig, valueProp):
    allOfItemList = []
    preRequisiteFieldsList = getUniquePreRequisiteFields(uiConfig)
    for preRequisiteField in preRequisiteFieldsList:
        ifObj = generateIfObject(preRequisiteField)
        thenObj = {"properties": {}, "required": []}
        allOfItemObj = {"if": ifObj}
        for group in uiConfig:
            fields = group.get('fields', [])
            for field in fields:
                if "preRequisiteField" not in field:
                    continue
                if comparePreRequisiteObject(field["preRequisiteField"], preRequisiteField):
                    thenObj["properties"][field[valueProp]] = uiTypetoSchemaFn.get(field["type"])(field, dbConfig, valueProp)
                    if "required" in field and field["required"] == True:
                        thenObj["required"].append(field[valueProp])
        allOfItemObj["then"] = thenObj
        allOfItemList.append(allOfItemObj)
    allOfItemList = generateAnyOfSchema(allOfItemList, valueProp)
    return allOfItemList

def getCommonAndOppositeFields(propertiesA, propertiesB, valueProp):
    keysListA = list(propertiesA.keys())
    keysListB = list(propertiesB.keys())
    commonProperties = []
    oppositeProperties = []
    for key in keysListA:
        if key not in keysListB:
            return None, None
        if propertiesA[key]["const"] == propertiesB[key]["const"]:
            commonProperties.append({"key": key, valueProp: propertiesA[key]["const"]})
        elif type(propertiesA[key]["const"]) == bool and propertiesA[key]["const"] != propertiesB[key]["const"]:
            oppositeProperties.append({"key": key, valueProp: propertiesA[key]["const"]})
        else:
            return None, None
    return commonProperties, oppositeProperties

def checkIfConditionsMatch(ifPropsA, ifObjectB, valueProp):
    for ifProp in ifPropsA:
        if ifProp["key"] not in ifObjectB:
            return False
        if ifProp[valueProp] != ifObjectB[ifProp["key"]]["const"]:
            return False
    return True

def findIndexToPlaceAnyOf(ifProp, allOfItemList, valueProp):
    if not ifProp:
        return -1
    length = len(allOfItemList)
    for index in range(length):
        if "if" in allOfItemList[index] and checkIfConditionsMatch(ifProp, allOfItemList[index]["if"]["properties"], valueProp):
            return index
    return -1

def generateAnyOfSchema(allOfItemList, valueProp):
    length = len(allOfItemList)
    delIndices = []
    for i in range(0, length):
        for j in range(i+1, length):
            ifPropertiesA = allOfItemList[i]["if"]["properties"]
            thenPropertiesA = allOfItemList[i]["then"]
            ifPropertiesB = allOfItemList[j]["if"]["properties"]
            thenPropertiesB = allOfItemList[j]["then"]
            commonIfProp, oppositeIfProp = getCommonAndOppositeFields(ifPropertiesA, ifPropertiesB, valueProp)
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
                indexToPlace = findIndexToPlaceAnyOf(commonIfProp, allOfItemList, valueProp)
                if indexToPlace == -1:
                    allOfItemList.append(anyOfObj)
                else:
                    allOfItemList[indexToPlace]["then"]["anyOf"] = anyOfObj
                delIndices.append(i)
                delIndices.append(j)
    allOfItemList = [allOfItemList[index] for index in range(len(allOfItemList)) if index not in delIndices]
    return allOfItemList

def generateConnectionMode(dbConfig):
    connectionObj = {"type": TypeString.OBJECT.value}
    connectionObj["properties"] = {}
    for sourceType in dbConfig["supportedSourceTypes"]:
            if sourceType in dbConfig["supportedConnectionModes"]:
                connectionItemObj = {"type": TypeString.STRING.value}
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


def generateProperties(uiConfig, dbConfig, schemaObject, properties, name, selector):
    if checkIsOldFormat(uiConfig):
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
            
            schemaObject['properties']['useNativeSDK'] = generateCheckbox({"type":"checkbox", 
                                                                           "value":"useNativeSDK"}, dbConfig, "value")
            schemaObject['properties']['connectionMode'] = generateConnectionMode(dbConfig)
        else:
            def generateConfigProps(config):
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
                    generateConfigProps(auth_config)

            generateConfigProps(config)


def generateSchema(uiConfig, dbConfig, name, selector):
    newSchema = {}
    schemaObject = {}
    schemaObject['$schema'] = 'http://json-schema.org/draft-07/schema#'
    schemaObject['required'] = []
    schemaObject['type'] = "object"
    schemaObject['properties'] = {}
    allOfSchemaObj = {}
    if checkIsOldFormat(uiConfig):
        allOfSchemaObj = generateAllOfSchema(uiConfig, dbConfig, "value")
    if allOfSchemaObj:
        if len(allOfSchemaObj) == 1:
            schemaObject['anyOf'] = allOfSchemaObj[0]
        else:
            schemaObject['allOf'] = allOfSchemaObj
    generateProperties(uiConfig, dbConfig, schemaObject,
                       schemaObject['properties'], name, selector)
    newSchema['configSchema'] = schemaObject
    return newSchema

def testIndividualType(uiConfig, dbConfig, schema, curUiType):
    if checkIsOldFormat(uiConfig):
        for uiConfigItem in uiConfig:
            for field in uiConfigItem["fields"]:
                if field["type"] == curUiType:
                    if field["value"] not in schema["properties"]:
                        warnings.warn(
                            f'{field["value"]} field is not in schema',  UserWarning)
                    else:
                        curSchemaField = schema["properties"][field["value"]]
                        newSchemaField = uiTypetoSchemaFn.get(
                            curUiType)(field, dbConfig, "value")
                        schemaDiff = diff(newSchemaField, curSchemaField)
                        if schemaDiff:
                            warnings.warn("For type:{} field:{} Difference is : {}".format(
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
                                    f'{field["configKey"]} field is not in schema',  UserWarning)
                            else:
                                curSchemaField = schema["properties"][field["configKey"]]
                                newSchemaField = uiTypetoSchemaFn.get(
                                    curUiType)(field, dbConfig, "configKey")
                                schemaDiff = diff(newSchemaField, curSchemaField)
                                if schemaDiff:
                                    warnings.warn("For type:{} field:{} Difference is : {}".format(
                                        curUiType, field["configKey"], schemaDiff), UserWarning)
                        
        for field in sdkTemplate.get('fields', []):
            generateFunction = uiTypetoSchemaFn.get(field['type'], None)
            if generateFunction:
                if generateFunction and field["type"] == curUiType:
                    if field["configKey"] not in schema["properties"]:
                        warnings.warn(
                            f'{field["configKey"]} field is not in schema',  UserWarning)
                    else:
                        curSchemaField = schema["properties"][field["configKey"]]
                        newSchemaField = uiTypetoSchemaFn.get(
                            curUiType)(field, dbConfig, "configKey")
                        schemaDiff = diff(newSchemaField, curSchemaField)
                        if schemaDiff:
                            warnings.warn("For type:{} field:{} Difference is : {}".format(
                                curUiType, field["configKey"], schemaDiff), UserWarning)


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


def validateSchema(uiConfig, dbConfig, schema, name, selector):
    if schema == None and uiConfig == None:
        return
    if uiConfig == None:
        print('-'*50)
        warnings.warn(f"Ui-Config is null for {name} in {selector}",UserWarning)
        print('-'*50)
        return
    generatedSchema = generateSchema(uiConfig, dbConfig, name, selector)
    if schema:
        schemaDiff = diff(schema, generatedSchema["configSchema"])
        if schemaDiff:
            print('-'*50)
            print(f'schema diff for {name} in {selector}s')
        # call for individual warnings
            for uiType in uiTypetoSchemaFn.keys():
                testIndividualType(uiConfig, dbConfig, schema, uiType)
            if "allOf" in schema:
                curAllOfSchema = schema["allOf"]
                newAllOfSchema = generateAllOfSchema(uiConfig, dbConfig, "value")
                allOfSchemaDiff = diff(newAllOfSchema, curAllOfSchema)
                if allOfSchemaDiff:
                    warnings.warn("For allOf field Difference is : {}".format(allOfSchemaDiff), UserWarning)
            if "anyOf" in schema:
                curAnyOfSchema = schema["anyOf"]
                newAnyOfSchema = generateAllOfSchema(uiConfig, dbConfig, "value")
                anyOfSchemaDiff = diff(newAnyOfSchema, curAnyOfSchema)
                if anyOfSchemaDiff:
                    warnings.warn("For anyOf field Difference is : {}".format(anyOfSchemaDiff), UserWarning)
            print('-'*50)
    else:
        print('-'*50)
        print(f'Generated Schema for {name} in {selector}s')
        print(json.dumps(generatedSchema,indent=2))
        print('-'*50)

