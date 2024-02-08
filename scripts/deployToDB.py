#!/usr/bin/env python3
import requests
import json
import os
import sys
import jsondiff
from constants import CONFIG_DIR

#########################
# ENV VARIABLES FOT TESTING
# CONTROL_PLANE_URL="https://api.rudderstack.com"
# print(CONTROL_PLANE_URL)
# USERNAME="cbadmin"
# print(USERNAME)
# PASSWORD="testpassword"
# print(PASSWORD)
#########################

#########################
# ENV VARIABLES
CONTROL_PLANE_URL=sys.argv[1]
print(CONTROL_PLANE_URL)
USERNAME=os.environ['API_USER'] #sys.argv[2]
print(USERNAME)
PASSWORD=os.environ['API_PASSWORD'] #sys.argv[3]
#print(PASSWORD)
#########################
# CONSTANTS
HEADER = {"Content-Type": "application/json"}
AUTH = (USERNAME, PASSWORD)
#########################


#########################
# UTIL METHODS
def parse_response(resp):
  if resp.status_code >= 200 and resp.status_code <= 300:
    return resp.status_code, resp.json()
  else:
    return resp.status_code, str(resp.content)

def get_persisted_store(base_url, selector):
    request_url = f'{base_url}/{selector}-definitions'
    response = requests.get(request_url)
    return json.loads(response.text)

def get_config_definition(base_url, selector, name):
    request_url = f'{base_url}/{selector}-definitions/{name}'
    response = requests.get(request_url)
    return response

def get_file_content(name, selector):
    file_selectors = ['db-config.json', 'ui-config.json', 'schema.json']

    directory = f'./{CONFIG_DIR}/{selector}s/{name}'
    available_files = os.listdir(directory)

    file_content = {}

    for file_selector in file_selectors:
        if file_selector in available_files:
            with open (f'{directory}/{file_selector}', 'r') as f:
                file_content.update(json.loads(f.read()))

    return file_content

def update_config_definition(selector, name, fileData):
    url = f'{CONTROL_PLANE_URL}/{selector}-definitions/{name}'
    resp = requests.post(url=url, headers=HEADER, data=json.dumps(fileData), auth=AUTH)
    return parse_response(resp)

def create_config_definition(selector, fileData):
    url = f'{CONTROL_PLANE_URL}/{selector}-definitions/'
    resp = requests.post(url=url, headers=HEADER, data=json.dumps(fileData), auth=AUTH)
    return parse_response(resp)

def update_config(data_diff, selector):
    results = []
    for diff in data_diff:
        name = diff['name']
        fileData = get_file_content(name, selector)
        nameInConfig = fileData["name"]

        if diff['action'] == 'create':
            url = f'{CONTROL_PLANE_URL}/{selector}-definitions'
        else:
            url = f'{CONTROL_PLANE_URL}/{selector}-definitions/{nameInConfig}'

        resp = requests.post(url=url, headers=HEADER, data=json.dumps(fileData), auth=AUTH)
        status, response = parse_response(resp)
        diff['update'] = {"status": status, "response": response}
        # results.append(diff)
        results.append(name)


    return json.dumps(results, indent=2)

def update_diff_db(selector):
    final_report = []

    ## data sets
    current_items = os.listdir(f'./{CONFIG_DIR}/{selector}s')

    for item in current_items:
        # check if item is a directory
        if not os.path.isdir(f'./{CONFIG_DIR}/{selector}s/{item}'):
            continue

        updated_data = get_file_content(item, selector)
        persisted_data = get_config_definition(CONTROL_PLANE_URL, selector, updated_data["name"])

        if persisted_data.status_code == 200:
            diff = jsondiff.diff(json.loads(persisted_data.text), updated_data, marshal=True)
            # ignore the $delete - values present in DB but missing in files. Anyways this doesn't get reflected in DB as keys are missing in files itself.
            # Best practice is to make sure all keys are maintained in the config files irrespective of them being null.
            del diff['$delete']

            if len(diff.keys()) > 0: # changes exist
                #print(diff)
                status, response = update_config_definition(selector, updated_data["name"], updated_data)
                final_report.append({"name": updated_data["name"], "action":"update", "status": status})
            else:
                final_report.append({"name": updated_data["name"], "action":"na", "status": ""})

        else:
            status, response = create_config_definition(selector, updated_data)
            final_report.append({"name": updated_data["name"], "action":"create", "status": status})

    return final_report

def get_stale_data(selector, report):
    stale_config_report = []
    persisted_data_set = get_persisted_store(CONTROL_PLANE_URL, selector)
    persisted_items = [item['name'] for item in persisted_data_set]
    file_items = [item['name'] for item in report]

    for item in persisted_items:
        if item not in file_items:
           stale_config_report.append({item})

    return stale_config_report

if __name__ == '__main__':
    print("Running Destination Definitions Updates")
    dest_final_report = update_diff_db('destination')
    print("Destination Definition Update Report")
    print(dest_final_report)
    print("Destination Stale Config Report")
    print(get_stale_data('destination', dest_final_report))

    print("Running Source Definitions Updates")
    src_final_report = update_diff_db('source')
    print("Source Definition Update Report")
    print(src_final_report)
    print("Source Stale Config Report")
    print(get_stale_data('source', src_final_report))

    print("Running Wht Lib Projects Definitions Updates")
    wht_final_report = update_diff_db('wht-lib-project')
    print("Wht lib project Definition Update Report")
    print(wht_final_report)
    print("Wht lib project Stale Config Report")
    print(get_stale_data('wht-lib-project', wht_final_report))
    