# AWS Tinkerer's Toolkit

---

AWS Tinkerer's Toolkit is a versatile and customizable Command Line Interface (CLI) tool designed for developers, DevOps
engineers, and AWS enthusiasts. This toolkit empowers users to create, manage, and run their custom Python tools with
ease, enabling them to streamline their workflows and address their unique requirements on AWS.

### Key Features

- **Custom Tool Creation**: Write your own Python scripts to perform specific tasks that matter most to you.
- **Ease of Use**: Run your custom tools seamlessly from the command line with minimal setup.
- **Modular Design**: Organize and manage your tools in a modular fashion, allowing for easy maintenance and updates.
- **AWS Integration**: Leverage the power of AWS services directly within your custom tools, enhancing your cloud
  operations and automations.
- **Extensible Framework**: Extend the toolkit’s functionality by adding new tools as your needs evolve.

### Why Use AWS Tinkerer's Toolkit?

The AWS Tinkerer's Toolkit is designed for flexibility and simplicity. Whether you're an experienced developer or a
newcomer to AWS, this toolkit provides the tools you need to customize your cloud environment and automate your
workflows, saving you time and enhancing your productivity.

## Getting Started

---

### Pre-requisites

- Valid AWS Account(s) - [AWS](https://aws.amazon.com/)
- AWS CLI v2 - [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- Python 3.12 or later - [Python 3.12](https://www.python.org/downloads/release/python-3120/)

### Installation

1. Clone the repository to your machine
2. Create a virtual environment: `python3 -m venv venv`
3. Activate the virtual environment: `source venv/bin/activate`
4. Install the requirements: `pip install -r requirements.txt`

### Running the Application

1. Open your terminal
2. Navigate to the project directory
3. Run the following command: `python3 tkk.py`

# Using the Application

---

## Common Functions

- `build_header`
    - The build_header function generates a formatted header for the application, displaying the application name and
      appropriately sized border lines.


- `build_menu`
    - The build_menu function is designed to create a CLI menu interface for the application. This function constructs
      and displays a structured menu with various components, providing users with clear and organized navigation
      options.


- `create_menu`
    - The create_menu function builds on the build_menu method to create an interactive CLI menu interface. It not only
      constructs and displays the menu but also incorporates user input collection and validation, ensuring a smooth and
      user-friendly experience.


- `form_builder`
    - The form_builder function is designed to create an interactive CLI form interface for collecting user information.
      It utilizes the build_header method to display a form header and guides users through a series of prompts to
      gather necessary details. Once the required information is collected, the results are returned to the calling
      function.


- `search_builder`
    - The search_builder function is designed to create an interactive search form within the CLI, facilitating user
      input for searching. It handles paging through search results, manages user selections, and ensures the validity
      of
      search inputs.

## Features

---

# Create AWS Session

The Create AWS functionality simplifies the creation of AWS boto3 sessions by allowing users to configure their
connection settings flexibly. Users can specify the AWS region, profile name, and access keys, with an optional Security
Token Service (STS) session key for enhanced security and temporary credentials.

```mermaid
---
config:
  theme: 'base'
  themeVariables:
    primaryColor: '#FFFFFF'
    primaryTextColor: '#000000'
    primaryBorderColor: '#000000'
    lineColor: '#F8B229'
    secondaryColor: '#20ab20ff'
    tertiaryColor: '#FFFFFF'
---
flowchart LR
        TTK@{ shape: div-rect, label: "TTK" } --> aws(Create AWS Session)
        aws --> pfn(Profile Name)
        aws --> ks(Key/Secret)
        aws --> sso(AWS SSO Login)
        aws --> cfg(Configure AWS SSO)
        aws --> asmrole(Assume Role)

        ups["`**User Prompts**
        - Profile Name (optional)
        - Region Name (optional)`"]
        pfn --> ups

        ksup["**User Prompts**
        - Access Key Id
        - Secrect Access Key
        - Session Token (optional)
        - Region Name (optional)"]
        ks --> ksup

        sso --> ssosub["`**Subprocess:** 
        _aws sso login_`"]

        cfg --> cfgsso["`**Subprocess:**
        _aws configure sso_`"]

        asmrprompt["**User Prompts**
        - Role ARN
        - Session Name (optional)
        - Region Name (optional)"]
        asmrole --> asmrprompt

        ssosub & cfgsso -->ssologin["`Rerun Create AWS Session and run **Profile Name** providing the name of the profile created in SSO`"]

        ups & ksup & ssologin & asmrprompt -->create_boto_session["`**Create boto3 session**
        _boto3.session.Session(**params)_`"]

        create_boto_session --> save_session["`Save session and config info globally`"]@{shape: div-rect}

        classDef green fill:#20ab20ff,stroke:#333,stroke-width:2px;
        class TTK,save_session green

```

# Show Regions

The Show Regions functionality allows for users to easily list out all AWS regions with their long/friendly names.
There are options to show all regions, show only the regions that are enabled, or show only the regions that are
disabled.

```mermaid
---
config:
  theme: 'base'
  themeVariables:
    primaryColor: '#FFFFFF'
    primaryTextColor: '#000000'
    primaryBorderColor: '#000000'
    lineColor: '#F8B229'
    secondaryColor: '#FFFFFF'
    tertiaryColor: '#FFFFFF'
    edgeLabelBackground: '#CBCBCB'
---
flowchart LR
        %% Define Objects
        start@{ shape: div-rect, label: "TTK" }
        id1(Create AWS Session)
        id2(Show Regions)

        id3["`**All Regions**
         _ENABLED_ | _ENABLING_ | _ENABLED_BY_DEFAULT_ | _DISABLED_ | _DISABLING_`"]

        id4["`**Enabled Only**
         _ENABLED_ | _ENABLING_ | _ENABLED_BY_DEFAULT`"]


       id5["`**Disabled Only**
        _DISABLED_ | _DISABLING_`"]

       id6["`**Get Regions**
       _account.list_regions_`"]

       id7["`**Get Region Friendly Name**
       _ssm.get_parameter_`"]

        exit["`Print Output`"]@{shape: div-rect}


        %% Connect Objects
        start -->id1
        id1 --> id2
        id2 --> id3 & id4 & id5
        id3 & id4 & id5 --> id6
        id6 --Loop Regions --> id7
        id7 --> exit


        %% Define Override styles
        classDef green fill:#20ab20ff,stroke:#333,stroke-width:2px;
        class start,exit green
```

# Security Group Scanner

The Security Group Scanner is a powerful feature designed to enhance your AWS security management. It scans all AWS
regions within your account, inspecting each security group per region. The results are parsed and compiled into a
comprehensive and easy-to-read report, both in text and JSON formats.

```mermaid
---
config:
  theme: 'base'
  themeVariables:
    primaryColor: '#FFFFFF'
    primaryTextColor: '#000000'
    primaryBorderColor: '#000000'
    lineColor: '#F8B229'
    secondaryColor: '#FFFFFF'
    tertiaryColor: '#FFFFFF'
    edgeLabelBackground: '#CBCBCB'
---
flowchart LR
        %% Define Objects
        start@{ shape: div-rect, label: "TTK" }
        id1(Create AWS Session)
        id2(Security Group Scanner)

        id3["`**Get Regions**
        _account.list_regions_`"]

        id4["`**Create AWS Session**
        _for each region_`"]

        id5["`**Get Security Groups**
        _ec2.describe_security_groups_`"]

        id6["`**Map SG Response to Model Objects**
        add objects to list`"]

        id7(Write SG Obj list ot json file on local fs)

        id8(Format SG obj list and print txt report on local fs)
   
        exit["`Notify user of report completion`"]@{shape: div-rect}

        %% Connect Objects
        start --> id1
        id1 --> id2
        id2 --> id3
        id3 -- loop regions --> id4

        id4 --> id5
        id5 -- loop security groups --> id6
        id6 --> id7
        id7 --> id8
        id8 --> exit
    
        %% Define Override styles
        classDef green fill:#20ab20ff,stroke:#333,stroke-width:2px;
        class start,exit green
```

# IAM User Report

The IAM User Report feature provides a detailed audit of all IAM users within your AWS account. It generates a
comprehensive text report and a JSON file, capturing detailed information about each IAM user.

```mermaid
---
config:
  theme: 'base'
  themeVariables:
    primaryColor: '#FFFFFF'
    primaryTextColor: '#000000'
    primaryBorderColor: '#000000'
    lineColor: '#F8B229'
    secondaryColor: '#FFFFFF'
    tertiaryColor: '#FFFFFF'
    edgeLabelBackground: '#CBCBCB'
---
flowchart LR
        %% Define Objects
        start@{ shape: div-rect, label: "TTK" }
        id1(Create AWS Session)
        id2(IAM Tools)
        id3(Generate IAM Users Report)

        id4["`**Get IAM Users**
        _iam.list_users_`"]

        id5["`**MFA Enabled**
        _iam.list_mfa_devices_`"]

        id6["`**Get Access Keys**
        _iam.list_access_keys_`"]

        id7["`**Get User Groups**
        _iam.list_groups_for_user_`"]

        id8["`**Get User Tags**
        _iam.list_user_tags_`"]

        id9["`Map IAM Responses to Model Objects
        _add objects to list_`"]

        id10(Write IAM Obj list ot json file on local fs)
        id11(Format IAM obj list and print txt report on local fs)

        exit["`Notify user of report completion`"]@{shape: div-rect}

        %% Connect Objects
        start --> id1
        id1 --> id2
        id2 --> id3
        id3 --> id4
        id4 -- loop users --> id5 & id6 & id7 & id8
        id5 & id6 & id7 & id8 --> id9
        id9 --> id10
        id10 --> id11
        id11 --> exit

        %% Define Override styles
        classDef green fill:#20ab20ff,stroke:#333,stroke-width:2px;
        class start,exit green
```

# IAM Key Rotator

The IAM Key Rotator within the AWS Tinkerer's Toolkit (TTK) integrates seamlessly with the IAM User Search feature,
enabling TTK users to efficiently manage access keys for IAM users. Users can search for an IAM user, retrieve their
details, and optionally move them to a quarantine IAM group to restrict access. Depending on the user's existing keys,
the tool automates key rotation: creating a new key if none exists, generating a new key and deactivating the current
one if only one key exists, or replacing the oldest key, deactivating the remaining key, and creating a new active key
if two keys are present. After each key rotation, the new access key and secret access key are securely stored as a JSON
file on the TTK user's local file system, ensuring ease of access and future reference.

```mermaid
---
config:
  theme: 'base'
  themeVariables:
    primaryColor: '#FFFFFF'
    primaryTextColor: '#000000'
    primaryBorderColor: '#000000'
    lineColor: '#F8B229'
    secondaryColor: '#FFFFFF'
    tertiaryColor: '#FFFFFF'
    edgeLabelBackground: '#CBCBCB'
---
flowchart LR
        %% Define Objects
        start@{ shape: div-rect, label: "TTK" }
        id1(Create AWS Session)
        id2(IAM Tools)
        id3(Search IAM Users)

        id4["`**User Prompts**
        - IAM Username`"]

        id5["`**Get IAM users**
        _iam.list_users_`"]

        id6(Use the user provided input to find the desired user)

        id7["`**Display the IAM User Details**
        _High level details_`"]

        id8(Show User Details)
        id9(Rotate Access Keys)
        id10(Quarantine User)

        id11(Format user and print)@{shape: div-rect}

        id12["`**Get IAM User Access keys**
        _iam.get_user
        iam.list_access_keys`"]

        id13{Quarantine group exists}

        id14("`**Add user to quarantine group**
        _iam.add_user_to_group_`")

        id15("`**Create quarantine group and deny all policy to itp**
        _iam.create_group_
        _iam.attach_group_policy_`")

        id16{Access Keys}

        id17("`**Create New Access Key**
        _iam.create_access_key_`")
        
        id18("`**Create New Access Key**
        _iam.create_access_key_`")

        id19("`**Identify oldest key and delete it**
        _iam.delete_access_key_`")

        id20("`**Inactivate Old Key**
        _iam.update_access_key_`")

        id23("`**Create New Access Key**
        _iam.create_access_key_`")

        id21("`**Inactivate Old Key**
        _iam.update_access_key`")

        id22(Write new access key to json file on local fs)

        exit["`Notify user of changes`"]@{shape: div-rect}

        %% Connect Objects
        start --> id1
        id1 --> id2
        id2 --> id3
        id3 --> id4
        id4 --> id5
        id5 -- Loop Users --> id6
        id6 --> id7
        id7 --> id8 & id9 & id10
        id8 --> id11
        id9 --> id12
        id12 --> id16
        id16 -- No Keys --> id17
        id16 -- 1 Key--> id18
        id16 -- 2 Keys --> id19
        id18 --> id20
        id19 --> id23
        id23 --> id21
        id17 & id20 & id21 --> id22
        id22 --> exit
        id10 --> id13
        id13 -- Yes --> id14
        id13 -- No --> id15
        id15 --> id14
        id14 --> exit

        %% Define Override styles
        classDef green fill:#20ab20ff,stroke:#333,stroke-width:2px;
        class start,exit,id11 green
```

# S3 Explorer

The S3 Explorer in the AWS Tinkerer's Toolkit (TTK) empowers users to interact seamlessly with AWS S3 buckets and their
contents. Users can search for AWS buckets, navigate through folder structures within selected buckets, and locate
specific files for download. The feature supports downloading individual files, as well as entire folders for efficient
data retrieval. Users can upload files directly to specified folders within the bucket and generate pre-signed URLs for
secure upload and download operations. This tool enhances user productivity by facilitating intuitive file management
and secure data transfer capabilities within AWS S3.


```mermaid
---
config:
  theme: 'base'
  themeVariables:
    primaryColor: '#FFFFFF'
    primaryTextColor: '#000000'
    primaryBorderColor: '#000000'
    lineColor: '#F8B229'
    secondaryColor: '#FFFFFF'
    tertiaryColor: '#FFFFFF'
    edgeLabelBackground: '#CBCBCB'
---
flowchart LR
        %% Define Objects
        start@{ shape: div-rect, label: "TTK" }
        id1(Create AWS Session)
        id2(S3 Explorer)
        id3("`**User Prompts**
        S3 Bucket Name`")

        id4["`**Get S3 Buckets**
        _s3.list_buckets_`"]

        id5(Use the user provided input to find the desired bucket)

        id6["`**Get the objects at the current level of the s3 bucket**
        _s3.list_objects_v2_`"]

        id7{Folder Options}

        id8(Select Item)

        id9(Search)

        id10(Download Folder)

        id11(Upload File to Folder)

        id12(Generate Upload Presigned URL)

        id13{Select Options}

        id14("`**User Prompts**
        - _Search Term_`")

        id15("`**User Prompts**
        - _Abs Path for download_`")

        id16("`**User Prompts**
        - _Abs Path of local file_`")

        id17("`**User Prompts**
        - _Desired filename_
        - Abs Path of local file`")

        id18("`**Get File Info**
        _s3.head_object_`")

        id19{File Options}

        id20("`**Upload File**
        _s3_upload_file_`")

        id21("`**Generate Presigned URL**
        _s3.generate_presigned_post_`")

        id22("`**Download Files**
        _s3.download_file_`")

        id23(Recursivly enter each folder and get files)

        id24(Create curl command as example)

        id25(Download File)

        id26(Generate Presigned URL)

        id27("`**User Prompts**
        - Abs Path of local file`")

        id28("`**User Prompts**
        - Desired filename
        - Abs Path of local file`")

        id29("`**Download Files**
        _s3.download_file`")

        id30("`**Generate Download Presigned URL**
        _s3.generate_presigned_url_`")

        %% Connect Objects
        start --> id1
        id1 --> id2
        id2 --> id3
        id3 --> id4
        id4 -- Loop Buckets --> id5
        id5 --> id6
        id6 --> id7
        id7 --> id8 & id9 & id10 & id11 & id12
        id8 --> id13
        id6 --Folder--> id13
        id13 --Files--> id18
        id18 --> id19
        id9 --> id14
        id14 --> id6
        id10 --> id15
        id15 --Loop Files --> id22
        id15 --Loop Folders --> id23
        id23 --> id22
        id11 --> id16
        id16 -->id20
        id12 --> id17
        id17 --> id21
        id21 --> id24
        id19 --> id25 & id26
        id25 --> id27
        id26 -->id28
        id28 --> id30
        id27 --> id29


        %% Define Override styles
        classDef green fill:#20ab20ff,stroke:#333,stroke-width:2px;
        class start,exit green
```


## License

This application is licensed under an MIT License. See
the [License](https://github.com/ssailor/aws-tinkerer-toolkit/blob/main/LICENSE) file for details.