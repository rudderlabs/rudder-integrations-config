import requests
from jsondiff import JsonDiffer
from constants import REQUEST_TIMEOUT, HEADER
import os
import json
import datetime


def is_ci():
    """Detect if running in a CI environment (GitHub Actions sets CI=true, and GITHUB_ACTION is always set)."""
    # See: https://docs.github.com/en/actions/reference/variables-reference#default-environment-variables
    return os.environ.get("CI") == "true" or "GITHUB_ACTION" in os.environ


def generate_curl_command(method, url, headers=None, data=None, auth=None):
    """Generate equivalent curl command for the API request."""
    curl_parts = ["curl"]

    # Add method
    if method.upper() != "GET":
        curl_parts.append(f"-X {method.upper()}")

    # Add headers
    if headers:
        for key, value in headers.items():
            curl_parts.append(f'-H "{key}: {value}"')

    # Add authentication
    if auth:
        if is_ci():
            # Mask both username and password in CI
            curl_parts.append(f'--user "***:***"')
        else:
            curl_parts.append(f'--user "{auth[0]}:{auth[1]}"')

    # Add data for POST/PUT requests
    if data and method.upper() in ["POST", "PUT", "PATCH"]:
        # Properly escape JSON data for curl
        if isinstance(data, str):
            json_data = data
        else:
            json_data = json.dumps(data)
        # Use single quotes to avoid escaping issues
        curl_parts.append(f"--data '{json_data}'")

    # Add URL (last)
    curl_parts.append(f'"{url}"')

    return " \\\n  ".join(curl_parts)


def log_api_request(
    method, url, headers=None, data=None, auth=None, response=None, to_file=False
):
    """Log API request details for debugging purposes."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ci_mode = is_ci()

    log_content = []
    log_content.append(f"\n🔍 API Request Debug [{timestamp}]:")
    log_content.append(f"   Method: {method}")
    log_content.append(f"   URL: {url}")
    if headers:
        log_content.append(f"   Headers: {json.dumps(headers, indent=4)}")
    if auth:
        if ci_mode:
            log_content.append(f"   Auth: ***:*** (masked in CI)")
        else:
            log_content.append(f"   Auth: {auth[0]}:***")
    if data:
        if isinstance(data, str):
            try:
                parsed_data = json.loads(data)
                log_content.append(
                    f"   Request Body: {json.dumps(parsed_data, indent=4)}"
                )
            except json.JSONDecodeError:
                log_content.append(f"   Request Body: {data}")
        else:
            log_content.append(f"   Request Body: {json.dumps(data, indent=4)}")

    # Add curl command
    curl_command = generate_curl_command(method, url, headers, data, auth)
    log_content.append(f"\n   🔧 Equivalent curl command:")
    log_content.append(f"   {curl_command}")

    if response:
        log_content.append(f"\n   Response Status: {response.status_code}")
        log_content.append(f"   Response Headers: {dict(response.headers)}")
        try:
            if response.text:
                log_content.append(
                    f"   Response Body: {json.dumps(response.json(), indent=4)}"
                )
        except (json.JSONDecodeError, ValueError):
            log_content.append(f"   Response Body: {response.text}")
    log_content.append("-" * 50)

    # Write to deploy-debug.log file if requested (skip console output)
    if to_file:
        try:
            with open("deploy-debug.log", "a", encoding="utf-8") as f:
                for line in log_content:
                    f.write(line + "\n")
                f.write("\n")  # Extra newline for readability
        except Exception as e:
            print(f"Warning: Could not write to deploy-debug.log: {e}")
    else:
        # Print to console only if not writing to file
        for line in log_content:
            print(line)


def initialize_debug_log():
    """Initialize or clear the deploy-debug.log file at the start of execution."""
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("deploy-debug.log", "w", encoding="utf-8") as f:
            f.write(f"=== DEBUG LOG STARTED [{timestamp}] ===\n")
            f.write("=" * 60 + "\n\n")
        print("📝 Debug logging enabled - logs will be written to deploy-debug.log")
        return True
    except Exception as e:
        print(f"Warning: Could not initialize deploy-debug.log: {e}")
        return False


def get_json_diff(oldJson, newJson, exclude_paths=None):
    """Returns the difference between two JSONs.

    Args:
        oldJson (object): old json.
        newJson (object): new json.

    Returns:
        object: difference between oldJson and newJson.
    """
    differ = JsonDiffer(marshal=True)
    return differ.diff(oldJson, newJson, exclude_paths=exclude_paths)


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


def get_config_definition(base_url, selector, name="", auth=None, verbose=False):
    request_url = f"{base_url}/{selector}-definitions/{name}".rstrip("/")

    if verbose:
        log_api_request("GET", request_url, auth=auth, to_file=True)

    response = requests.get(
        request_url,
        timeout=REQUEST_TIMEOUT,
        auth=auth,
    )

    if verbose:
        log_api_request("GET", request_url, auth=auth, response=response, to_file=True)

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


def update_config_definition(
    base_url,
    selector,
    name,
    fileData,
    method="POST",
    auth=None,
    dry_run=False,
    verbose=False,
):
    if dry_run:
        if verbose:
            url = f"{base_url}/{selector}-definitions/{name}"
            log_api_request(
                method,
                url,
                headers=HEADER,
                data=json.dumps(fileData),
                auth=auth,
                to_file=True,
            )
        return "DRY RUN - Would update", {
            "message": "Dry run mode - no actual update performed"
        }

    url = f"{base_url}/{selector}-definitions/{name}"

    if verbose:
        log_api_request(
            method,
            url,
            headers=HEADER,
            data=json.dumps(fileData),
            auth=auth,
            to_file=True,
        )

    resp = requests.request(
        method=method,
        url=url,
        headers=HEADER,
        data=json.dumps(fileData),
        auth=auth,
        timeout=REQUEST_TIMEOUT,
    )

    if verbose:
        log_api_request(
            method,
            url,
            headers=HEADER,
            data=json.dumps(fileData),
            auth=auth,
            response=resp,
            to_file=True,
        )

    return parse_response(resp)


def create_config_definition(
    base_url, selector, fileData, auth, dry_run=False, verbose=False
):
    if dry_run:
        if verbose:
            url = f"{base_url}/{selector}-definitions/"
            log_api_request(
                "POST",
                url,
                headers=HEADER,
                data=json.dumps(fileData),
                auth=auth,
                to_file=True,
            )
        return "DRY RUN - Would create", {
            "message": "Dry run mode - no actual creation performed"
        }

    url = f"{base_url}/{selector}-definitions/"

    if verbose:
        log_api_request(
            "POST",
            url,
            headers=HEADER,
            data=json.dumps(fileData),
            auth=auth,
            to_file=True,
        )

    resp = requests.post(
        url=url,
        headers=HEADER,
        data=json.dumps(fileData),
        auth=auth,
        timeout=REQUEST_TIMEOUT,
    )

    if verbose:
        log_api_request(
            "POST",
            url,
            headers=HEADER,
            data=json.dumps(fileData),
            auth=auth,
            response=resp,
            to_file=True,
        )

    return parse_response(resp)
