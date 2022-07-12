import requests
import json
import os
import sys
import jsondiff

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
USERNAME=sys.argv[2]
print(USERNAME)
PASSWORD=sys.argv[3]
print(PASSWORD)
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

def get_file_content(name, selector):
    file_selectors = ['db_config.json', 'ui_config.json', 'schema.json', 'metadata.json']

    directory = f'./data/{selector}s/{name}'
    available_files = os.listdir(directory)

    file_content = {}

    for file_selector in file_selectors:
        if file_selector in available_files:
            with open (f'{directory}/{file_selector}', 'r') as f:
                file_content.update(json.loads(f.read()))

    return file_content
#########################

def calculate_diff(persisted_data_set, selector):
    final_report = []

    ## data set
    current_items = [item.replace('.json', '') for item in os.listdir(f'./data/{selector}s')]
    persisted_items = [item['name'].lower() for item in persisted_data_set]

    ## check for updates
    for persisted_data in persisted_data_set:
        name = persisted_data["name"].lower()
        if name in current_items:
            updated_data = get_file_content(name, selector)

            diff = jsondiff.diff(persisted_data, updated_data, marshal=True)
            # ignore the id, createdAt, updatedAt keys
            if diff['$delete'] == ['id', 'createdAt', 'updatedAt']:
                del diff['$delete']

            if len(diff.keys()) > 0: # no changes
                final_report.append({"name": name, "diff": diff, "action": "update"})

    ## check for new items
    new_items = [item for item in current_items if item not in persisted_items]
    for item in new_items:
        final_report.append({"name": item, "diff": None, "action": "create"})

    return final_report

def update_config(data_diff, selector):
    results = []
    for diff in data_diff:
        name = diff['name']
        data = get_file_content(name, selector)

        if diff['action'] == 'create':
            url = f'{CONTROL_PLANE_URL}/{selector}-definitions'
        else:
            url = f'{CONTROL_PLANE_URL}/{selector}-definitions/{name.upper()}'

        resp = requests.post(url=url, headers=HEADER, data=json.dumps(data), auth=AUTH)
        status, response = parse_response(resp)
        diff['update'] = {"status": status, "response": response}
        results.append(diff)

    return json.dumps(results, indent=2)

if __name__ == '__main__':
    ##################
    ## DESTINATIONS
    ##################
    # get persisted storage
    destinations = get_persisted_store(CONTROL_PLANE_URL, 'destination')
    # calculate the diff and populate the list for update
    dest_diffs = calculate_diff(destinations, 'destination')
    # make API calls to update
    dest_updates = update_config(dest_diffs, 'destination')
    print(dest_updates)

    ##################
    ## SOURCES
    ##################
    # get persisted storage
    sources = get_persisted_store(CONTROL_PLANE_URL, 'source')
    # calculate the diff and populate the list for update
    source_diffs = calculate_diff(sources, 'source')
    # make API calls to update
    source_updates = update_config(source_diffs, 'source')
    print(source_updates)

