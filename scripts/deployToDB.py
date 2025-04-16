#!/usr/bin/env python3
import requests
import json
import os
import sys
import jsondiff
import argparse
from constants import CONFIG_DIR, REQUEST_TIMEOUT, HEADER
from utils import (
    get_config_definition,
    get_file_content,
    update_config_definition,
    create_config_definition,
    parse_response,
)

ALL_SELECTORS = ["destination", "source"]


def get_command_line_arguments():
    parser = argparse.ArgumentParser(description="Script to deploy config files to DB.")
    parser.add_argument("control_plane_url", nargs="?", help="Control plane URL")
    parser.add_argument("username", nargs="?", help="Control plane admin username")
    parser.add_argument("password", nargs="?", help="Control plane admin password")
    parser.add_argument(
        "selector",
        nargs="?",
        help="Specify destination or source",
        default=None,
    )
    parser.add_argument(
        "item_name", nargs="?", help="Specific item name to update.", default=None
    )

    args = parser.parse_args()

    control_plane_url = args.control_plane_url or os.getenv("CONTROL_PLANE_URL")
    username = args.username or os.getenv("API_USER")
    password = args.password or os.getenv("API_PASSWORD")
    selector = args.selector or os.getenv("SELECTOR")
    item_name = args.item_name or os.getenv("ITEM_NAME")

    invalid_args = []

    if control_plane_url is None:
        invalid_args.append(
            "1st positional argument or CONTROL_PLANE_URL environment variable is missing"
        )
    if username is None:
        invalid_args.append(
            "2nd positional argument or API_USER environment variable is missing"
        )
    if password is None:
        invalid_args.append(
            "3rd positional argument or API_PASSWORD environment variable is missing"
        )
    if selector is None:
        SELECTORS = ALL_SELECTORS
    elif selector not in ALL_SELECTORS:
        invalid_args.append(
            "4th positional argument or SELECTOR environment variable is invalid"
        )
    else:
        SELECTORS = [selector]

    if invalid_args:
        print("Error: The following arguments or environment variables are invalid:")
        for arg in invalid_args:
            print(arg)
        sys.exit(1)

    return control_plane_url, username, password, SELECTORS, item_name


CONTROL_PLANE_URL, USERNAME, PASSWORD, SELECTORS, ITEM_NAME = (
    get_command_line_arguments()
)

# CONSTANTS
AUTH = (USERNAME, PASSWORD)
#########################


#########################
# UTIL METHODS


def get_persisted_store(base_url, selector):
    request_url = f"{base_url}/{selector}-definitions"
    response = requests.get(request_url, timeout=REQUEST_TIMEOUT, auth=AUTH)
    return json.loads(response.text)


# not used anywhere it can be removed
def update_config(data_diff, selector):
    results = []
    for diff in data_diff:
        name = diff["name"]
        directory = f"./{CONFIG_DIR}/{selector}s/{name}"
        fileData = get_file_content(directory)
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
        directory = f"./{CONFIG_DIR}/{selector}s/{item}"
        updated_data = get_file_content(directory)
        if (
            updated_data.get("isSkipForProd")
            and CONTROL_PLANE_URL == "https://api.rudderstack.com"
        ):
            final_report.append({"name": updated_data["name"], "status": "skipped"})
            continue
        persisted_data = get_config_definition(
            CONTROL_PLANE_URL, selector, updated_data["name"], AUTH
        )

        if persisted_data.status_code == 200:
            diff = jsondiff.diff(
                json.loads(persisted_data.text), updated_data, marshal=True
            )
            # ignore the $delete - values present in DB but missing in files. Anyways this doesn't get reflected in DB as keys are missing in files itself.
            # Best practice is to make sure all keys are maintained in the config files irrespective of them being null.
            del diff["$delete"]

            if len(diff.keys()) > 0:  # changes exist
                status, response = update_config_definition(
                    CONTROL_PLANE_URL,
                    selector,
                    updated_data["name"],
                    updated_data,
                    AUTH,
                )
                final_report.append(
                    {"name": updated_data["name"], "action": "update", "status": status}
                )
            else:
                final_report.append(
                    {"name": updated_data["name"], "action": "N/A", "status": ""}
                )

        else:
            status, response = create_config_definition(
                CONTROL_PLANE_URL, selector, updated_data, AUTH
            )
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
    for selector in SELECTORS:
        print("\n")
        print("#" * 50)
        print("Running {} Definitions Updates".format(selector.capitalize()))
        final_report = update_diff_db(selector, ITEM_NAME)

        print("\n")
        print("#" * 50)
        print("{} Definition Update Report".format(selector.capitalize()))
        print(get_formatted_json(final_report))

        print("\n")
        print("#" * 50)
        print("Stale {}s Report".format(selector.capitalize()))
        print(get_formatted_json(get_stale_data(selector, final_report)))
