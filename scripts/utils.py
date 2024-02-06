from jsondiff import JsonDiffer
import json

from constants import TEST_INTEGRATION_NAME_PREFIX, TEST_INTEGRATION_NAME_SUFFIX

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
    with open(filePath, 'r') as file:
        return json.loads(file.read().encode('utf-8', 'ignore'))
    
def is_test_integration(name):
    return name.startswith(TEST_INTEGRATION_NAME_PREFIX) and name.endswith(TEST_INTEGRATION_NAME_SUFFIX)
