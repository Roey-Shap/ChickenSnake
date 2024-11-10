import os
import time

import metadata
from CardData import *
from Card import Card 
from UI import *
import LineSegment

from ascii_art import logo_art
from UI import log_and_print

# @TODO:
# Right now:
############


# Updating spreadsheet to have Adventure-related cards point back to the original card
    # So then you could have double-faced adventures, for example:
    # A is a creature with an adventure (and is this marked as an adventure base), B. B points to A in its related cards.
    # A also has an alternate side, C, which also has an adventure, D. 
    # C points to A as well and is marked as a backface and an adventure base. D points to C.
    # Double-faced tokens are supported this way as well:
        # Suppose A is a card that refers to token T. T is marked as a token and points to A.
        # S is the backface of T; it's marked as a backface and a token and points to T.
# Support most common other card types:
    # Planeswalker, Saga, Fuse/Split
# Italics:
    # Flavor text:
        # Make space for it on the card
    # Other ideas:
        # Words to automatically include reminder text for (is that feasible? Where should it go? Always at the end of the paragraph?)
# Images:
    # Make playtest art autogenerate images based on type and mana cost
    # But also allow images to be pulled from for specific cards
# Specific color trim

# Support adding brackets around abilities that choose or span multiple lines to make them not have larger line spacings like
    # normal new lines? Seems like they actually just get normal newlines on official MtG cards.

# Other border types
# Snow
# ------
# Level up
# Flip (Kamigawa)
# Class
# Cases (Karlov Manor)


def main():
    try:
        metadata.settings_final_configs = metadata.get_user_settings()
        generated_a_missing_folder: bool = metadata.initialize_metadata()

        full_final_card_images_path = os.path.abspath(metadata.settings_final_configs["card_images_filepath"])
        full_final_markdown_images_path = os.path.abspath(metadata.settings_final_configs["output_base_filepath"])

        metadata_set_code = metadata.settings_data_obj["file_settings"]["set_code"]
        adjusted_version_code = metadata.settings_data_obj["file_settings"]["set_version_code"].replace("_", ".")

        header_string, header_string_tokens = get_markdown_file_header_strings(
                        adjusted_version_code,
                        metadata_set_code,
                        metadata.settings_data_obj["file_settings"]["set_longname"],
                        metadata.settings_data_obj["file_settings"]["release_date"]
                        )

        # Intro to user
        print(logo_art)
        print("\n")
        log_and_print("Welcome to ChickenSnake, for fast custom playtest cards!")
        
        # Prompt user to generate card images
        generate_card_images_input: str = get_user_input(
            yes_no_input_check, 
            "Do you also want to generate playtest card images? >-  (y/n)  -----> "
        )
        log_to_file("[User input]: " + generate_card_images_input)
        start_time = time.time()

        log_and_print("\nExtracting card data from input file...")
        cards_dict: dict[str, Card] = get_card_data_from_spreadsheet(metadata.settings_final_configs["card_data_filepath"])

        log_and_print("\nExtracting keyword data from keywords JSON file...")
        metadata.get_keywords_from_file()

        user_requested_card_images = generate_card_images_input.lower() in ["y", "yes"]
        if user_requested_card_images:
            log_and_print("Initializing image creation assets...")
            image_assets = initialize_card_image_assets({
                        "pre-set": metadata.settings_final_configs["card_image_creation_assets_filepath"],
                        "generated": metadata.settings_final_configs["card_image_creation_assets_generated_filepath"]
                        })
            
            log_and_print("Generating card images...")
            generate_card_images(cards_dict,
                                metadata.settings_final_configs["card_images_filepath"], 
                                image_assets)
            
            log_and_print(f"\nDone! In %.2f seconds." % (time.time() - start_time))

        card_rarities = ["Common", "Uncommon", "Rare", "Mythic"]
        cards_by_rarity = group_cards_by_rarity(card_rarities, cards_dict)
        generate_draft_text_file(metadata.settings_final_configs["draft_text_filepath"], cards_dict, 
                                 metadata.draft_pack_settings_string, 
                                 metadata.settings_final_configs["card_images_url_final_base"], 
                                 card_rarities, cards_by_rarity)
        generate_markdown_file({"normal": metadata.settings_final_configs["markdown_cards_filepath"], 
                                "token": metadata.settings_final_configs["markdown_tokens_filepath"]}, 
                                cards_dict, 
                                {"normal": header_string, "token": header_string_tokens}, 
                                {"normal": markdown_closer_string_normal, "token": markdown_closer_string_tokens}, 
                                metadata.settings_data_obj["file_settings"]["set_code"])

        log_and_print()
        log_and_print()
        if user_requested_card_images:
            log_and_print("Generated card images at:")
            log_and_print("      " + full_final_card_images_path)
            log_and_print()

        log_and_print("Cockatrice set files (.xml) and Drafting file (.txt) generated at:")
        log_and_print("      " + full_final_markdown_images_path)
        log_and_print("\nCopy and paste this URL as a 'Card Source' in Cockatrice to download your images on the fly:")
        log_and_print("      " + metadata.settings_final_configs["cockatrice_card_images_url"])
        log_and_print("\nThis entire program output has also been printed to a log file there.")
        log_and_print()
    except Exception as e:
        equals_str = "============================================="
        print(equals_str)
        print(traceback.format_exc())
        print(equals_str)
        print("\n")
        print(e)
        print("\n")

    _ = input("Press any key then enter to close this window.")


if __name__ == "__main__":
    main()
