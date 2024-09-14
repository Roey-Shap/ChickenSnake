from datetime import datetime
import os
import UI

###################################################################
# Welcome to the metadata! (They're like settings. But fancier!)
# Confused on how to use these? The README.md file might help!
###################################################################

# File locations and names
base_filepath = ".\\DoD3\\"
output_folder_name = "output"
spreadsheet_file_name = "MtG DoD Custom - Cards.csv"
uploaded_images_base_url = "https://roey-shap.github.io/ChickenSnake/DoD3/output/Playtest_Images/"
set_code = "DOD"
set_longname = "DoD3"
set_version_code = "1_0"  # MUST BE IN XX_XX format! Not more than 1 underscore!
release_date = "2024-09-08"


### Settings ###
# Card Image Visuals
card_line_height_between_abilities = 1.4
card_line_height_normal = 1.035

# @TODO: Doesn't currently do anything
# It's typical to see a special placeholder name in test cards where one hasn't been decided yet.
# The one I always see is tilde (~). Another common one is CARDNAME. Chose whatever you'd like!
replace_reference_string_with_cardname = True
reference_card_name =  "~"
# If you didn't have time to do rarities, just set this to False and you won't be warned about it!
rarities_should_be_in_place = True


# Asset loading 
# Set to True if you want a new log each time you run the program. 
# ... if you want to can keep track of errors you've fixed over time.
make_unique_program_run_log = False
# Set to True if you want the program to always regenerate the hybrid colors
# and other card frames from the few base frames you have be default 
always_regenerate_base_card_frames = False

# Give updates about card errors and file accesses as the program runs.
verbose_mode_cards = False
verbose_mode_files = False
# @TODO: Should warn about things like mana symbols being out of order and corrected. 
# Maybe also templating issues?
warn_about_card_semantics_errors = False

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

####################
### PRESET ZONE ###
# You probably won't want (or need) to touch these.
output_base_filepath = base_filepath + output_folder_name + "\\"
input_folder_name = "Inputs\\"
card_data_filepath = ".\\" + input_folder_name + spreadsheet_file_name
card_images_filepath = output_base_filepath + "Playtest_Card_Images\\"
token_images_filepath = output_base_filepath + "Playtest_Token_Images\\"
card_image_creation_assets_filepath = ".\\Playtest_Base_Images\\"
card_image_creation_assets_generated_filepath = ".\\Playtest_Base_Images_Generated\\"
text_files_base_name = f"{set_longname}_{set_version_code}"
log_filepath = output_base_filepath + "log_chickensnake.txt"

# For Cockatrice
markdown_cards_filepath = output_base_filepath + f"{text_files_base_name}_cards.xml"
markdown_tokens_filepath = output_base_filepath + f"{text_files_base_name}_tokens.xml"
# For Draftmancer
draft_text_filepath = output_base_filepath + f"{text_files_base_name}.txt"
current_execution_log_filepath = log_filepath

def do_log_file_init() -> bool:
    generated_output_folder = False
    for generated_folder in [base_filepath,
                             output_base_filepath,
                             card_image_creation_assets_generated_filepath, 
                             card_images_filepath, 
                             token_images_filepath,
                             ]:
        # print(generated_folder)
        output_folder_exists = os.path.exists(generated_folder)
        if not output_folder_exists:
            os.mkdir(generated_folder)
            generated_output_folder = True

    # Override previous contents of the file and log some initial data
    current_execution_log_filepath: str = log_filepath
    if make_unique_program_run_log:
        current_execution_log_filepath = current_execution_log_filepath.removesuffix(".txt") + \
                    datetime.now().strftime("_%d_%m_%y_%H_%M_%S.txt")

    current_execution_log_filepath = current_execution_log_filepath

    with open(current_execution_log_filepath, 'w+'):	
        datetime_string = datetime.now().strftime("%B %d, %Y at %H:%M")
        UI.log_to_file(datetime_string)    

    return generated_output_folder
####################
