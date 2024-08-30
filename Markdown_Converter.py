import metadata
from CardData import *
from Card import Card 
from UI import *
import LineSegment
import os

# @TODO: 
# Assign rarities to current cards
# Check that get_stats_string still works in the correct context with the use of get_draft_text_rep
# Check Slow-moving projectile
# Add set symbol to each card
# Use flavor text
# Use area-calculation of text to adjust text size
# Add spaces between deliberate newlines in cards
# Make playtest art autogenerate images based on type and mana cost


full_final_card_images_path = os.path.abspath(metadata.card_images_filepath)
full_final_markdown_images_path = os.path.abspath(metadata.output_base_filepath)

header_string = \
f"""<?xml version="{metadata.set_version_code}" encoding="UTF-8"?>
<cockatrice_carddatabase version="3">
<sets>
<set>
<name>{metadata.set_code}</name>
<longname>{metadata.set_longname}</longname>
<releasedate>{metadata.release_date}</releasedate>
<settype>Custom</settype>
</set>
</sets>
<cards>
"""

closer_string = \
f"""
</cards>
</cockatrice_carddatabase>
"""

def main():
    print("Welcome to ChickenSnake!")
    for generated_folder in [metadata.output_base_filepath, metadata.card_images_filepath]:
        output_folder_exists = os.path.exists(generated_folder)
        if not output_folder_exists:
            os.mkdir(generated_folder)

    
    generate_card_images_input: str = get_user_input(
        yes_no_input_check, 
        "In addition to generating a markdown file, do you want to generate default card images? (y/n)\n"
    )
    cards_dict: dict[str, Card] = get_card_data_from_spreadsheet(metadata.card_data_filepath)

    do_generate_card_images = generate_card_images_input.lower() in ["y", "yes"]
    if do_generate_card_images:
        print("Initializing image creation assets...")
        image_assets = initialize_card_image_assets(metadata.card_image_creation_assets_filepath)
        
        print("\nGenerating card images...")
        generate_card_images(cards_dict, metadata.card_images_filepath, image_assets)
        
        print("\nDone!") 

    card_rarities = ["Common", "Uncommon", "Rare", "Mythic"]
    cards_by_rarity = group_cards_by_rarity(card_rarities, cards_dict)
    generate_draft_text_file(metadata.draft_text_filepath, cards_dict, 
                                            metadata.draft_pack_settings_string, 
                                            metadata.uploaded_images_base_url, 
                                            card_rarities, cards_by_rarity)
    generate_markdown_file(metadata.markdown_filepath, cards_dict, 
                           header_string, closer_string, metadata.set_code)

    print()
    print("==============")
    if do_generate_card_images:
        print("Generated card images at:")
        print(">>>   " + full_final_card_images_path)
        print()

    print("Cockatrice set file (.xml) and Drafting file (.txt) generated at:")
    print(">>>   " + full_final_markdown_images_path)
    print("==============")

if __name__ == "__main__":
    main()
