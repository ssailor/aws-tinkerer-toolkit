import os
import re
import copy
import regex_patterns


class MenuItem:
    def __init__(self, text, id):
        self.display_text = text
        self.unique_id = id


class FormItem:
    def __init__(self, prompt, regex_pattern=None):
        self.user_prompt = prompt
        self.regex_validation_pattern = regex_pattern
        self.response = None


# Create a Pageinator class for paging through search results
class Paginator:
    def __init__(self, items, page_size=10):
        self.items = items
        self.page_size = page_size
        self.current_page = 0

    def get_page(self, page_number):
        start = page_number * self.page_size
        end = start + self.page_size
        return self.items[start:end]

    def next_page(self):
        self.current_page += 1
        if self.current_page * self.page_size >= len(self.items):
            self.current_page = 0  # Wrap around to the first page
        return self.get_page(self.current_page)

    def previous_page(self):
        self.current_page -= 1
        if self.current_page < 0:
            self.current_page = (len(self.items) - 1) // self.page_size  # Wrap around to the last page
        return self.get_page(self.current_page)

    def get_current_page(self):
        return self.get_page(self.current_page)

    def has_next_page(self):
        return (self.current_page + 1) * self.page_size < len(self.items)

    def has_previous_page(self):
        return self.current_page > 0

    def total_pages(self):
        return (len(self.items) + self.page_size - 1) // self.page_size

    def current_range_string(self):
        start = (self.current_page * self.page_size) + 1
        end = min((start - 1) + self.page_size, len(self.items))
        return f"{start}-{end} of {len(self.items)}"


def wait_for_input():
    input("Press Enter to continue...")


def clear_screen():
    # Print a large number of newlines to overwrite the scrollback buffer in the console (more readable this way)
    print("\n" * 1000)

    if os.name == 'nt':  # Check if the OS is Windows
        os.system('cls')  # Clear the screen for windows
    else:
        os.system('clear')  # Clear the screen for unix based systems


def build_divider(header_name, padding=20):
    return f"{'-' * (len(header_name) + (padding * 2) + 2)}\n"


def build_header(header_name, padding=20):
    header = f"*{'-' * padding}{'-' * (len(header_name))}{'-' * padding}*" + "\n"
    header += f"|{' ' * padding}{header_name}{' ' * padding}|" + "\n"
    header += f"*{'-' * padding}{'-' * (len(header_name))}{'-' * padding}*" + "\n"
    return header


def build_menu(header_name, section_name=None, description=None, padding=20, center_section=False, config_section=
None, content_section=None):
    divider = build_divider(header_name, padding)
    header = build_header(header_name, padding)

    # Build the menu as a single string for better spacing on the console
    menu = ""
    menu += header

    # Add the config section if it exists
    if config_section:
        menu += "Config Info" + "\n"
        menu += divider
        for key, value in config_section.items():
            menu += f"{key}: {value}" + "\n"
        menu += divider

    # Add the section name if it exists
    if section_name:
        if center_section:
            menu += f"{' ' * padding}{section_name}{' ' * padding}" + "\n"
        else:
            menu += section_name + "\n"
        menu += divider

    # Add the description if it exists
    if description:
        menu += description + "\n"
        menu += divider

    # Add a Content Section if it exists
    if content_section:
        menu += content_section + "\n"
        menu += divider

    return menu


def create_menu(header_name, section_name=None, description=None, menu_items=None, padding=20, center_section=False,
                is_main_menu=False, config_section=None, content_section=None):
    # Create the menu
    menu = build_menu(header_name=header_name, section_name=section_name, description=description, padding=padding,
                      center_section=center_section, config_section=config_section, content_section=content_section)

    # Create the divider for the form formatting
    divider = build_divider(header_name, padding)

    # Check if this menu is the main menu, if it is then add an exit option else add a back option
    if is_main_menu:
        menu_items.append(MenuItem("Exit", "exit"))
    else:
        menu_items.append(MenuItem("Back", "back"))

    # Add the menu items to the menu
    for index, item in enumerate(menu_items, 1):
        if isinstance(item, MenuItem):
            menu += f"{index}. {item.display_text}" + "\n"
        else:
            raise ValueError("Invalid menu item provided")

    # Add a divider after the menu items for formatting
    menu += divider

    # Loop until the user selects a valid option
    while True:
        # Display the menu
        clear_screen()
        print(menu)
        if len(menu_items) == 1:
            user_choice = input(f"What would you like to do? :")
        elif len(menu_items) > 1:
            user_choice = input(f"What would you like to do? (1-{len(menu_items)}) :")
        else:
            raise ValueError("No menu items were provided")

        if user_choice.isdigit() and int(user_choice) != 0 and int(user_choice) <= len(menu_items):
            return menu_items[int(user_choice) - 1].unique_id
        else:
            clear_screen()
            print(f"Invalid choice. Please select a valid option between 1 and {len(menu_items)}")
            wait_for_input()


def form_builder(header_name, section_name=None, description=None, form_items=None, padding=20, center_section=False,
                 config_section=None):
    # Create the menu for the form
    menu = build_menu(header_name=header_name, section_name=section_name, description=description, padding=padding,
                      center_section=center_section, config_section=config_section)

    # Create the divider for the form formatting
    divider = build_divider(header_name, padding)

    # Create a copy of the form items to reset the form if the user wants to restart
    temp_form_items = copy.deepcopy(form_items)

    # Loop until the user provides valid input for all form items
    while True:
        # Create a flag to determine if all items in the form are valid
        all_items_valid = True

        # Display the menu
        clear_screen()
        print(menu)

        # Print out all items that have a response (this makes sure all items already collected are displayed first)
        for key, value in form_items.items():
            if isinstance(value, FormItem):
                if value.response:
                    print(f"{value.user_prompt}: {value.response}")
                    continue
            else:
                raise ValueError("Invalid form item provided")

        # Loop through all form items and prompt the user for input
        for key, value in form_items.items():
            if isinstance(value, FormItem):

                # Skip items that already have a response and they have already been collected
                if value.response:
                    continue

                # Get the response from the user and store in a temp variable for validation
                user_response = input(f"{value.user_prompt}: ")

                # If a validation regex was provided check the response against it otherwise just add the response
                # to the form item list
                if value.regex_validation_pattern:
                    if regex_validator(user_response, value.regex_validation_pattern):
                        value.response = user_response
                    else:
                        all_items_valid = False
                        print(f"\nInvalid input provided. Please provide a valid value.")
                        wait_for_input()
                        break
                else:
                    value.response = user_response
            else:
                raise ValueError("Invalid form item provided")

        # If all items are valid return the form items
        if all_items_valid:
            print(divider)
            confirm_prompt = input("Are you sure you want to continue? (y/n) or cancel: ")
            if regex_validator(confirm_prompt, regex_patterns.REGEX_BOOL_YES):
                clear_screen()
                return form_items
            elif regex_validator(confirm_prompt, regex_patterns.REGEX_BOOL_NO):
                print("\nRestarting form...")
                form_items = copy.deepcopy(temp_form_items)
                wait_for_input()
                continue
            elif confirm_prompt.lower() == "cancel":
                return None  # Return None to indicate the form was cancelled
            else:
                print("\nInvalid input provided. Please provide a valid value.")
                wait_for_input()
                continue


def search_builder(header_name, section_name=None, search_list=None, comparator_func=None, search_prompt_text=None,
                   padding=20,center_section=False, config_section=None,additional_search_options=None,
                   use_search_results=False,results_header = "Search Results"):
    # Create the menu for the form
    menu = build_menu(header_name=header_name, section_name=section_name, description=None, padding=padding,
                      center_section=center_section, config_section=config_section)

    # Create the divider for the form formatting
    divider = build_divider(header_name, padding)

    # Create a list to store the search results
    if use_search_results:
        search_results = search_list
    else:
        search_results = []

    # Create a search term variable then if None prompt the user for the search term
    search_text = None
    if search_prompt_text is None:
        search_prompt_text = "Please enter a search term:"

    if search_text is None and len(search_results) == 0:
        clear_screen()
        print(menu)
        search_text = input(search_prompt_text)

        # Search the list for the search term and add to the search results list
        for item in search_list:
            if comparator_func:
                compare_value = comparator_func(item, search_text)
                if compare_value:
                    if isinstance(compare_value, MenuItem):
                        search_results.append(compare_value)
            else:
                raise ValueError("Invalid comparator function provided")

    # Create search info
    p = Paginator(search_results, page_size=10)

    # Loop until the user selects a valid option
    while True:

        search_menu = ""
        search_menu += "Search Info" + "\n"
        search_menu += divider

        current_page_items = p.get_current_page()

        if len(current_page_items) == 0:
            search_menu += f"Page: N/A" + "\n"
            search_menu += f"Page Items: N/A" + "\n"
        else:
            search_menu += f"Page: {p.current_page + 1} of {p.total_pages()}" + "\n"
            search_menu += f"Page Items: {p.current_range_string()}" + "\n"

        if search_text:
            search_menu += f"Search Text: {search_text}" + "\n"

        search_menu += divider
        search_menu += results_header + "\n"
        search_menu += divider

        if len(current_page_items) == 0:
            search_menu += f"No items found for search term: {search_text}" + "\n"
        else:
            for index, item in enumerate(current_page_items, 1):
                if index < 10:
                    search_menu += f"{index}.  {item.display_text}" + "\n"
                else:
                    search_menu += f"{index}. {item.display_text}" + "\n"

        search_menu += divider

        search_option_menu_items = []
        if len(current_page_items) > 0:
            search_option_menu_items.append(MenuItem("Select Item", "select"))

        search_option_menu_items.append(MenuItem("Search", "search"))


        if p.has_next_page():
            search_option_menu_items.append(MenuItem("Next Page", "next"))

        if p.has_previous_page():
            search_option_menu_items.append(MenuItem("Previous Page", "previous"))

        if additional_search_options:
            for item in additional_search_options:
                if isinstance(item, MenuItem):
                    search_option_menu_items.append(item)
                else:
                    raise ValueError("Invalid menu item provided")

        search_option_menu_items.append(MenuItem("Back", "back"))

        # This will need tobe dynamically updated based on the search results
        # Build the options menu
        options_menu = "Options" + "\n"
        options_menu += divider
        for index, item in enumerate(search_option_menu_items, 1):
            if isinstance(item, MenuItem):
                options_menu += f"{index}. {item.display_text}" + "\n"
            else:
                raise ValueError("Invalid menu item provided")

        options_menu += divider
        # Display the menu
        clear_screen()
        print(menu + search_menu + options_menu)
        if len(search_option_menu_items) == 1:
            user_choice = input(f"What would you like to do? :")
        elif len(search_option_menu_items) > 1:
            user_choice = input(f"What would you like to do? (1-{len(search_option_menu_items)}) :")
        else:
            raise ValueError("No menu items were provided")

        if user_choice.isdigit() and int(user_choice) != 0 and int(user_choice) <= len(search_option_menu_items):
            option_selection = search_option_menu_items[int(user_choice) - 1].unique_id
            if option_selection == "next":
                p.next_page()
            elif option_selection == "previous":
                p.previous_page()
            elif option_selection == "back":
                return None
            elif option_selection == "search":
                # clear the screen and print the menu
                clear_screen()
                print(menu)

                # Get the user input for the search text
                search_text = input(search_prompt_text)

                # Reset the search results
                search_results = []

                # Search the list for the search term and add to the search results list
                for item in search_list:
                    if comparator_func:
                        compare_value = comparator_func(item, search_text)
                        if compare_value:
                            if isinstance(compare_value, MenuItem):
                                search_results.append(compare_value)
                    else:
                        raise ValueError("Invalid comparator function provided")

                # Reset the results and current page in the Paginator
                p.items = search_results
                p.current_page = 0

            elif option_selection == "select":

                if len(current_page_items) == 0:
                    clear_screen()
                    print("No items to select from. Please search again.")
                    wait_for_input()
                    continue
                elif len(current_page_items) == 1:
                    return current_page_items[0].unique_id

                # Prompt the user to select an item if there is more than 1 item to choose from
                clear_screen()
                item_select_header = "Select Item" + "\n"
                item_select_header += divider
                item_select_header += (
                        "Select an item by item number from the search list \nor type 'back' to return to the search menu" + "\n")
                item_select_header += divider

                print(menu + search_menu + item_select_header)
                # Get the user input for the item to select
                item_selection = input("What item would you like to select?:")
                if item_selection == "back":
                    continue
                elif item_selection.isdigit() and int(item_selection) != 0 and int(item_selection) <= len(
                        current_page_items):
                    selected_item = current_page_items[int(item_selection) - 1]
                    return selected_item.unique_id
                else:
                    clear_screen()
                    print(f"Invalid choice. Please select a valid option between 1 and {len(current_page_items)}")
                    wait_for_input()
            elif option_selection in [item.unique_id for item in additional_search_options]:
                return option_selection
        else:
            clear_screen()
            print(f"Invalid choice. Please select a valid option between 1 and {len(search_option_menu_items)}")
            wait_for_input()


def regex_validator(value, pattern):
    return re.match(pattern, value) is not None
