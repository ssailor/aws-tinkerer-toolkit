import os

import requests

import menu_builder
import utils


# Get all bucket names
def list_buckets(session):
    buckets = []
    client = session.client('s3')
    response = client.list_buckets()

    for bucket in response['Buckets']:
        buckets.append(bucket.get('Name'))
    return buckets


def comparitor_s3_bucket(bucket_name, search_text):

    if isinstance(bucket_name, menu_builder.MenuItem):
        bucket_name = bucket_name.display_text

    if search_text == "" or search_text is None:
        return menu_builder.MenuItem(bucket_name, bucket_name)
    elif utils.regex_contains(bucket_name, search_text):
        return menu_builder.MenuItem(bucket_name, bucket_name)
    else:
        return None


# Get files and folders for a specific folder/prefix in a bucket
def list_objects_and_folders(session, bucket_name, prefix=None):
    # Initialize the S3 client
    client = session.client('s3')

    # Create a paginator for the list_objects_v2 operation
    paginator = client.get_paginator('list_objects_v2')

    # Use the paginator to iterate through all pages
    prams = {
        'Bucket': bucket_name,
        'Delimiter': '/',
    }

    # If a prefix is provided, add it to the parameters
    if prefix:
        # Ensure that the prefix ends with a '/'
        if not prefix.endswith('/'):
            prefix += '/'
        prams['Prefix'] = prefix

    # Initialize sets to store unique objects and folders
    files = set()
    folders = set()

    # Iterate through each page of results
    for page in paginator.paginate(**prams):
        if 'Contents' in page:
            for item in page['Contents']:
                if item['Key'][-1] != '/':
                    files.add(item['Key'])
        if 'CommonPrefixes' in page:
            for common_prefix in page['CommonPrefixes']:
                folders.add(common_prefix['Prefix'])

    # Convert the sets to lists and sort them
    files_list = list(files)
    folders_list = list(folders)

    # Sort the lists
    files_list.sort()
    folders_list.sort()

    # Return tuple of objects and folders
    return files_list, folders_list


# Create a presdigned URL for an object in a bucket
# This function creates a S3 presigned download url
def generate_download_presigned_url(session, bucket_name, s3_key, expiration_seconds):
    # Create the s3 client from the provided session
    client = session.client('s3')

    return client.generate_presigned_url(
        ClientMethod='get_object',
        Params={'Bucket': bucket_name, 'Key': s3_key},
        ExpiresIn=expiration_seconds)


def generate_upload_presigned_url(session, bucket_name, s3_key, expiration_seconds=3600):
    # Create the s3 client from the provided session
    client = session.client('s3')

    if s3_key is None:
        s3_key = "/"

    # Generate the presigned URL
    response = client.generate_presigned_post(
        Bucket=bucket_name,
        Key=s3_key,
        ExpiresIn=expiration_seconds
    )

    # Parse out the presigned url (string) and fields (dict) from the response
    url = response.get("url")
    fields = response.get("fields")

    # Return the url and fields as a tuple
    return url, fields


def download_s3_folder(session, bucket_name, s3_key, local_path, recurse=True):
    # Ensure that the local path exists, ensure it's a directory and make sure it ends with a '/'
    if os.path.exists(local_path):
        if os.path.isdir(local_path) and not local_path.endswith("/"):
            local_path += "/"
    else:
        print(f"Directory {local_path} does not exist")
        return None

    # For the provided s3 get all the files and folders
    files, folders = list_objects_and_folders(session, bucket_name, s3_key)

    # Download all the files in the current folder
    for file in files:
        full_path = local_path + file.split('/')[-1]
        print(f"Downloading {full_path}")
        download_file(session, bucket_name, file, full_path)

    # If recurse is true then download all the folders, if a folder does not exist create it
    if recurse:
        for folder in folders:
            new_path = local_path + folder.split('/')[-2] + "/"
            if not os.path.exists(new_path):
                os.mkdir(new_path)
                print(f"Created folder {new_path}")

            # Recurse into the folder to get all of it's folder and files then download them
            download_s3_folder(session, bucket_name, folder, new_path, True)


# Upload an object to a bucket
def upload_file(session, bucket_name, local_file, s3_key):
    # Initialize the S3 client
    client = session.client('s3')

    if s3_key is None:
        s3_key = "/"

    s3_key += local_file.split("/")[-1]

    # Upload the object
    client.upload_file(local_file, bucket_name, s3_key)


# Download an object from a bucket
def download_file(session, bucket_name, s3_key, local_file):
    # Initialize the S3 client
    client = session.client('s3')

    # Download the object
    client.download_file(bucket_name, s3_key, local_file)


def get_file_info(session, bucket_name, s3_key):
    # Initialize the S3 client
    client = session.client('s3')

    # Get the object metadata
    return client.head_object(Bucket=bucket_name, Key=s3_key)


# This function creates a POST curl command using the AWS S3 Upload Presigned URL information for a specified file
def create_curl_upload_command(url, fields, file="<INSERT FILE ABS PATH>"):
    # Create the base curl command
    curl_command = "curl -X POST"

    # Add each field item to the body of the curl command
    for k, v in fields.items():
        curl_command += f" -F \"{k}={v}\""

    # Add the file to the body of the curl command
    curl_command += f" -F \"file=@{file}\""

    # Add the url to the curl command
    curl_command += f" \"{url}\""

    # return the curl command string
    return curl_command


# This function uses python to upload the file to S3
def upload_to_s3(url, fields, file):
    # Open a read binary to the file you want to upload to the presigned upload url
    files = {'file': open(file, 'rb')}

    # Submit a post request adding both the fields and file to the post body to the presigned url
    r = requests.post(url, data=fields, files=files)

    # Check to see if the post request returns a status code of 204, if so then return success otherwise return failure
    if r.status_code == 204:
        return "success"
    else:
        return "upload failed"