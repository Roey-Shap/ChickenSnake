import metadata
from CardData import *
from Card import Card 
from UI import *
import LineSegment
import os
from ascii_art import logo_art
from UI import log_and_print

# @TODO: 
## General
# Add proper instructions for zero-to-set

## Card image generation                            
# Make gold cards still use correct color trim
  # Download all 5 color trims
  # Means we can also do this for colored artifacts
# Use flavor text - make it italicized and in a smaller font
# Make playtest art autogenerate images based on type and mana cost
# Support adding brackets around abilities that choose or span multiple lines to make them not have larger line spacings like
    # normal new lines? Can we assume that after "choose ..." there won't be any more abilities and just say that if we see
    # the phrase 'spree' or 'choose [any number/number N/one or more]' that we lock into not having anymore deliberate 
    # newline extra line spacing?

# Automatically generate and save the left/middle/right sides of the cards if they don't exist
# (Not going to support tri-color cards for now)
# Then apply those borders to the cards based on their type. The following are likely simple to start with:
# (Normal, Artifact, Vehicle, Miracle, Tokens, Enchantments, Snow)
# Border types downloaded (V by supported, X by unsupported):
# X Normal
# X Artifact
# X Vehicle
# X Arc-style tokens
# X Miracle
# X Fuse
# X Planeswalkers (3/4 ability)
# X Saga

# Border types to download in order of priority:
# Enchantments (Nyx)
# Snow
# Split
# ------
# Adventures
# Level up
# Flip (Kamigawa)
# Class
# Battle
# Cases (Karlov Manor) (How to template that...)

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
    generated_output_folder = False
    for generated_folder in [metadata.output_base_filepath, metadata.card_images_filepath]:
        output_folder_exists = os.path.exists(generated_folder)
        if not output_folder_exists:
            os.mkdir(generated_folder)
            generated_output_folder = True

    print(logo_art)
    print("\n")
    log_and_print("Welcome to ChickenSnake, for fast custom playtest cards!")
    
    generate_card_images_input: str = get_user_input(
        yes_no_input_check, 
        "Do you also want to generate default card images? (y/n) >>> >>> "
    )
    log_to_file("[User input]: " + generate_card_images_input)

    log_and_print("\nExtracting card data from input file...")
    cards_dict: dict[str, Card] = get_card_data_from_spreadsheet(metadata.card_data_filepath)

    do_generate_card_images = generate_card_images_input.lower() in ["y", "yes"]
    if do_generate_card_images:
        log_and_print("\nInitializing image creation assets...")
        image_assets = initialize_card_image_assets(metadata.card_image_creation_assets_filepath)
        
        log_and_print("\nGenerating card images...")
        generate_card_images(cards_dict, metadata.card_images_filepath, image_assets)
        
        log_and_print("\nDone!") 

    card_rarities = ["Common", "Uncommon", "Rare", "Mythic"]
    cards_by_rarity = group_cards_by_rarity(card_rarities, cards_dict)
    generate_draft_text_file(metadata.draft_text_filepath, cards_dict, 
                                            metadata.draft_pack_settings_string, 
                                            metadata.uploaded_images_base_url, 
                                            card_rarities, cards_by_rarity)
    generate_markdown_file(metadata.markdown_filepath, cards_dict, 
                           header_string, closer_string, metadata.set_code)

    log_and_print()
    log_and_print("==============")
    if do_generate_card_images:
        log_and_print("Generated card images at:")
        log_and_print(">>>   " + full_final_card_images_path)
        log_and_print()

    log_and_print("Cockatrice set file (.xml) and Drafting file (.txt) generated at:")
    log_and_print(">>>   " + full_final_markdown_images_path)
    log_and_print("This entire program output has also been printed to a log file there.")
    log_and_print("==============")


if __name__ == "__main__":
    main()
