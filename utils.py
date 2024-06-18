import os
import json
import uuid

import requests
import yaml
import subprocess
import platform
import re
from datetime import datetime

class ReportBuilder:
    def __init__(self):
        self.text = ""

    def write(self, text,indent=0,left_padding=0):
        self.text += f'{'\t' * indent}{' ' * left_padding}{text}\n'

    def newline(self):
        self.text += '\n'

    def __str__(self):
        return self.text

def regex_contains(base_string, search_string):
    # Normalize the items by removing special characters,spaces and converting to lowercase
    norm_base = re.sub(r'[^a-zA-Z0-9]', '', base_string).lower()
    norm_search = re.sub(r'[^a-zA-Z0-9]', '', search_string).lower()

    return norm_search in norm_base


def create_directory(dirPath):
    dirPath = dirPath.replace("/", "\\")
    if os.path.isdir(dirPath) is False:
        os.makedirs(dirPath)


# Read json file
def read_json_file(path):
    if path.endswith(".json"):
        return json.loads(read_file(path))
    else:
        raise Exception("Invalid file type, the file being read must be a json file")


# Read a file into memory
def read_file(path):
    if os.path.isfile(path):
        with open(path, 'r') as file:
            return file.read()
    else:
        raise Exception("The provided file does not exist")

# Generate a UUID
def generate_uuid(remove_hyphens=False):
    uid = uuid.uuid4()
    if remove_hyphens:
        uid = str(uid).replace("-", "")
    return uid

def load_json(json_string):
    return json.loads(json_string)

def stringify_yaml(obj):
    # Convert to json first to handle the obj to dict conversion then convert to yaml
    json_str = stringify_json(obj)
    return yaml.dump(json.loads(json_str), default_flow_style=False)

def print_yaml(obj):
    print(stringify_yaml(obj))

# Print json to the console
def print_json(obj,indent=4):
    print(stringify_json(obj, indent=indent))

def stringify_json(obj, indent=4):
    if indent == 0:
        return json.dumps(obj, default=lambda obj: str(obj) if isinstance(obj, datetime) else obj.__dict__)
    else:
        return json.dumps(obj, indent=indent, default=lambda obj: str(obj) if isinstance(obj, datetime) else obj.__dict__)

# Helper function to check if a file exists and if it does make sure that it's not 0 bytes
def valid_file_exists(path):
    rtn_value = True

    if not os.path.isfile(path):
        rtn_value = False
    else:
        if os.path.getsize(path) <= 0:
            rtn_value = False

    return rtn_value


# Write json file
def write_json_file(path, content):
    if path.endswith(".json"):
        write_file(path, stringify_json(content))
    else:
        raise Exception("The filename for this file must end in the json extension")


# Write contents to a file
def write_file(path, content):
    with open(path, 'w') as file:
        file.write(content)


# Write contents to a file
def append_file(path, content):
    with open(path, 'a+') as file:
        file.write(content)

def datetime_now_string(format="%Y-%m-%d %H:%M:%S"):
    return datetime.now().strftime(format)


def open_file(file_path):
    try:
        current_os = platform.system()
        if current_os == 'Windows':
            subprocess.run(['start', file_path], shell=True, check=True)
        elif current_os == 'Darwin':  # macOS
            subprocess.run(['open', file_path], check=True)
        elif current_os == 'Linux':
            subprocess.run(['xdg-open', file_path], check=True)
        else:
            raise ValueError(f"Unsupported OS: {current_os}")
    except Exception as e:
        print(f"Failed to open file: {e}")

# Todo: Need to test this function
def download_file_from_url(url, download_path):
    r = requests.get(url, allow_redirects=True)
    open(download_path, 'wb').write(r.content)

# Todo: Need to test this function
def upload_to_url(url, fields, file):
    # Open a read binary to the file you want to upload to the presigned upload url
    file_stream = {'file': open(file, 'rb')}

    # Submit a post request adding both the fields and file to the post body to the presigned url
    r = requests.post(url, data=fields, files=file_stream)

    # Check to see if the post request returns a status code of 204, if so then return success otherwise return failure
    if r.status_code == 204:
        return True
    else:
        return False

def foramt_bytes(bytes):
    if bytes < 1024:
        return f"{bytes} bytes"
    elif bytes < 1024 * 1024:
        return f"{bytes / 1024:.2f} KB"
    elif bytes < 1024 * 1024 * 1024:
        return f"{bytes / 1024 / 1024:.2f} MB"
    elif bytes < 1024 * 1024 * 1024 * 1024:
        return f"{bytes / 1024 / 1024 / 1024:.2f} GB"
    elif bytes < 1024 * 1024 * 1024 * 1024 * 1024:
        return f"{bytes / 1024 / 1024 / 1024 / 1024:.2f} TB"
    elif bytes < 1024 * 1024 * 1024 * 1024 * 1024 * 1024:
        return f"{bytes / 1024 / 1024 / 1024 / 1024 / 1024:.2f} PB"
    else:
        return f"{bytes} bytes"

