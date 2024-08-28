# import sys
# print(sys.executable)
from CardData import *
from Card import Card 
from UI import *
import LineSegment


# @TODO: 
# Make rarity consideration in text file
# Assign rarities to current cards
# Check that get_stats_string still works in the correct context with the use of get_draft_text_rep
# Check Slow-moving projectile
# Split header stringgs and general file-writing data into a separate file
# Make it so user can change the set name and csv name and such
# Make playtest art autogenerate images based on type and mana cost
base_filepath = ".\\DoD3\\"
markdown_filepath = base_filepath + "DoD3.xml"
card_data_filepath = base_filepath + "MtG Concept Set DoD 3.0 - Cards.csv"
card_images_filepath = base_filepath + "\\Playtest_Images\\"
card_image_creation_assets_filepath = base_filepath + "Playtest_Base_Images\\"
draft_text_filepath = base_filepath + "DoD3.txt"
uploaded_images_base_url = "https://roey-shap.github.io/ChickenSnake/DoD3/Playtest_Images/"
set_code = "DoD"
header_string = \
f"""<?xml version="1.0" encoding="UTF-8"?>
<cockatrice_carddatabase version="3">
<sets>
<set>
<name>{set_code}</name>
<longname>DoD3</longname>
<releasedate>2024-08-04</releasedate>
<settype>Custom</settype>
</set>
</sets>
<cards>
"""
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

closer_string = \
f"""
</cards>
</cockatrice_carddatabase>
"""

def main():
    print("Welcome to ChickenSnake!")
    do_generate_card_images: bool = get_user_input(
        yes_no_input_check, 
        "In addition to generating a markdown file, do you want to generate default card images? (y/n)\n"
    )
    cards_dict: dict[str, Card] = get_card_data_from_spreadsheet(card_data_filepath)

    if do_generate_card_images.lower() in ["y", "yes"]:
        print("Initializing image creation assets...")
        image_assets = initialize_card_image_assets(card_image_creation_assets_filepath)
        print("Generating card images at:")
        print(card_images_filepath)
        print(".....")
        generate_card_images(cards_dict, card_images_filepath, image_assets)
        print("Done!")
    
    card_rarities = ["Common", "Uncommon", "Rare", "Mythic"]
    cards_by_rarity = group_cards_by_rarity(card_rarities, cards_dict)
    generate_draft_text_file(draft_text_filepath, cards_dict, draft_pack_settings_string, uploaded_images_base_url, card_rarities, cards_by_rarity)
    generate_markdown_file(markdown_filepath, cards_dict, header_string, closer_string, set_code)


        
if __name__ == "__main__":
    main()


