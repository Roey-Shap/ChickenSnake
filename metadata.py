
###################################################################
# Welcome to the metadata! (They're like settings. But fancier!)
# Confused on how to use these? the README.md file might help!
###################################################################

# File locations and names
base_filepath = ".\\DoD3\\"
output_folder_name = "output"
spreadsheet_file_name = "MtG DoD Custom - Cards.csv"
uploaded_images_base_url = "https://roey-shap.github.io/ChickenSnake/DoD3/Playtest_Images/"
set_code = "DoD"
set_longname = "DoD3"
set_version_code = "1_0_1"
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
make_unique_program_run_log = True
# Set to True if you want the program to always regenerate the hybrid colors
# and other card frames from the few base frames you have be default 
always_regenerate_base_card_frames = False

# Give updates about card errors and file accesses as the program runs.
verbose_mode_cards = True
verbose_mode_files = False
# @TODO: Doesn't currently do anything. Should warn about things like mana symbols being out of order and corrected. 
# Maybe also templating issues?
warn_about_card_semantics_errors = True

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
card_data_filepath = base_filepath + spreadsheet_file_name
card_images_filepath = output_base_filepath + "Playtest_Images\\"
card_image_creation_assets_filepath = base_filepath + "Playtest_Base_Images\\"
text_files_base_name = f"{set_longname}_{set_version_code}"
log_filepath = output_base_filepath + "log_chickensnake.txt"
# For Cockatrice
markdown_filepath = output_base_filepath + f"{text_files_base_name}.xml"
# For Draftmancer
draft_text_filepath = output_base_filepath + f"{text_files_base_name}.txt"
current_execution_log_filepath = log_filepath
####################
