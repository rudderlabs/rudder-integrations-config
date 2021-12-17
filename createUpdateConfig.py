import json
import requests
import sys
import os
import jsonschema
import time

# cd src/scripts
# run with - python3 createUpdateConfig.py <user> <password> create source all - to create all source-definition
# run with - python3 createUpdateConfig.py <user> <password> update source all - to update all source-definition
# run with - python3 createUpdateConfig.py <user> <password> create destination all - to create all destination-definition
# run with - python3 createUpdateConfig.py <user> <password> update destination all - to update all destination-definition

# run with - python3 createUpdateConfig.py <user> <password> create source <sourcename> - to create single source-definition
# run with - python3 createUpdateConfig.py <user> <password> update source <sourcename> - to update single source-definition
# run with - python3 createUpdateConfig.py <user> <password> create destination <destinationname> - to create single destination-definition
# run with - python3 createUpdateConfig.py <user> <password> update destination <destinationname> - to update single destination-definition

# example: python3 createUpdateConfig.py <user> <password> create source iOS
# example: python3 createUpdateConfig.py <user> <password> update source iOS
# example: python3 createUpdateConfig.py <user> <password> create destination KAFKA
# example: python3 createUpdateConfig.py <user> <password> update destination KAFKA
# prod https://api.rudderstack.com
# staging https://sources-api.dev.rudderlabs.com
# dev https://api.dev.rudderlabs.com

BASE_URL = "http://localhost:5050"
  
USER_NAME = sys.argv[1]
PASSWORD = sys.argv[2]
TASK = sys.argv[3]
TYPE = sys.argv[4]
NAMES = sys.argv[5:]

INDEX = 0
COUNT = 0
failed_configs = []

def parse_response(resp, name):
  if resp.status_code >= 200 and resp.status_code <= 300:
    return resp.json()
  else:
    failed_configs.append(name)
    return resp.content

def getConfigSchema(file):
    schemaFile = f'schemaList/destinations/{file}'
    if os.path.exists(schemaFile):
        try:
            fs = open(schemaFile,)
            content = json.load(fs)
            fs.close()
            return content
        except Exception as e:
            raise Exception(f"Error occurred while getting schema for {file} with error: {e}")
    return None

## TODO: Need to validateSchema using ajv
def validateSchema(schema):
    try:
        jsonschema.Draft7Validator.check_schema(schema)
    except jsonschema.exceptions.SchemaError as err:
        return False
    return True

def createUpdateDestination(file, task):
  try:
    f = open(f'destinationConfigs/{file}',)
    data = json.load(f)
    f.close()
    display_name = data["displayName"]
    name = data["name"]
    configSchema = getConfigSchema(file)

    if configSchema is not None:
        if validateSchema(configSchema) is not True:
           raise Exception(f"Invalid config schema for {file}")
        data["configSchema"] = configSchema

    if task == "create":
      print(f'Creating destination "{display_name}" ({INDEX + 1}/{COUNT})')
      resp = requests.post(url=f'{BASE_URL}/destination-definitions', headers={"Content-Type": "application/json"}, data=json.dumps(data), auth=(USER_NAME, PASSWORD))
      print(parse_response(resp, name))
      print()
    elif task == "update":
      print(f'Updating destination "{display_name}" ({INDEX + 1}/{COUNT})')
      resp = requests.post(url=f'{BASE_URL}/destination-definitions/{name}', headers={"Content-Type": "application/json"}, data=json.dumps(data), auth=(USER_NAME, PASSWORD))
      print(parse_response(resp, name))
      print()
    
  except Exception as e:
    print(e)

def createUpdateSource(file, task):
  try:
    f = open(f'sourceConfigs/{file}',)
    data = json.load(f)
    f.close()
    display_name = data["displayName"]
    name = data["name"]

    if task == "create":
      print(f'Creating source "{display_name}" ({INDEX + 1}/{COUNT})')
      resp = requests.post(url=f'{BASE_URL}/source-definitions', headers={"Content-Type": "application/json"}, data=json.dumps(data), auth=(USER_NAME, PASSWORD))
      print(parse_response(resp, name))
      print()
    
    elif task == "update":
      print(f'Updating source "{display_name}" ({INDEX + 1}/{COUNT})')
      resp = requests.post(url=f'{BASE_URL}/source-definitions/{name}', headers={"Content-Type": "application/json"}, data=json.dumps(data), auth=(USER_NAME, PASSWORD))
      print(parse_response(resp, name))
      print()

  except Exception as e:
    print(e)


def main():
  if TASK != "create" and TASK != "update":
    print("Please specify correct task - create or update")
    return
  if TYPE != "destination" and TYPE != "source":
    print("Please specify correct type - source or destination")
    return
  if len(NAMES) == 0:
    print("Please specify correct source/destination name(s) to create or update - specific source/destination name(s) or \"all\" for bulk creation/updation")
    return
  
  global COUNT
  global INDEX

  if TYPE == "destination":
    if "all" in NAMES:
      filenames = os.listdir('destinationConfigs')
      COUNT = len(filenames)
      for INDEX, file in enumerate(filenames):
        createUpdateDestination(file, TASK)
    else:
      COUNT = len(NAMES)
      for INDEX, name in enumerate(NAMES):
        createUpdateDestination(f'{name}.json', TASK)

  elif TYPE == "source":
    if "all" in NAMES:
      filenames = os.listdir('sourceConfigs')
      COUNT = len(filenames)
      for INDEX, file in enumerate(filenames):
        createUpdateSource(file, TASK)
    else:
      COUNT = len(NAMES)
      for INDEX, name in enumerate(NAMES):
        createUpdateSource(f'{name}.json', TASK)
  
  if len(failed_configs) > 0:
    print(f"Failed configs: {len(failed_configs)}/{COUNT}")
    print("Retry using the following command: ")
    print(f"python3 createUpdateConfig.py {USER_NAME} {PASSWORD} {TASK} {TYPE} ", end="", flush=True)
    for name in failed_configs:
      print(f'"{name}" ', end="", flush=True)
    print()
  print("Done!")


if __name__ == '__main__':
  main()
