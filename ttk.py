import aws_utils
import iam_key_rotator
import s3_explorer
import utils
import menu_builder
import subprocess
import security_group_scanner
import regex_patterns


class Config:
    def __init__(self, header_name=None):
        self.header_name = header_name
        self.session = None
        self.base_session = None
        self.aws_profile_name = None
        self.aws_region_name = None
        self.aws_access_key_id = None
        self.aws_secret_access_key = None
        self.aws_session_token = None
        self.aws_assume_rolename = None
        self.aws_account_id = None
        self.assumed_account_id = None

    def clear_config(self, retain_header_name=True):
        if retain_header_name is False:
            self.header_name = None

        self.session = None
        self.base_session = None
        self.aws_profile_name = None
        self.aws_region_name = None
        self.aws_access_key_id = None
        self.aws_secret_access_key = None
        self.aws_session_token = None
        self.aws_assume_rolename = None
        self.aws_account_id = None
        self.assumed_account_id = None

    def build_config_info(self):
        config_info = {}

        # Add config info
        if self.aws_profile_name:
            config_info["Profile Name"] = self.aws_profile_name

        if self.aws_region_name:
            config_info["Region Name"] = self.aws_region_name

        if self.aws_access_key_id:
            config_info["Access Key ID"] = self.aws_access_key_id

        if self.aws_assume_rolename:
            config_info["Assumed Role ARN"] = self.aws_assume_rolename

        if self.aws_account_id:
            config_info["Account ID"] = self.aws_account_id

        if self.assumed_account_id:
            config_info["Assumed Account ID"] = self.assumed_account_id

        return config_info


if __name__ == "__main__":

    # Build config object
    config = Config("AWS Tinkerer's Toolkit")

    while True:

        menu_items = [menu_builder.MenuItem("Create AWS Session", "AWS_SESSION")]

        if config.session:
            menu_items.append(menu_builder.MenuItem("Show Regions", "REGIONS"))
            menu_items.append(menu_builder.MenuItem("Security Group Scanner", "SG_SCANNER"))
            menu_items.append(menu_builder.MenuItem("IAM Tools", "IAM_TOOLS"))
            menu_items.append(menu_builder.MenuItem("S3 Explorer", "S3_EXPLORER"))

        config_info = config.build_config_info()

        # If no config info was added then set it to None
        if len(config_info) == 0:
            config_info = None

        choice = menu_builder.create_menu(config.header_name, description="What would you like to do?",
                                          menu_items=menu_items,
                                          is_main_menu=True, config_section=config_info)

        if choice == "AWS_SESSION":
            auth_menu_items = [menu_builder.MenuItem("Profile Name", "PROFILE_NAME"),
                               menu_builder.MenuItem("Key/Secret", "KEYS"),
                               menu_builder.MenuItem("AWS SSO Login", "AWS_SSO_LOGIN"),
                               menu_builder.MenuItem("Configure AWS SSO", "AWS_SSO")]

            if config.session is not None:
                if config.base_session is None:
                    auth_menu_items.append(menu_builder.MenuItem("Assume Role", "ASSUME_ROLE"))
                else:
                    auth_menu_items.append(menu_builder.MenuItem("Return to Base Session", "BASE_SESSION"))

            auth_choice = menu_builder.create_menu(config.header_name, section_name="AWS Auth",
                                                   description="How would you like to authenticate?",
                                                   menu_items=auth_menu_items, config_section=config_info)

            if auth_choice == "PROFILE_NAME":

                auth_profile_form_items = {"profile_name": menu_builder.FormItem("What profile would you like to use? "
                                                                                 "(Leave blank for default)"),
                                           "region_name": menu_builder.FormItem("What region would you like to use? ("
                                                                                "Optional)")}

                form_data = menu_builder.form_builder(config.header_name, "AWS Auth: Profile Name",
                                                      "Please provide the following information",
                                                      auth_profile_form_items, config_section=config_info)

                # If None was returned then treat it like a canceled and return to the parent menu
                if not form_data:
                    continue

                # Reset Global Variables
                config.clear_config(retain_header_name=True)

                profile = form_data.get("profile_name").response or "default"

                config.session = aws_utils.create_aws_session(profile_name=profile, region_name=form_data.get(
                    "region_name").response)

                # Update the global variables
                config.aws_profile_name = profile
                config.aws_region_name = form_data.get("region_name").response

                # Get the account id of the current session
                config.aws_account_id = aws_utils.get_current_account_id(config.session)


            elif auth_choice == "KEYS":

                auth_keys_form_items = {"access_key_id": menu_builder.FormItem("What is the access key ID?"),
                                        "secret_access_key": menu_builder.FormItem("What is the secret access key?"),
                                        "session_token": menu_builder.FormItem("What is the session token? (If you "
                                                                               "don't have one, leave this blank)"),
                                        "region_name": menu_builder.FormItem("What region would you like to use? ("
                                                                             "Optional)")}

                form_data = menu_builder.form_builder(config.header_name, "AWS Auth: IAM Keys",
                                                      "Please provide the following information", auth_keys_form_items,
                                                      config_section=config_info)

                # If None was returned then treat it like a canceled and return to the parent menu
                if not form_data:
                    continue

                # Reset Global Variables
                config.clear_config(retain_header_name=True)

                config.session = aws_utils.create_aws_session(region_name=form_data.get("region_name").response,
                                                              aws_credentials=aws_utils.AwsCredentials(
                                                                  access_key_id=form_data.get("access_key_id").response,
                                                                  secret_access_key=form_data.get(
                                                                      "secret_access_key").response,
                                                                  session_token=form_data.get(
                                                                      "session_token").response))

                # Update the global variables
                config.aws_region_name = form_data.get("region_name").response
                config.aws_access_key_id = form_data.get("access_key_id").response
                config.aws_secret_access_key = form_data.get("secret_access_key").response
                config.aws_session_token = form_data.get("session_token").response

                # Get the account id of the current session
                config.aws_account_id = aws_utils.get_current_account_id(config.session)

            elif auth_choice == "ASSUME_ROLE":
                if config.session is None:
                    print("You must create a session before assuming a role.")
                    menu_builder.wait_for_input()
                    continue

                config.base_session = config.session

                assume_role_form_items = {"role_arn": menu_builder.FormItem("What is the role ARN?"),
                                          "session_name": menu_builder.FormItem("What is the session name? (Optional)"),
                                          "region_name": menu_builder.FormItem(
                                              "What region would you like to use? (Optional)")}

                form_data = menu_builder.form_builder(config.header_name, "AWS Auth: Assume Role",
                                                      "Please provide the following information",
                                                      assume_role_form_items, config_section=config_info)

                # If None was returned then treat it like a canceled and return to the parent menu
                if not form_data:
                    continue

                # Reset Global Variables
                config.aws_assume_rolename = None
                config.assumed_account_id = None

                if form_data.get("session_name").response == "" or form_data.get("session_name").response is None:
                    form_data["session_name"].response = "AWSTinkererToolkit"

                config.session = aws_utils.assume_role(config.session, role_arn=form_data.get("role_arn").response,
                                                       session_name=form_data.get("session_name").response,
                                                       region_name=form_data.get("region_name").response)

                # Update the global variables
                config.aws_region_name = form_data.get("region_name").response
                config.aws_assume_rolename = form_data.get("role_arn").response
                config.assumed_account_id = aws_utils.get_current_account_id(config.session)


            elif auth_choice == "BASE_SESSION":
                if config.base_session is None:
                    print("Invalid Choice: You are not current in an assumed role session.")
                    menu_builder.wait_for_input()
                    continue

                config.session = config.base_session
                config.base_session = None
                config.aws_assume_rolename = None
                config.assumed_account_id = None

            elif auth_choice == "AWS_SSO":
                sso_menu = menu_builder.build_menu(config.header_name, "AWS SSO Configuration",
                                                   "Please follow the prompts to create a role using AWS SSO",
                                                   padding=20,
                                                   center_section=False, config_section=config_info)

                # Clear the screen and display the menu
                menu_builder.clear_screen()
                print(sso_menu)

                # Run a subprocess to execute the aws configure sso command
                subprocess.run("aws configure sso", shell=True)
                print("")
                menu_builder.wait_for_input()

            elif auth_choice == "AWS_SSO_LOGIN":
                sso_menu = menu_builder.build_menu(config.header_name, "AWS SSO Login",
                                                   "Please follow the prompts to login to the AWS SSO",
                                                   padding=20,
                                                   center_section=False, config_section=config_info)

                # Clear the screen and display the menu
                menu_builder.clear_screen()
                print(sso_menu)

                # Run a subprocess to execute the aws configure sso command
                subprocess.run("aws sso login", shell=True)
                print("")
                menu_builder.wait_for_input()
            else:
                continue


        elif choice == "REGIONS":
            regions_menu = [menu_builder.MenuItem("All Regions", "ALL_REGIONS"),
                            menu_builder.MenuItem("Enabled Only", "ENABLED_REGIONS"),
                            menu_builder.MenuItem("Disabled Only", "DISABLED_REGIONS")]

            region_choice = menu_builder.create_menu(config.header_name, section_name="Regions", description="What set "
                                                                                                             "of "
                                                                                                             "regions would "
                                                                                                             "you like to see?",
                                                     menu_items=regions_menu, config_section=config_info)

            regions = []
            region_title = None

            if region_choice == "ALL_REGIONS":
                regions = aws_utils.get_regions(config.session, region_status_filter=aws_utils.AccountStatusFilters.ALL)
                region_title = "All Regions"

            elif region_choice == "ENABLED_REGIONS":
                regions = aws_utils.get_regions(config.session,
                                                region_status_filter=aws_utils.AccountStatusFilters.ENABLED)
                region_title = "Enabled Regions"

            elif region_choice == "DISABLED_REGIONS":
                regions = aws_utils.get_regions(config.session,
                                                region_status_filter=aws_utils.AccountStatusFilters.DISABLED)
                region_title = "Disabled Regions"
            else:
                continue

            regions_header_menu = menu_builder.build_menu(config.header_name, region_title, description=None,
                                                          padding=20,
                                                          center_section=True, config_section=config_info)

            # Clear the screen and display the menu
            menu_builder.clear_screen()
            print(regions_header_menu)

            for region in regions:
                print(f"{region} | {aws_utils.get_region_friendly_name(config.session, region)}")

            print("\n")
            menu_builder.wait_for_input()

        elif choice == "SG_SCANNER":

            sg_results = {}
            filename_account_id = config.aws_account_id

            regions_header_menu = menu_builder.build_menu(config.header_name, "Security Group Scanner",
                                                          description=None, padding=20, center_section=True,
                                                          config_section=config_info)

            # Clear the screen and display the menu
            menu_builder.clear_screen()
            print(regions_header_menu)

            # Loop though all the regions and get the security groups
            for region in aws_utils.get_regions(config.session,
                                                region_status_filter=aws_utils.AccountStatusFilters.ENABLED):
                # Check for a profile name and reuse it to create a new session for the region change otherwise use
                # the key information
                if config.aws_profile_name:
                    temp_session = aws_utils.create_aws_session(region_name=region,
                                                                profile_name=config.aws_profile_name)
                else:
                    temp_session = aws_utils.create_aws_session(region_name=region,
                                                                aws_credentials=aws_utils.AwsCredentials(
                                                                    access_key_id=config.aws_access_key_id,
                                                                    secret_access_key=config.aws_access_key_id,
                                                                    session_token=config.aws_session_token))

                # If you are using an assumed role then re-assume the role in the new region
                if config.aws_assume_rolename:
                    temp_session = aws_utils.assume_role(temp_session, role_arn=config.aws_assume_rolename,
                                                         session_name="AWSTinkererToolkit",
                                                         region_name=region)
                    filename_account_id = config.assumed_account_id

                sg_results[region] = security_group_scanner.get_security_groups(temp_session)
                print(f"{region} Scan Complete")

            # Generate a timestamp for the filename (This will allow for both files to have the same timestamp for
            # easy comparison between the json and txt files
            filename_timestamp = utils.datetime_now_string("%Y-%m-%dT%H-%M-%S")
            sg_report_filename = f"{filename_timestamp}--"f"{filename_account_id}--SecurityGroupReport"
            # Write the results to a json file
            utils.write_json_file(f"{sg_report_filename}.json",
                                  sg_results)

            # Generate the formatted txt report and print it
            sg_report = security_group_scanner.format_report(config.session, sg_results)
            utils.write_file(f"{sg_report_filename}.txt", sg_report)

            print("\nSecurity Group Report Generated...")

            # Ask the user if they would like to view the report, if yes then open the file with the default program
            confirm_prompt = input("Would you like to view the report? (y/n): ")
            if menu_builder.regex_validator(confirm_prompt, regex_patterns.REGEX_BOOL_YES):
                utils.open_file(f"{sg_report_filename}.txt")
                continue
            elif menu_builder.regex_validator(confirm_prompt, regex_patterns.REGEX_BOOL_NO):
                continue
            else:
                print("\nInvalid input provided. Please provide a valid value y/n")
                menu_builder.wait_for_input()
                continue

        elif choice == "IAM_TOOLS":
            while True:
                iam_tool_menu = [menu_builder.MenuItem("Search IAM Users", "SEARCH_IAM_USERS"),
                                 menu_builder.MenuItem("Generate IAM Users Report", "IAM_USERS_REPORT"), ]

                iam_tool_choice = menu_builder.create_menu(config.header_name, section_name="IAM Tools",
                                                           description="What would you like to do?",
                                                           menu_items=iam_tool_menu, config_section=config_info)

                if iam_tool_choice == "SEARCH_IAM_USERS":
                    search_prompt = "IAM Username: "
                    quarantine_group_name = "quarantine"

                    iam_users = iam_key_rotator.get_iam_users(config.session)

                    search_selection = menu_builder.search_builder(config.header_name, section_name="Search",
                                                                   search_list=iam_users,
                                                                   config_section=config_info,
                                                                   search_prompt_text=search_prompt,
                                                                   comparator_func=iam_key_rotator.comparitor_iam_users)

                    # If None was returned then treat it like a canceled and return to the parent menu
                    if search_selection is None:
                        continue

                    while True:
                        temp_user = None
                        user_info = None

                        for user in iam_users:
                            if user.UserID == search_selection:
                                temp_user = iam_key_rotator.get_iam_user_details(config.session, user.UserName)
                                user_info = iam_key_rotator.format_user_view(temp_user)
                                break

                        # check if user is in the quarantine group
                        in_quarantine = any(group.GroupName == quarantine_group_name for group in temp_user.IAMGroups)

                        user_menu_items = [menu_builder.MenuItem("Show User Details", "SHOW_USER_DETAILS"),
                                           menu_builder.MenuItem("Rotate Access Keys", "ROTATE_ACCESS_KEYS")]

                        if in_quarantine is False:
                            user_menu_items.append(menu_builder.MenuItem("Quarantine User", "QUARANTINE_USER"))
                        else:
                            user_menu_items.append(menu_builder.MenuItem("Remove User From Quarantine",
                                                                         "UNQUARANTINE_USER"))

                        user_info_menu = menu_builder.create_menu(header_name=config.header_name,
                                                                  section_name=f"IAM User Details: "f"{temp_user.UserName}",
                                                                  config_section=config_info, content_section=user_info,
                                                                  menu_items=user_menu_items)

                        # If None was returned then treat it like a canceled and return to the parent menu
                        if not user_info_menu:
                            continue

                        if user_info_menu == "SHOW_USER_DETAILS":
                            menu_builder.clear_screen()
                            formatted_user_details = iam_key_rotator.format_user_details(temp_user)

                            iam_detailed_user = menu_builder.build_menu(config.header_name, "IAM: User Details",
                                                                        description=None, padding=20,
                                                                        center_section=False,
                                                                        config_section=config_info,
                                                                        content_section=formatted_user_details)
                            print(iam_detailed_user)
                            menu_builder.wait_for_input()

                        elif user_info_menu == "ROTATE_ACCESS_KEYS":
                            confirm_prompt = input("Are you sure you want to continue? (y/n): ")
                            if menu_builder.regex_validator(confirm_prompt, regex_patterns.REGEX_BOOL_YES):
                                print("Rotating Access Keys...")
                                iam_key_rotator.rotate_access_keys(config.session, temp_user.UserName)
                                print("Access Keys Rotated...")

                                menu_builder.wait_for_input()
                            elif menu_builder.regex_validator(confirm_prompt, regex_patterns.REGEX_BOOL_NO):
                                print("Access Key Rotation Cancelled...")
                                menu_builder.wait_for_input()
                            else:
                                print("\nInvalid input provided. Please try again...")
                                menu_builder.wait_for_input()
                                continue

                        elif user_info_menu == "QUARANTINE_USER":
                            confirm_prompt = input("Are you sure you want to continue? (y/n): ")
                            if menu_builder.regex_validator(confirm_prompt, regex_patterns.REGEX_BOOL_YES):
                                print("Quarantining User...")
                                iam_key_rotator.quarantine_user(config.session, temp_user.UserName)
                                print("User Quarantined...")
                                menu_builder.wait_for_input()
                                continue
                            elif menu_builder.regex_validator(confirm_prompt, regex_patterns.REGEX_BOOL_NO):
                                print("Quarantine Cancelled...")
                                menu_builder.wait_for_input()
                            else:
                                print("\nInvalid input provided. Please try again...")
                                menu_builder.wait_for_input()
                                continue

                        elif user_info_menu == "UNQUARANTINE_USER":
                            confirm_prompt = input("Are you sure you want to continue? (y/n): ")
                            if menu_builder.regex_validator(confirm_prompt, regex_patterns.REGEX_BOOL_YES):
                                print("Removing user from Quarantine...")
                                iam_key_rotator.remove_user_from_group(config.session, temp_user.UserName,
                                                                       quarantine_group_name)
                                print("User Removed From Quarantine...")
                                menu_builder.wait_for_input()
                                continue
                            elif menu_builder.regex_validator(confirm_prompt, regex_patterns.REGEX_BOOL_NO):
                                print("Operation Cancelled, user is still in quarantine...")
                                menu_builder.wait_for_input()
                            else:
                                print("\nInvalid input provided. Please try again...")
                                menu_builder.wait_for_input()
                                continue

                        elif user_info_menu == "back":
                            break
                        else:
                            print("This feature is not yet implemented. Please check back later.")
                            menu_builder.wait_for_input()

                elif iam_tool_choice == "IAM_USERS_REPORT":

                    menu_builder.clear_screen()
                    print(
                        menu_builder.build_menu(config.header_name, "IAM: Generate IAM Users Report", description=None,
                                                padding=20,
                                                center_section=False, config_section=config_info))
                    filename_account_id = config.aws_account_id
                    users = iam_key_rotator.get_iam_users(config.session, get_details=True)

                    # Write the results to a json file
                    if config.assumed_account_id:
                        utils.write_json_file(
                            f"{utils.datetime_now_string("%Y-%m-%dT%H-%M-%S")}--"f"{config.assumed_account_id}--IAMUsersReport.json",
                            users)
                    else:
                        utils.write_json_file(
                            f"{utils.datetime_now_string("%Y-%m-%dT%H-%M-%S")}--"f"{config.aws_account_id}--IAMUsersReport.json",
                            users)

                    # Generate the formatted txt report and print it
                    iam_report = iam_key_rotator.format_users_report(config.session, users)
                    iam_users_report_filename = None
                    if config.assumed_account_id:
                        iam_users_report_filename = f"{utils.datetime_now_string("%Y-%m-%dT%H-%M-%S")}--"f"{config.assumed_account_id}--IAMUsersReport.txt"
                    else:
                        iam_users_report_filename = f"{utils.datetime_now_string("%Y-%m-%dT%H-%M-%S")}--"f"{config.aws_account_id}--IAMUsersReport.txt"

                    # Write the report to a file
                    utils.write_file(iam_users_report_filename, iam_report)
                    print("IAM Users Report Generated...")

                    # Ask the user if they would like to view the report, if yes then open the file with the default program
                    confirm_prompt = input("Would you like to view the report? (y/n): ")
                    if menu_builder.regex_validator(confirm_prompt, regex_patterns.REGEX_BOOL_YES):
                        utils.open_file(iam_users_report_filename)
                        continue
                    elif menu_builder.regex_validator(confirm_prompt, regex_patterns.REGEX_BOOL_NO):
                        continue
                    else:
                        print("\nInvalid input provided. Please provide a valid value y/n")
                        menu_builder.wait_for_input()
                        continue
                elif iam_tool_choice == "back":
                    break

        elif choice == "S3_EXPLORER":
            search_prompt = "S3 Bucket Name: "

            s3_buckets = s3_explorer.list_buckets(config.session)

            bucket_search_selection = menu_builder.search_builder(config.header_name, section_name="Search",
                                                                  search_list=s3_buckets,
                                                                  config_section=config_info,
                                                                  search_prompt_text=search_prompt,
                                                                  comparator_func=s3_explorer.comparitor_s3_bucket)

            if not bucket_search_selection:
                continue

            selected_path = None
            while True:
                if not bucket_search_selection:
                    continue
                else:
                    file_items, folder_items = s3_explorer.list_objects_and_folders(config.session,
                                                                                    bucket_search_selection,
                                                                                    prefix=selected_path)

                    # Combine the lists for the search results
                    folder_objects = [*file_items, *folder_items]

                    # Sort the objects
                    folder_objects.sort()

                    addl_folder_search_options = []
                    if selected_path is not None and selected_path != "":
                        addl_folder_search_options.append(menu_builder.MenuItem("Parent Folder", "PARENT_FOLDER"))
                    addl_folder_search_options.append(menu_builder.MenuItem("Download Folder", "DOWNLOAD_FOLDER"))
                    addl_folder_search_options.append(menu_builder.MenuItem("Upload File to Folder", "UPLOAD_FILE"))
                    addl_folder_search_options.append(
                        menu_builder.MenuItem("Generate Upload Presigned URL", "UPLOAD_URL"))

                    # Convert the search result list to Menu items
                    folder_obj_items = []
                    for obj in folder_objects:
                        # Todo: Fix the obj here
                        if obj.endswith('/'):
                            display_name = str(obj).split('/')[-2] + "/"
                        else:
                            if "/" in obj:
                                display_name = str(obj).split('/')[-1]
                            else:
                                display_name = obj
                        folder_obj_items.append(menu_builder.MenuItem(display_name, obj))

                    folder_search_selection = menu_builder.search_builder(config.header_name, section_name="Search",
                                                                          search_list=folder_obj_items,
                                                                          config_section=config_info,
                                                                          search_prompt_text="Object Name:",
                                                                          comparator_func=s3_explorer.comparitor_s3_bucket,
                                                                          additional_search_options=addl_folder_search_options,
                                                                          use_search_results=True,
                                                                          results_header=f"Path: {selected_path if selected_path else '/'}")

                    # If None was returned then treat it like a canceled and return to the parent menu
                    if not folder_search_selection:
                        break

                    if folder_search_selection in [item.unique_id for item in addl_folder_search_options]:
                        if folder_search_selection == "UPLOAD_FILE":
                            upload_file_form_items = {"local_file_path": menu_builder.FormItem("What is the absolute "
                                                                                               "path of the local file you want to upload?")}

                            form_data = menu_builder.form_builder(config.header_name, "S3 Explorer: Upload File",
                                                                  "Please provide the "
                                                                  "following information",
                                                                  upload_file_form_items, config_section=config_info)

                            # If None was returned then treat it like a canceled and return to the parent menu
                            if not form_data:
                                continue

                            if form_data.get("local_file_path").response == "" or form_data.get(
                                    "local_file_path").response is None:
                                raise Exception("You must provide a valid file path to upload.")
                            else:
                                s3_explorer.upload_file(config.session, bucket_search_selection,
                                                        form_data.get("local_file_path").response, selected_path)
                                print("File Uploaded...")
                                menu_builder.wait_for_input()
                                continue

                        elif folder_search_selection == "UPLOAD_URL":
                            upload_url_form_items = {"file_name": menu_builder.FormItem("What is the file name "
                                                                                        "you want to upload "
                                                                                        "to?"),
                                                     "local_file_abs_path": menu_builder.FormItem("What is the "
                                                                                                  "absolute path of "
                                                                                                  "the local file ?")}

                            form_data = menu_builder.form_builder(config.header_name,
                                                                  "S3 Explorer: Generate Upload Presigned URL",
                                                                  "Please provide the following information",
                                                                  upload_url_form_items, config_section=config_info)

                            # If None was returned then treat it like a canceled and return to the parent menu
                            if not form_data:
                                continue

                            if selected_path == "" or selected_path is None:
                                upload_url_path = form_data.get("file_name").response
                            else:
                                upload_url_path = selected_path + form_data.get("file_name").response

                            if (form_data.get("file_name").response == "" or form_data.get("file_name").response is
                                    None):
                                raise Exception("You must provide a valid file path to upload.")
                            else:
                                upload_url, upload_fields = s3_explorer.generate_upload_presigned_url(config.session,
                                                                                                      bucket_search_selection,
                                                                                                      upload_url_path,
                                                                                                      60)

                                curl_upload_command = s3_explorer.create_curl_upload_command(upload_url, upload_fields,
                                                                                             file=form_data.get(
                                                                                                 "local_file_abs_path").response)

                                print(f"Curl Example for Upload Presigned URL Usage\n")
                                print(curl_upload_command + "\n")
                                print("URL Expires in 60 seconds from creation...")
                                menu_builder.wait_for_input()
                                continue

                        elif folder_search_selection == "PARENT_FOLDER":

                            if selected_path == "" or selected_path == "/" or selected_path is None:
                                print("You are already at the root of the bucket.")
                                continue

                            if selected_path.endswith('/'):
                                temp_path = selected_path[:-1]
                            else:
                                temp_path = selected_path

                            temp_path = temp_path.split("/")
                            if len(temp_path) > 1:
                                selected_path = "".join(temp_path[:-1])
                            else:
                                selected_path = ""

                        elif folder_search_selection == "DOWNLOAD_FOLDER":
                            download_folder_form_items = {
                                "local_folder_path": menu_builder.FormItem("What is the absolute "
                                                                           "path of the local folder you want to download to?")}

                            form_data = menu_builder.form_builder(config.header_name, "S3 Explorer: Download Folder",
                                                                  "Please provide the "
                                                                  "following information",
                                                                  download_folder_form_items,
                                                                  config_section=config_info)

                            # If None was returned then treat it like a canceled and return to the parent menu
                            if not form_data:
                                continue

                            local_path = form_data.get("local_folder_path").response

                            folder_download_menu = menu_builder.build_menu(config.header_name,
                                                                           "S3 Explorer: Download Folder",
                                                                           description=None,
                                                                           padding=20,
                                                                           center_section=False,
                                                                           config_section=config_info)

                            # Clear the screen and display the menu
                            menu_builder.clear_screen()
                            print(folder_download_menu)

                            if local_path == "" or local_path is None:
                                raise Exception("You must provide a valid folder path to download.")
                            else:
                                s3_explorer.download_s3_folder(config.session, bucket_search_selection,
                                                               selected_path, local_path, recurse=True)

                                print("\nDownloads Complete...")
                                menu_builder.wait_for_input()
                                continue

                    # Results from search menu that were not from the additional search options
                    else:
                        # If ends in / then it's a folder, otherwise assume a file
                        if folder_search_selection.endswith('/'):
                            selected_path = folder_search_selection
                        else:
                            # If selection is a file then pull head info for object, and create new menu for file
                            file_head_info = s3_explorer.get_file_info(config.session, bucket_search_selection,
                                                                       folder_search_selection)

                            if file_head_info.get('StorageClass') is None:
                                storage_class = "STANDARD"
                            else:
                                storage_class = file_head_info.get('StorageClass')

                            s3_filename = str(folder_search_selection).split('/')[-1]
                            file_info = f"File Name: {s3_filename}\n"
                            file_info += f"Size: {utils.foramt_bytes(file_head_info.get('ContentLength'))}\n"
                            file_info += f"Last Modified: {str(file_head_info.get('LastModified'))}\n"
                            file_info += f"Storage Class: {storage_class}\n"
                            file_info += f"ETag: {str(file_head_info.get('ETag')).replace('"', '')}\n"
                            file_info += f"S3 Uri: s3://{bucket_search_selection}/{selected_path}{s3_filename}\n"

                            s3_file_menu_items = [menu_builder.MenuItem("Download File", "DOWNLOAD_FILE"),
                                                  menu_builder.MenuItem("Generate Presigned URL", "DOWNLOAD_URL")]

                            s3_file_menu = menu_builder.create_menu(header_name=config.header_name,
                                                                    section_name=f"S3 Explorer: File Details",
                                                                    config_section=config_info,
                                                                    content_section=file_info,
                                                                    menu_items=s3_file_menu_items)

                            # If None was returned then treat it like a canceled and return to the parent menu
                            if not s3_file_menu:
                                continue

                            if s3_file_menu == "DOWNLOAD_FILE":
                                download_file_form_items = {
                                    "local_folder_path": menu_builder.FormItem("What is the absolute "
                                                                               "path of the local folder you want to download to?")}

                                form_data = menu_builder.form_builder(config.header_name,
                                                                      "S3 Explorer: Download File",
                                                                      "Please provide the "
                                                                      "following information",
                                                                      download_file_form_items,
                                                                      config_section=config_info)

                                # If None was returned then treat it like a canceled and return to the parent menu
                                if not form_data:
                                    continue

                                local_path = form_data.get("local_folder_path").response

                                file_download_menu = menu_builder.build_menu(config.header_name,
                                                                             "S3 Explorer: Download File",
                                                                             description=None,
                                                                             padding=20,
                                                                             center_section=False,
                                                                             config_section=config_info)

                                # Clear the screen and display the menu
                                menu_builder.clear_screen()
                                print(file_download_menu)

                                if local_path == "" or local_path is None:
                                    raise Exception("You must provide a valid folder path to download.")
                                else:
                                    if not local_path.endswith("/"):
                                        local_path += "/"
                                    s3_explorer.download_file(config.session, bucket_search_selection,
                                                              folder_search_selection, local_path + s3_filename)

                                    print("\nDownload Complete...")
                                    menu_builder.wait_for_input()
                                    continue
                            elif s3_file_menu == "DOWNLOAD_URL":
                                download_url = s3_explorer.generate_download_presigned_url(config.session,
                                                                                           bucket_search_selection,
                                                                                           folder_search_selection, 60)
                                print(f"Presigned URL For {folder_search_selection}: {download_url}")
                                print("URL Expires in 60 seconds from creation...")
                                menu_builder.wait_for_input()
                                continue

            # menu_builder.wait_for_input()

        elif choice == "exit":
            menu_builder.clear_screen()
            exit()
