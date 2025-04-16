import requests
from jsondiff import JsonDiffer
from constants import REQUEST_TIMEOUT, HEADER
import os
import json


def get_json_diff(oldJson, newJson):
    """Returns the difference between two JSONs.

    Args:
        oldJson (object): old json.
        newJson (object): new json.

    Returns:
        object: difference between oldJson and newJson.
    """
    differ = JsonDiffer(marshal=True)
    return differ.diff(oldJson, newJson)


def apply_json_diff(oldJson, diff):
    """Applies the difference on oldJson and returns the newJson.

    Args:
        oldJson (object): old json.
        diff (object): difference between oldJson and newJson.

    Returns:
        object: new json.
    """
    differ = JsonDiffer(marshal=True)
    return differ.patch(oldJson, diff)


def get_formatted_json(jsonObj):
    """Formats the json object.

    Args:
        jsonObj (object): json object.

    Returns:
        string: formatted json.
    """
    return json.dumps(jsonObj, indent=2, ensure_ascii=False)


def get_json_from_file(filePath):
    """Reads the content of the file and returns the json object.

    Args:
        filePath (string): file path.

    Returns:
        object: json object.
    """
    with open(filePath, "r") as file:
        return json.loads(file.read().encode("utf-8", "ignore"))


def is_old_format(uiConfig):
    if isinstance(uiConfig, dict):
        return False
    return True

def parse_response(resp):
    if resp.status_code >= 200 and resp.status_code <= 300:
        return resp.status_code, resp.json()
    else:
        return resp.status_code, str(resp.content)

def get_config_definition(base_url, selector, name="", auth=None):
    request_url = f"{base_url}/{selector}-definitions/{name}"
    if selector == "accounts":
        request_url = f"{base_url}/account-definitions"
    response = requests.get(
        request_url,
        timeout=REQUEST_TIMEOUT,
        auth=auth,
    )
    return response


def get_file_content(directory):
    file_selectors = ["db-config.json", "ui-config.json", "schema.json"]

    available_files = os.listdir(directory)

    file_content = {}

    for file_selector in file_selectors:
        if file_selector in available_files:
            with open(f"{directory}/{file_selector}", "r") as f:
                file_content.update(json.loads(f.read()))

    return file_content


def update_config_definition(base_url, selector, name, fileData, auth=None):
    url = f"{base_url}/{selector}-definitions/{name}"
    method = "POST"
    if selector == "accounts":
        url = f"{base_url}/account-definitions/{name}"
        method = "PUT"
    resp = requests.request(
        method=method,
        url=url,
        headers=HEADER,
        data=json.dumps(fileData),
        auth=auth,
        timeout=REQUEST_TIMEOUT,
    )
    return parse_response(resp)


def create_config_definition(base_url, selector, fileData, auth):
    if selector == "accounts":
        selector = "account"
    url = f"{base_url}/{selector}-definitions/"
    resp = requests.post(
        url=url,
        headers=HEADER,
        data=json.dumps(fileData),
        auth=auth,
        timeout=REQUEST_TIMEOUT,
    )
    return parse_response(resp)
