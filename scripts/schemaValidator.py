import json
from schemaGenerator import uiTypetoSchemaType, checkIsOldFormat
from jsondiff import diff
import os

def getDestDirectories(directory):
   allDestList = os.listdir(directory)
   return allDestList

def getUiConfigAndSchema(directory):
   fileContent = {}
   with open(f'{directory}/ui-config.json', 'r') as f:
       fileContent.update(json.loads(f.read()))
   with open(f'{directory}/schema.json', 'r') as f:
       fileContent.update(json.loads(f.read()))
  
   uiConfig = fileContent.get('uiConfig', None)
   schema = fileContent.get('configSchema', None)
   return uiConfig, schema

def testIndividualType(directory, curType):
   allDirList = getDestDirectories(directory)
   for curDirectory in allDirList:
       uiConfig, schema = getUiConfigAndSchema(f'{directory}/{curDirectory}')
       if schema == None:
           print(f"At {curDirectory} : Schema in null")
           continue
       if not checkIsOldFormat(uiConfig):
           print(f"At {curDirectory} : Ui-Config is of new type")
           continue
       for uiConfigItem in uiConfig:
           for field in uiConfigItem["fields"]:
               if field["type"] == curType:
                   if field["value"] not in schema["properties"]:
                       print(f'At {curDirectory} : {field["value"]} field is not in schema')
                   else:
                       curSchemaField = schema["properties"][field["value"]]
                       newSchemaField = uiTypetoSchemaType.get(curType)(field)
                       schemaDiff = diff(newSchemaField,curSchemaField)
                       if schemaDiff:
                           print(f'At {curDirectory} difference is : {schemaDiff}')


if __name__ == '__main__':
    for type in uiTypetoSchemaType.keys():
        print(f"##################   {type}   ###########################")
        print("")
        testIndividualType('../src/configurations/destinations/', type)
        print("")
