import aws_utils
import menu_builder
import utils
from botocore.exceptions import ClientError
import json

class IAMUser:
    def __init__(self):
        self.AccountID = None
        self.UserName = None
        self.ARN = None
        self.UserID = None
        self.CreationDate = None
        self.PasswordLastUsed = None
        self.MFAEnabled = None
        self.AccessKeys = []
        self.IAMGroups = []
        self.Tags = None


class IAMUserAccessKey:
    def __init__(self):
        self.AccessKeyID = None
        self.SecretAccessKey = None
        self.Status = None
        self.CreationDate = None
        self.KeyDescription = None
        self.AccessKeyLastUsed = None
        self.LastUsedDate = None
        self.LastUsedRegion = None
        self.LastUsedServiceName = None

class IAMKeyLastUsed:
    def __init__(self):
        self.LastUsedDate = None
        self.Region = None
        self.ServiceName = None

class Tag:
    def __init__(self):
        self.key = None
        self.value = None

class IAMGroup:
    def __init__(self):
        self.Path = None
        self.GroupName = None
        self.GroupID = None
        self.ARN = None
        self.CreateDate = None

def get_iam_user_details(session, username):

    client = session.client('iam')
    response = client.get_user(UserName=username)

    # Loop through each user in the response and collect the values
    user = response.get("User")

    temp_user = IAMUser()
    temp_user.AccountID = user.get("Arn").split(":")[4]
    temp_user.UserName = user.get("UserName")
    temp_user.ARN = user.get("Arn")
    temp_user.UserID = user.get("UserId")
    temp_user.CreationDate = user.get("CreateDate")
    temp_user.PasswordLastUsed = user.get("PasswordLastUsed")
    temp_user.MFAEnabled = mfa_enabled_for_user(session, temp_user.UserName)
    temp_user.AccessKeys = get_access_keys_for_user(session, temp_user.UserName)
    temp_user.IAMGroups = get_user_groups(session, temp_user.UserName)
    temp_user.Tags = get_user_tags(session, temp_user.UserName, tags=[])

    # If the user has tags then loop through the access keys and add the tag to the key description
    if len(temp_user.AccessKeys) > 0:
        for key in temp_user.AccessKeys:
            if temp_user.Tags is not None:
                for tag in temp_user.Tags:
                    if tag.key == key.AccessKeyID:
                        key.KeyDescription = tag.value

    # Return the user object
    return temp_user

def format_user_details(user):
    r = utils.ReportBuilder()
    r.write("Account ID: " + user.AccountID)
    r.write("User Name: " + user.UserName)
    r.write("ARN: " + user.ARN)
    r.write("User ID: " + user.UserID)
    r.write("Creation Date: " + str(user.CreationDate))
    r.write("Password Last Used: " + str(user.PasswordLastUsed))
    r.write("MFA Enabled: " + str(user.MFAEnabled))

    if len(user.AccessKeys) == 0:
        r.write("Access Keys: None")
    else:
        r.write("Access Keys: ")
        for key in user.AccessKeys:
            r.write("* " + key.AccessKeyID, 0,2)
            r.write("Status: " + key.Status, 0,4)
            r.write("Creation Date: " + str(key.CreationDate), 0,4)
            r.write("Key Description: " + str(key.KeyDescription), 0,4)
            r.write("Last Used Date: " + str(key.LastUsedDate), 0,4)
            r.write("Last Used Region: " + key.LastUsedRegion, 0,4)
            r.write("Last Used Service Name: " + key.LastUsedServiceName, 0,4)

    if len(user.AccessKeys) == 0:
        r.write("IAM Groups: None")
    else:
        r.write("IAM Groups: ")
        for group in user.IAMGroups:
            r.write("* " + group.GroupName, 0, 2)

    if user.Tags is None or len(user.Tags) == 0:
        r.write("Tags: None")
    else:
        r.write("Tags: ")
        for tag in user.Tags:
            r.write(f"* {tag.key}: {tag.value}", 0,2)

    return str(r)

def format_user_view(user):
    r = utils.ReportBuilder()
    r.write(f"User Name: {user.UserName}")
    r.write(f"Password Last Used: {str(user.PasswordLastUsed)}")
    r.write(f"MFA Enabled: {str(user.MFAEnabled)}")

    if len(user.AccessKeys) == 0:
        r.write("Access Keys: None")
    else:
        r.write("Access Keys: ")
        for key in user.AccessKeys:
            if key.KeyDescription is not None:
                r.write(f"* {key.AccessKeyID} ({key.KeyDescription}) - {key.Status}", 0,2)
            else:
                r.write(f"* {key.AccessKeyID} - {key.Status}", 0,2)

    if user.Tags is None or len(user.Tags) == 0:
        r.write("Tags: None")
    else:
        tag_counter = 0
        r.write("Tags: ")
        for tag in user.Tags:
            r.write(f"* {tag.key}: {tag.value}", 0,2)
            tag_counter += 1
            if len(user.Tags) > 10 and tag_counter == 10:
                r.write(f"...", 0,2)
                break

    return str(r)

def comparitor_iam_users(user, search_text):
    if search_text == "" or search_text is None:
        return menu_builder.MenuItem(user.UserName, user.UserID)
    elif utils.regex_contains(user.UserName, search_text):
        return menu_builder.MenuItem(user.UserName, user.UserID)
    else:
        return None

# Function to retrieve the users tags
def get_user_tags(session, username, tags=[], marker=None):
    # Create the list of parameters to be passed into the boto call
    params = {"UserName": username}

    # If a marker is provided then add it to the list of params to pass into the boto call
    if marker:
        params.update({"Marker": marker})

    # Create the boto client and execute the list_user_tags function with the list of parameters
    client = session.client('iam')
    response = client.list_user_tags(**params)

    # Get the marker from the response
    marker = response.get("Marker")

    # Loop though all the tags and search for the specified tag, if found return it
    for tag in response.get("Tags"):
        t = Tag()
        t.key = tag.get('Key')
        t. value = tag.get('Value')
        tags.append(t)

    # If marker has a value then recursively call this function to move to the next set of records, otherwise return null
    if marker:
        get_user_tags(session, username, tags, marker)

    return tags

def get_iam_users(session,get_details=False):
    users = []
    marker = None

    client = session.client('iam')

    while True:

        # If there is a token to continue getting records use it, otherwise retrieve the first set of records
        if marker:
            response = client.list_users(Marker=marker)
        else:
            response = client.list_users()

        # Loop through each user in the response and collect the values
        for user in response.get("Users"):
            temp_user = IAMUser()
            temp_user.AccountID = user.get("Arn").split(":")[4]
            temp_user.UserName = user.get("UserName")
            temp_user.ARN = user.get("Arn")
            temp_user.UserID = user.get("UserId")
            temp_user.CreationDate = user.get("CreateDate")
            temp_user.PasswordLastUsed = user.get("PasswordLastUsed")

            if get_details:
                temp_user.MFAEnabled = mfa_enabled_for_user(session, temp_user.UserName)
                temp_user.AccessKeys = get_access_keys_for_user(session, temp_user.UserName)
                temp_user.IAMGroups = get_user_groups(session, temp_user.UserName)
                temp_user.Tags = get_user_tags(session, temp_user.UserName, tags=[])

                # If the user has tags then loop through the access keys and add the tag to the key description
                if len(temp_user.AccessKeys) > 0:
                    for key in temp_user.AccessKeys:
                        if temp_user.Tags is not None:
                            for tag in temp_user.Tags:
                                if tag.key == key.AccessKeyID:
                                    key.KeyDescription = tag.value

            # Add the user to the list
            users.append(temp_user)

        # Check if the response contains a next token, if it does then use it to get the next page of results,
        # if not exit the infinite loop
        if response.get("Marker"):
            marker = response.get("Marker")
        else:
            break

    # Return the list of users
    return users

# Check if the user has MFA enabled
def mfa_enabled_for_user(session, username):
    # Set mfa enabled flag to false by default
    mfa_enabled = False

    # Create the boto client and execute the list_mfa_devices command for the specified user
    client = session.client('iam')
    response = client.list_mfa_devices(UserName=username)

    # Check to see if there is an MFA device associated to the user
    if len(response.get("MFADevices")) > 0:
        mfa_enabled = True

    return mfa_enabled


# Function to get the access keys for the specified user
def get_access_keys_for_user(session, username):
    # Initialize an array to collect the access keys for the specified user
    access_keys = []

    # Create the boto client and execute the list_access_keys function for the provided user
    client = session.client('iam')
    response = client.list_access_keys(UserName=username)

    # Check if there is an AccessKeyMetadata section in the response
    if response.get("AccessKeyMetadata") is not None:
        # Loop though the keys in the response and parse them into their model objects
        for key in response.get("AccessKeyMetadata"):
            temp_key = IAMUserAccessKey()
            temp_key.AccessKeyID = key.get("AccessKeyId")
            temp_key.SecretAccessKey = key.get("SecretAccessKey")
            temp_key.Status = key.get("Status")
            temp_key.CreationDate = key.get("CreateDate")

            key_last_used = client.get_access_key_last_used(AccessKeyId=temp_key.AccessKeyID)
            if key_last_used.get("AccessKeyLastUsed") is not None:
                temp_key.LastUsedDate = key_last_used.get("AccessKeyLastUsed").get("LastUsedDate")
                temp_key.LastUsedRegion = key_last_used.get("AccessKeyLastUsed").get("Region")
                temp_key.LastUsedServiceName = key_last_used.get("AccessKeyLastUsed").get("ServiceName")

            # Add the AccessKey object to the list
            access_keys.append(temp_key)

    # Return the access keys for the specified user
    return access_keys


def update_access_key(session, username, access_key_id, set_status_inactive):
    # Create the list of parameters to be passed into the boto call
    params = {"UserName": username, "AccessKeyId": access_key_id}

    # Check if the status should be set to inactive, if true set the status to inactive and add it to the parameters dictionary
    if set_status_inactive:
        params.update({"Status": 'Inactive'})

    # Create the client and execute the list_users command with the created parameters
    client = session.client('iam')
    client.update_access_key(**params)


# Function to delete a specified users access key
def delete_access_key(session, username, access_key_id):
    # Create the list of parameters to be passed into the boto call
    params = {"UserName": username, "AccessKeyId": access_key_id}

    # Create the client and execute the delete_access_key command with the created parameters
    client = session.client('iam')
    client.delete_access_key(**params)


# Function to create a new access key for a specified user
def create_access_key(session, username):
    # Create the list of parameters to be passed into the boto call
    params = {"UserName": username}

    # Create the client and execute the delete_access_key command with the created parameters
    client = session.client('iam')
    response = client.create_access_key(**params)

    # Pull out the AccessKey section of the response
    access_key_info = response.get("AccessKey")

    # Parse access key information into object
    access_key = IAMUserAccessKey()
    access_key.AccessKeyID = access_key_info.get("AccessKeyId")
    access_key.SecretAccessKey = access_key_info.get("SecretAccessKey")
    access_key.Status = access_key_info.get("Status")
    access_key.CreationDate = access_key_info.get("CreateDate")

    # Return the access key information
    return access_key

def format_users_report(session,users):
    r = utils.ReportBuilder()
    header_name = "AWS Security Group Report"
    header = menu_builder.build_header(header_name, 20)
    divider = menu_builder.build_divider(header_name, padding=20)
    r.write(header)
    r.write("Account ID: " + aws_utils.get_current_account_id(session))
    r.newline()
    r.write("Results")
    r.write(divider)
    r.newline()

    for user in users:
        r.write(f"* " + user.UserName)
        r.write(f"- User ID: {user.UserID}", 1)
        r.write(f"- ARN: {user.ARN}",1)
        r.write(f"- Creation Date: {str(user.CreationDate)}",1)
        r.write(f"- Password Last Used: {str(user.PasswordLastUsed)}",1)
        r.write(f"- MFA Enabled: {str(user.MFAEnabled)}",1)
        if len(user.AccessKeys) == 0:
            r.write(f"- Access Keys: None",1)
        else:
            r.write(f"* Access Keys: ", 1)
            for key in user.AccessKeys:
                r.write(f"* {key.AccessKeyID}",2)
                r.write(f"- Status:{key.Status}",3)
                r.write(f"- Creation Date:{str(key.CreationDate)}",3)
                r.write(f"- Key Description:{key.KeyDescription}",3)
                r.write(f"- Last Used Date:{key.LastUsedDate}",3)
                r.write(f"- Last Used Region:{key.LastUsedRegion}",3)
                r.write(f"- Last Used Service Name:{key.LastUsedServiceName}",3)
        if len(user.IAMGroups) == 0:
            r.write(f"- IAM Groups: None",1)
        else:
            r.write(f"* IAM Groups: ", 1)
            for group in user.IAMGroups:
                r.write(f"* {group.GroupName}",2)
                r.write(f"- Path:{group.Path}",3)
                r.write(f"- Path:{group.GroupID}", 3)
                r.write(f"- Path:{group.ARN}", 3)
                r.write(f"- Path:{str(group.CreateDate)}", 3)

        if len(user.Tags) == 0:
            r.write("- Tags: None",1)
        else:
            r.write("* Tags: ", 1)
            for tag in user.Tags:
                r.write(f"- {tag.key}: {tag.value}",2)

        r.newline()

    return str(r)

def rotate_access_keys(session, username):

    # 1. Get the user details
    user = get_iam_user_details(session, username)

    # 2. Get the access keys for the user
    access_keys = user.AccessKeys

    # 3. Check to see if the user has any access keys -- if not then create a new access key
    if len(access_keys) == 0:
        iam_access_key = create_access_key(session, username)

        # Tag the new key with a description
        tag_user(session, username, iam_access_key.AccessKeyID, f"Key Rotation By Tinkerer Toolkit: {utils.datetime_now_string()}")

    # 4. If there is only 1 then create a new key and inactivate the old key
    elif len(access_keys) == 1:
        # Get the old access key id
        old_access_key_id = access_keys[0].AccessKeyID
        # create a new access key
        iam_access_key = create_access_key(session, username)

        # build a new session with the new access key and test that it works
        temp_keys = aws_utils.AwsCredentials(iam_access_key.AccessKeyID, iam_access_key.SecretAccessKey)
        test_session = aws_utils.create_aws_session(aws_credentials=temp_keys)

        if test_session is None:
            raise Exception("Unable to create a new session with the new access key")

        # Tag the new key with a description
        tag_user(session, username, iam_access_key.AccessKeyID, f"Key Rotation By Tinkerer Toolkit: {utils.datetime_now_string()}")

        # inactivate the old access key
        update_access_key(session, username, old_access_key_id, True)


    # 5. If the user has access keys then check if they are both active -- if not then throw an error
    elif len(access_keys) == 2:
        key_1 = access_keys[0]
        key_2 = access_keys[1]

        if key_1.CreationDate < key_2.CreationDate:
            old_access_key_id = key_1.AccessKeyID
            latest_existing_access_key = key_2.AccessKeyID
        else:
            old_access_key_id = key_2.AccessKeyID
            latest_existing_access_key = key_1.AccessKeyID

        # Delete the old access key
        delete_access_key(session, username, old_access_key_id)

        # Delete the old access key tag
        delete_user_tag(session, username, old_access_key_id)

        # create a new access key
        iam_access_key = create_access_key(session, username)

        # build a new session with the new access key and test that it works
        temp_keys = aws_utils.AwsCredentials(iam_access_key.AccessKeyID, iam_access_key.SecretAccessKey)
        test_session = aws_utils.create_aws_session(aws_credentials=temp_keys)

        if test_session is None:
            raise Exception("Unable to create a new session with the new access key")

        # Tag the new key with a description
        tag_user(session, username, iam_access_key.AccessKeyID, f"Key Rotation By Tinkerer Toolkit: {utils.datetime_now_string()}")

        # inactivate the old access key
        update_access_key(session, username, latest_existing_access_key, True)
        tag_user(session, username, iam_access_key.AccessKeyID,
                 f"Key Rotation By Tinkerer Toolkit: {utils.datetime_now_string()}")

    else:
        raise Exception("The user has more than 2 access keys, this is not supported")

    # 7. Write the new key info to a json file
    iam_key_filename = f"{utils.datetime_now_string("%Y-%m-%dT%H-%M-%S")}--{str(user.AccountID)}--{user.UserName}--AccessKeyInfo.json"
    utils.write_json_file(iam_key_filename, iam_access_key)

    return

def tag_user(session, username, key, value):
    # Create the client and execute the tag_user command with the created parameters
    client = session.client('iam')
    client.tag_user(UserName=username, Tags=[{"Key": key, "Value": value}])

def delete_user_tag(session, username, key):
    # Create the client and execute the tag_user command with the created parameters
    client = session.client('iam')
    client.untag_user(UserName=username, TagKeys=[key])

def list_iam_groups(session):
    client = session.client('iam')
    response = client.list_groups()

    groups = []
    for group in response.get("Groups"):
        groups.append(group.get("GroupName"))

    return groups

def add_user_to_group(session, username, group_name):
    client = session.client('iam')
    client.add_user_to_group(UserName=username, GroupName=group_name)


def ensure_quarantine_group(session):
    client = session.client('iam')

    group_name = 'quarantine'
    managed_policy_arn = 'arn:aws:iam::aws:policy/AWSDenyAll'

    # Check if the group exists
    try:
        client.get_group(GroupName=group_name)
        return  # Exit the function if the group already exists
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':
            # Group does not exist, so create it
            print(f"Creating {group_name} group...")
            client.create_group(GroupName=group_name)

            # Attach the AWS-managed DenyAll policy to the group
            print(f"Attaching managed policy 'AWSDenyAll' to group '{group_name}'.")
            client.attach_group_policy(
                GroupName=group_name,
                PolicyArn=managed_policy_arn
            )
            print(f"Managed policy 'AWSDenyAll' attached to group '{group_name}' successfully.")
        else:
            # Handle other possible errors
            print(f"Unexpected error: {e}")


def quarantine_user(session, username):
    group_name = 'quarantine'

    # Ensure the quarantine group exists
    ensure_quarantine_group(session)

    # Add the user to the quarantine group if not already in it
    add_user_to_group(session, username, group_name)

def remove_user_from_group(session, username,group_name):
    client = session.client('iam')
    # Remove user from group
    client.remove_user_from_group(GroupName=group_name, UserName=username)

def get_user_groups(session,username):
    user_groups = []
    marker = None

    client = session.client('iam')

    while True:

        # If there is a token to continue getting records use it, otherwise retrieve the first set of records
        if marker:
            response = client.list_groups_for_user(UserName=username,Marker=marker)
        else:
            response = client.list_groups_for_user(UserName=username)

        # Loop through each user in the response and collect the values
        for group in response.get("Groups"):
            temp_group = IAMGroup()
            temp_group.Path = group.get("Path")
            temp_group.GroupName = group.get("GroupName")
            temp_group.GroupID = group.get("GroupId")
            temp_group.ARN = group.get("Arn")
            temp_group.CreateDate = group.get("CreateDate")

            # Add the user to the list
            user_groups.append(temp_group)

        # Check if the response contains a next token, if it does then use it to get the next page of results,
        # if not exit the infinite loop
        if response.get("Marker"):
            marker = response.get("Marker")
        else:
            break

    # Return the list of users
    return user_groups