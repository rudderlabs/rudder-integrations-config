import requests
import json
import os
import sys

#########################
# ENV VARIABLES
CONTROL_PLANE_URL=sys.argv[1]
print(CONTROL_PLANE_URL)
USERNAME=sys.argv[2]
print(USERNAME)
PASSWORD=sys.argv[3]
print(PASSWORD)
#########################

def get_persisted_store(base_url, selector):
    request_url = f'{base_url}/{selector}-definitions'
    response = requests.get(request_url)
    return json.loads(response.text)

def calculate_diff(persisted_data, selector):
    for data in persisted_data:
        name = data["name"].lower()

        updated_file_path = f'./{selector}s/{name}.json'
        f = open(updated_file_path, 'r')
        updated_config = json.loads(f.read())
        f.close()

        print(json.dumps(data))
        print(json.dumps(updated_config))

        print("---------------")

        break
    pass

def update_config(data_diff, selector):
    return "WIP"

def prepare_data(persisted_data_set, selector):
    ignored_keys = ['id', 'createdAt', 'updatedAt']
    for persisted_data in persisted_data_set:
        name = persisted_data['name'].lower()
        updated_file_path = f'./{selector}s/{name}.json'
        f = open(updated_file_path, 'r')
        current_data = json.loads(f.read())
        f.close()

        p_key_set = list(persisted_data.keys())
        c_key_set = list(current_data.keys())

        final_key_set = p_key_set + c_key_set
        final_object = {}

        for key in final_key_set:
            if key not in ignored_keys:
                if key in p_key_set and key not in c_key_set:
                    final_object[key] = persisted_data[key]
                else:
                    final_object[key] = current_data[key]

        print (final_object)

        f = open(updated_file_path, 'w')
        f.write(json.dumps(final_object, indent=2))
        f.close()

if __name__ == '__main__':
    ##################
    ## DESTINATIONS
    ##################
    # get persisted storage
    destinations = get_persisted_store(CONTROL_PLANE_URL, 'destination')
    ## ONE TIME
    prepare_data(destinations, 'destination')
    ##
    # # calculate the diff and populate the list for update
    # dest_diffs = calculate_diff(destinations, 'destination')
    # # make API calls to update
    # dest_updates = update_config(dest_diffs, 'destination')
    # print(dest_updates)

    ##################
    ## SOURCES
    ##################
    # get persisted storage
    sources = get_persisted_store(CONTROL_PLANE_URL, 'source')
    ## ONE TIME
    prepare_data(sources, 'source')
    ##
    # # calculate the diff and populate the list for update
    # source_diffs = calculate_diff(sources, 'source')
    # # make API calls to update
    # source_updates = update_config(source_diffs, 'source')
    # print(source_updates)




