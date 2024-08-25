# import sys
# print(sys.executable)
from CardData import *
from Card import Card 
from UI import *
import LineSegment

# test_text = "This is some test text. {t}, do a thing, add {r}{r}."
# print(LineSegment.LineSegment.split_text_for_symbols(test_text))

# @TODO: 
# Get version number from the spreadsheet
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

closer_string = \
f"""
</cards>
</cockatrice_carddatabase>
"""

def main():
    print("Welcome to ChickenSnake!")
    do_generate_card_images: bool = get_user_input(yes_no_input_check, "In addition to generating a markdown file, do you want to generate default card images? (y/n)\n")
    cards_dict: dict[str, Card] = get_card_data_from_spreadsheet(card_data_filepath)
    num_cards_total = len(cards_dict)

    if do_generate_card_images.lower() in ["y", "yes"]:
        print("Initializing image creation assets...")
        image_assets = initialize_card_image_assets(card_image_creation_assets_filepath)
        print("Generating card images at:")
        print(card_images_filepath)
        print(".....")
        generate_card_images(cards_dict, card_images_filepath, image_assets)
        print("Done!")

    with open(draft_text_filepath, 'w') as draft_text_file:
        draft_text_file.write("[CustomCards]\n[")
        for i, card in enumerate(cards_dict.values()):
            draft_text_file.write(card.get_draft_text_rep(uploaded_images_base_url, CARD_PICTURE_FILE_FORMAT))
            if i < num_cards_total - 1:
                draft_text_file.write(",")
            # single_line_text_file.write(card.name)
            # single_line_text_file.write('\n')
        draft_text_file.write("]\n")
        draft_text_file.write("[MainSlot(15)]\n")
        for card in cards_dict.values():
            draft_text_file.write(f"2 {card.name}\n")

    with open(markdown_filepath, 'w') as markdown_file:
        markdown_file.write(header_string)
        for card in cards_dict.values():
            markdown_file.write(
f"""
<card>
    <name>{card.name}</name>
    <set picURL="{f"/{card.name}.full.{CARD_PICTURE_FILE_FORMAT}"}" picURLHq="" picURLSt="">{set_code}</set>
    <color>{card.colors}</color>
    <manacost>{card.manacost}</manacost>
    <type>{card.get_type_string()}</type>{"" if card.stats is None else f"{chr(10) + chr(9)}<pt>{card.stats[0]}/{card.stats[1]}</pt>"}
    <tablerow>0</tablerow>
    <text>{card.body_text}</text>
</card>
"""
    )

        markdown_file.write(closer_string)
        
if __name__ == "__main__":
    main()