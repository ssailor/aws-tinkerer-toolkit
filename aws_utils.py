import boto3
from enum import Enum


class AwsCredentials:
    def __init__(self, access_key_id, secret_access_key, session_token=None):
        self.AccessKeyId = access_key_id
        self.SecretAccessKey = secret_access_key
        self.SessionToken = session_token


class AccountStatusFilters(Enum):
    ENABLED = 1
    DISABLED = 2
    ALL = 3


def create_aws_session(region_name=None, profile_name=None, aws_credentials=None):
    # Dynamically build the parameters that will be passed into the boto method
    params = {}

    # Guard Checks
    if aws_credentials is not None and not isinstance(aws_credentials, AwsCredentials):
        raise ValueError("Invalid aws_credentials object")

    if profile_name and aws_credentials:
        raise ValueError("You can't provide both profile_name and aws_credentials")

    # Build out parameters to create the session
    if region_name:
        params.update({"region_name": region_name})
    else:
        params.update({"region_name": "us-east-1"})

    if profile_name:
        params.update({"profile_name": profile_name})

    if aws_credentials:
        params.update({"aws_access_key_id": aws_credentials.AccessKeyId,
                       "aws_secret_access_key": aws_credentials.SecretAccessKey})
        if aws_credentials.SessionToken:
            params.update({"aws_session_token": aws_credentials.SessionToken})

    # Build the session
    return boto3.session.Session(**params)

def change_session_region(session, new_region_name):
    creds = AwsCredentials(session.get_credentials().access_key, session.get_credentials().secret_key,
                           session.get_credentials().token)

    if session.profile_name:
        return create_aws_session(region_name=new_region_name, profile_name=session.profile_name)
    else:
        return create_aws_session(region_name=new_region_name, aws_credentials=creds)


# Using an existing session, assume a role and return a new session
def assume_role(session, role_arn, session_name, region_name=None):
    client = session.client('sts')
    response = client.assume_role(
        RoleArn=role_arn,
        RoleSessionName=session_name
    )
    response_creds = response.get("Credentials")
    ca_creds = AwsCredentials(response_creds.get("AccessKeyId"), response_creds.get("SecretAccessKey"),
                              response_creds.get("SessionToken"))
    role_session = create_aws_session(region_name=region_name, profile_name=None, aws_credentials=ca_creds)
    return role_session


# Get all the regions and their status in the calling account
def get_regions(session, region_status_filter=AccountStatusFilters.ALL):
    regions = []

    enabled_status = ["ENABLED", "ENABLING", "ENABLED_BY_DEFAULT"]
    disabled_status = ["DISABLED", "DISABLING"]
    all_status = enabled_status + disabled_status

    if not isinstance(region_status_filter, AccountStatusFilters):
        raise Exception("Invalid region_status_filter")

    if region_status_filter == AccountStatusFilters.ENABLED:
        region_filter = enabled_status
    elif region_status_filter == AccountStatusFilters.DISABLED:
        region_filter = disabled_status
    else:
        region_filter = all_status

    client = session.client(service_name="account")
    paginator = client.get_paginator("list_regions")

    # Loop though all the pages and get the regions
    for page in paginator.paginate(RegionOptStatusContains=region_filter):
        for item in page.get("Regions"):
            regions.append(item.get("RegionName"))

    return regions

def get_region_friendly_name(session, region_name):
    client = session.client(service_name="ssm")
    response = client.get_parameter(Name=f"/aws/service/global-infrastructure/regions/{region_name}/longName")
    return response.get("Parameter").get("Value")

def get_current_account_id(session):
    client = session.client(service_name="sts")
    response = client.get_caller_identity()
    return response.get("Account")

