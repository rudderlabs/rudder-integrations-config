#!/usr/bin/env python3
import requests
import json
import os
import sys
import jsondiff
import argparse
from constants import CONFIG_DIR


def get_command_line_arguments():
    parser = argparse.ArgumentParser(description="Script to deploy config files to DB.")
    parser.add_argument("control_plane_url", nargs="?", help="Control plane URL")
    parser.add_argument("username", nargs="?", help="Control plane admin username")
    parser.add_argument("password", nargs="?", help="Control plane admin password")
    parser.add_argument(
        "item_name", nargs="?", help="Specific item name to update.", default=None
    )

    args = parser.parse_args()

    control_plane_url = args.control_plane_url or os.getenv("CONTROL_PLANE_URL")
    username = args.username or os.getenv("API_USER")
    password = args.password or os.getenv("API_PASSWORD")
    item_name = args.item_name or os.getenv("ITEM_NAME")

    missing_args = []

    if control_plane_url is None:
        missing_args.append(
            "1st positional argument or CONTROL_PLANE_URL environment variable"
        )
    if username is None:
        missing_args.append("2nd positional argument or API_USER environment variable")
    if password is None:
        missing_args.append(
            "3rd positional argument or API_PASSWORD environment variable"
        )

    if missing_args:
        print("Error: Missing the following arguments or environment variables:")
        for arg in missing_args:
            print(arg)
        sys.exit(1)

    return control_plane_url, username, password, item_name


CONTROL_PLANE_URL, USERNAME, PASSWORD, ITEM_NAME = get_command_line_arguments()

# CONSTANTS
HEADER = {"Content-Type": "application/json"}
AUTH = (USERNAME, PASSWORD)
REQUEST_TIMEOUT = 10  # seconds
#########################


#########################
# UTIL METHODS
def parse_response(resp):
    if resp.status_code >= 200 and resp.status_code <= 300:
        return resp.status_code, resp.json()
    else:
        return resp.status_code, str(resp.content)


def get_persisted_store(base_url, selector):
    request_url = f"{base_url}/{selector}-definitions"
    response = requests.get(request_url, timeout=REQUEST_TIMEOUT)
    return json.loads(response.text)


def get_config_definition(base_url, selector, name):
    request_url = f"{base_url}/{selector}-definitions/{name}"
    response = requests.get(request_url, timeout=REQUEST_TIMEOUT)
    return response


def get_file_content(name, selector):
    file_selectors = ["db-config.json", "ui-config.json", "schema.json"]

    directory = f"./{CONFIG_DIR}/{selector}s/{name}"
    available_files = os.listdir(directory)

    file_content = {}

    for file_selector in file_selectors:
        if file_selector in available_files:
            with open(f"{directory}/{file_selector}", "r") as f:
                file_content.update(json.loads(f.read()))

    return file_content


def update_config_definition(selector, name, fileData):
    url = f"{CONTROL_PLANE_URL}/{selector}-definitions/{name}"
    resp = requests.post(
        url=url,
        headers=HEADER,
        data=json.dumps(fileData),
        auth=AUTH,
        timeout=REQUEST_TIMEOUT,
    )
    return parse_response(resp)


def create_config_definition(selector, fileData):
    url = f"{CONTROL_PLANE_URL}/{selector}-definitions/"
    resp = requests.post(
        url=url,
        headers=HEADER,
        data=json.dumps(fileData),
        auth=AUTH,
        timeout=REQUEST_TIMEOUT,
    )
    return parse_response(resp)


def update_config(data_diff, selector):
    results = []
    for diff in data_diff:
        name = diff["name"]
        fileData = get_file_content(name, selector)
        nameInConfig = fileData["name"]

        if diff["action"] == "create":
            url = f"{CONTROL_PLANE_URL}/{selector}-definitions"
        else:
            url = f"{CONTROL_PLANE_URL}/{selector}-definitions/{nameInConfig}"

        resp = requests.post(
            url=url,
            headers=HEADER,
            data=json.dumps(fileData),
            auth=AUTH,
            timeout=REQUEST_TIMEOUT,
        )
        status, response = parse_response(resp)
        diff["update"] = {"status": status, "response": response}
        # results.append(diff)
        results.append(name)

    return json.dumps(results, indent=2)


def update_diff_db(selector, item_name=None):
    final_report = []

    ## data sets
    if item_name:
        current_items = [item_name]
    else:
        current_items = os.listdir(f"./{CONFIG_DIR}/{selector}s")

    print(f"Current items: {current_items}")

    for item in current_items:
        # check if item is a directory
        if not os.path.isdir(f"./{CONFIG_DIR}/{selector}s/{item}"):
            continue

        updated_data = get_file_content(item, selector)
        persisted_data = get_config_definition(
            CONTROL_PLANE_URL, selector, updated_data["name"]
        )

        if persisted_data.status_code == 200:
            diff = jsondiff.diff(
                json.loads(persisted_data.text), updated_data, marshal=True
            )
            # ignore the $delete - values present in DB but missing in files. Anyways this doesn't get reflected in DB as keys are missing in files itself.
            # Best practice is to make sure all keys are maintained in the config files irrespective of them being null.
            del diff["$delete"]

            if len(diff.keys()) > 0:  # changes exist
                # print(diff)
                status, response = update_config_definition(
                    selector, updated_data["name"], updated_data
                )
                final_report.append(
                    {"name": updated_data["name"], "action": "update", "status": status}
                )
            else:
                final_report.append(
                    {"name": updated_data["name"], "action": "N/A", "status": ""}
                )

        else:
            status, response = create_config_definition(selector, updated_data)
            final_report.append(
                {"name": updated_data["name"], "action": "create", "status": status}
            )

    return final_report


def get_formatted_json(data):
    return json.dumps(data, indent=2)


def get_stale_data(selector, report):
    stale_config_report = []
    persisted_data_set = get_persisted_store(CONTROL_PLANE_URL, selector)
    persisted_items = [item["name"] for item in persisted_data_set]
    file_items = [item["name"] for item in report]

    for item in persisted_items:
        if item not in file_items:
            stale_config_report.append(item)

    return stale_config_report


if __name__ == "__main__":

    print("\n")
    print("#" * 50)
    print("Running Destination Definitions Updates")
    dest_final_report = update_diff_db("destination", ITEM_NAME)

    print("\n")
    print("#" * 50)
    print("Destination Definition Update Report")
    print(get_formatted_json(dest_final_report))

    print("\n")
    print("#" * 50)
    print("Stale Destinations Report")
    print(get_formatted_json(get_stale_data("destination", dest_final_report)))

    print("\n")
    print("#" * 50)
    print("Running Source Definitions Updates")
    src_final_report = update_diff_db("source", ITEM_NAME)

    print("\n")
    print("#" * 50)
    print("Source Definition Update Report")
    print(get_formatted_json(src_final_report))

    print("\n")
    print("#" * 50)
    print("Stale Sources Report")
    print(get_formatted_json(get_stale_data("source", src_final_report)))

    print("\n")
    print("#" * 50)
    print("Running Wht Lib Project Definitions Updates")
    wht_final_report = update_diff_db("wht-lib-project", ITEM_NAME)

    print("\n")
    print("#" * 50)
    print("Wht Lib Project Definition Update Report")
    print(get_formatted_json(wht_final_report))

    print("\n")
    print("#" * 50)
    print("Stale Wht Lib Projects Report")
    print(get_formatted_json(get_stale_data("wht-lib-project", wht_final_report)))
