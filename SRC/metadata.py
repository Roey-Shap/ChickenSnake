from datetime import datetime
import os
import UI
import json
import json_minify

###################################################################
# Welcome to the metadata! (They're like settings. But fancier!)
# Confused on how to use these? The README.md file might help!
###################################################################

# File locations and names
settings_data_obj = {
    "file_settings": {
        "output_filepath": ".\\Outputs\\",
        "input_filepath": ".\\Inputs\\",
        "spreadsheet_file_name": "Cards.csv",
        "uploaded_images_base_url": "https://roey-shap.github.io/MtGDoD3/",
        # "use_custom_draftmancer_link": False,
        "set_code": "SET",
        "set_longname": "SetLongName",
        "set_version_code": "1_0",  # MUST BE IN XX_XX format! Not more than 1 underscore!
        "release_date": "2024-09-08",
    },
    "card_image_settings": {
        "card_line_height_between_abilities": 1.4,
        "card_line_height_normal": 1.035,
        "generate_random_card_art": True,
    },
    "card_semantics_settings":
    {
        # It's typical to see a special placeholder name in test cards where one hasn't been decided yet.
        # The one I always see is tilde (~). Another common one is CARDNAME. Chose whatever you'd like!
        "replace_reference_string_with_cardname": True,
        "reference_card_name":  "~",
        "shortened_reference_card_name_when_able": True,

        "italics_toggle_character": "@",
        
        # If you didn't have time to do rarities, just set this to False and you won't be warned about it!
        "rarities_should_be_in_place": True,
        "verbose_mode_cards": False,
        "verbose_mode_files": False,
        "warn_about_card_semantics_errors": True
    },
    "asset_loading_settings":
    {
        # Set to true if you want a new log each time you run the program...
        # ... so you can keep track of errors you've fixed over time.
        "make_unique_program_run_log": False,
        # Set to true if you want the program to always regenerate the hybrid color borders
        # and other card frames from the few base frames 
        "always_regenerate_base_card_frames": False
    }
}

# Determines how often certain pack types appear in Draftmancer's drafts. 
# This is a typical distribution for MtG packs in the wild.
draft_pack_settings_string = \
f"""
[Settings]
{{
    "layouts": {{
        "Rare": {{
            "weight": 7,
            "slots": {{
                "Common": 10,
                "Uncommon": 3,
                "Rare": 1
            }}
        }},
        "Mythic": {{
            "weight": 1,
            "slots": {{
                "Common": 10,
                "Uncommon": 3,
                "Mythic": 1
            }}
        }}
    }}
}}
"""

KEYWORDS_DICT: dict[str: list[str]] = {}
KEYWORDS_REGEX_OR_STRING: str = ""

def update_final_configuration_settings(settings_data_local):
    file_settings = settings_data_local["file_settings"]
    set_name_prefix = file_settings['set_longname'].lower()
    output_base_filepath = f"{file_settings['output_filepath']}{set_name_prefix}\\"
    text_files_base_name = f"{file_settings['set_longname']}_{file_settings['set_version_code']}"
    card_image_subfolder_suffix = "Playtest_Card_Images"
    settings_preset = {
        "output_base_filepath": output_base_filepath,
        "card_data_filepath": file_settings["input_filepath"] + file_settings["spreadsheet_file_name"],
        "card_images_filepath": f"{output_base_filepath}{card_image_subfolder_suffix}\\",
        # "token_images_filepath": output_base_filepath + f"Playtest_Token_Images_{file_settings['set_longname']}\\",
        "card_image_creation_assets_filepath": ".\\Playtest_Base_Images\\",
        "card_image_creation_assets_generated_filepath": ".\\Playtest_Base_Images_Generated\\",
        "text_files_base_name": text_files_base_name,
        "log_filepath": output_base_filepath + "log_chickensnake.txt",
        "card_images_url_final_base": f"{file_settings['uploaded_images_base_url']}{set_name_prefix}/{card_image_subfolder_suffix}/",
        # For Cockatrice
        "markdown_cards_filepath": f"{output_base_filepath}{text_files_base_name}_cards.xml",
        "markdown_tokens_filepath": f"{output_base_filepath}{text_files_base_name}_tokens.xml",
        "cockatrice_card_images_url": f"{file_settings['uploaded_images_base_url']}!setname_lower!/{card_image_subfolder_suffix}/!name!.jpg",
        # For Draftmancer
        "draft_text_filepath": output_base_filepath + f"{text_files_base_name}.txt",
    }
        
    settings_preset["current_execution_log_filepath"] = settings_preset["log_filepath"]   

    return settings_preset

def get_keywords_from_file():
    keywords_object_local = None
    with open('./Keywords.json') as keywords_file:
        raw_json_string = "".join(keywords_file.readlines())
        minified = json_minify.json_minify(raw_json_string)
        keywords_object_local = json.loads(minified)

    if keywords_object_local is None:
        raise FileNotFoundError("**WARNING: Your keywords file is missing. Keyword highlighting won't work properly. Please redownload the files.**")

    KEYWORDS_DICT = keywords_object_local["data"]
    global KEYWORDS_REGEX_OR_STRING
    KEYWORDS_REGEX_OR_STRING = "|".join(KEYWORDS_DICT["abilityWords"])    

# Use the default settings to build the final configuration initially
settings_final_configs = update_final_configuration_settings(settings_data_obj)
# print(settings_final_configs)

def get_current_execution_log_filepath() -> str:
    current_execution_log_filepath = settings_final_configs["current_execution_log_filepath"]
    return current_execution_log_filepath

def get_user_settings():
    # we begin by grabbing the user's settings from the JSON file
    settings_object_local = None
    with open('./settings.json', 'r') as settings_file:
        raw_json_string = "".join(settings_file.readlines())
        minified = json_minify.json_minify(raw_json_string)
        settings_object_local = json.loads(minified)

    if settings_object_local is None:
        print("**WARNING: Your settings file is missing! Using defaults.**")
    else:
        def recursive_dict_copy(d1, d_dest):
            for key, value in d1.items():
                if type(value) is dict and key in d_dest:
                    recursive_dict_copy(value, d_dest[key])
                else:
                    d_dest[key] = value
        # print(settings_data_obj)        
        recursive_dict_copy(settings_object_local, settings_data_obj)
        # print()
        # print(settings_data_obj)

        settings_final_configs = update_final_configuration_settings(settings_data_obj)
        # print("CURRENT SETTINGS")
        # print(settings_final_configs)

    if settings_data_obj["asset_loading_settings"]["make_unique_program_run_log"]:
        current_execution_log_filepath = settings_final_configs["current_execution_log_filepath"] 
        settings_final_configs["current_execution_log_filepath"] = \
            current_execution_log_filepath.removesuffix(".txt") + datetime.now().strftime("_%d_%m_%y_%H_%M_%S.txt")
        
    return settings_final_configs

def initialize_metadata() -> bool:
    # then we generate any missing directories or files
    generated_output_folder = False
    
    if not os.path.exists(settings_final_configs["card_data_filepath"]):
        raise ValueError("Error: Card spreadsheet filepath doesn't exist. Check spreadsheet and input folder names.")

    for generated_folder in [settings_final_configs["output_base_filepath"],
                             settings_final_configs["card_image_creation_assets_generated_filepath"], 
                             settings_final_configs["card_images_filepath"], 
                             ]:
        output_folder_exists = os.path.exists(generated_folder)
        if not output_folder_exists:
            os.mkdir(generated_folder)
            generated_output_folder = True


    # finally we tend to generating and setting up the log file for this execution
    current_execution_log_filepath = get_current_execution_log_filepath()
    # Override previous contents of the file and log some initial data
    # we do this open to override the existing path 
    with open(current_execution_log_filepath, 'w+'):	
        datetime_string = datetime.now().strftime("%B %d, %Y at %H:%M")
        UI.log_to_file(datetime_string)    

    return generated_output_folder
####################
