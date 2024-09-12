import csv
from Card import Card
from PIL import Image, ImageFont, ImageDraw, ImageTk, ImageChops
from Fonts import body_text_font_name, symbols_font_name
from LineSegment import LineSegment
import Fonts
from LineSegment import hybrid_pips_with_non_wubrg_order_colors
import metadata
from UI import log_and_print
import os.path

import traceback

CARD_PICTURE_FILE_FORMAT = "jpg"

C_BLACK = (0, 0, 0)
C_WHITE = (255, 255, 255)
# card_pixel_dims = (375, 523)
card_pixel_dims = (500, 700)
max_types_string_width_ratio = 357 / 500
right_mana_border = int(card_pixel_dims[0] * 0.93)

# font_body  = ImageFont.truetype(body_text_font_name, 13)
# font_body_tiny = ImageFont.truetype(body_text_font_name, 11)
# font_body_large  = ImageFont.truetype(body_text_font_name, 15)

class CardImageInfo():
        def __init__(self, frame_supertype: str, side: str, frame_subtype: str,
                     should_be_modified=False, special_card_asset_name_mode=False) -> None:
            self.frame_supertype = frame_supertype
            self.side = side
            self.frame_subtype = frame_subtype
            self.should_be_modified = should_be_modified
            extra_underscore = "_" if len(self.side) > 0 else ""
            single_underscore = "_" if not special_card_asset_name_mode else ""
            self.file_prefix = f"{self.frame_supertype}{single_underscore}{self.side}{extra_underscore}{self.frame_subtype}"
            self.base_file_prefix = f"{self.frame_supertype}_{self.frame_subtype}"
            if not self.should_be_modified and not special_card_asset_name_mode:
                self.file_prefix = self.base_file_prefix
            self.filepath = ""

set_symbol_card_image_info = CardImageInfo("set_symbol", "", "", should_be_modified=False, special_card_asset_name_mode=True)

def get_color_string(csv_row: dict[str, str]) -> str:
    color_string = ""
    color_string += "W" if csv_row["Is White"] == "1" else ""
    color_string += "U" if csv_row["Is Blue"] == "1" else ""
    color_string += "B" if csv_row["Is Black"] == "1" else ""
    color_string += "R" if csv_row["Is Red"] == "1" else ""
    color_string += "G" if csv_row["Is Green"] == "1" else ""

    return color_string

def get_power_toughness(csv_row: dict[str, str]) -> tuple[int|str, int|str] | None:
    power_string = csv_row["Power"]
    toughness_string = csv_row["Toughness"]
    try:
        if power_string == "*":
            power = "*"
        else:
            power = int(power_string)
        
        if toughness_string == "*":
            toughness = "*"
        else:
            toughness = int(toughness_string)

        return (power, toughness)
    except:
        return None

def get_mana_cost_string(raw_mana_cost: str) -> str:
    tokens = raw_mana_cost.split('{')
    stripped = [s.removesuffix('}').upper() for s in tokens if len(s) > 0]
    hybrid = ["{" + reorder_mana_string(s) + "}" if '/' in s else s for s in stripped]
    joined = ''.join(hybrid)

    return joined

def reorder_mana_string(stripped_cost: str) -> str:
    if stripped_cost.lower() in hybrid_pips_with_non_wubrg_order_colors or "p" in stripped_cost.lower():
        first, second = stripped_cost.split('/')
        return second + '/' + first
    else:
        return stripped_cost

def get_card_data_from_spreadsheet(card_data_filepath) -> dict[str, Card]:
    cards_dict: dict[str, Card] = {}
    saw_card_with_errors = False
    with open(card_data_filepath) as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if row["Is Card"] == "1":
                name = row["Name"]
                colors = get_color_string(row)
                raw_mana_cost_string = row["Cost"]
                manacost = get_mana_cost_string(raw_mana_cost_string)
                converted_manacost = row["CMC"]
                supertype = row["Type"]
                subtype = row["Subtype"]
                rarity = row["Rarity"]

                is_rarity_missing = len(rarity) == 0
                if is_rarity_missing:
                    rarity = "c"

                stats = get_power_toughness(row)
                body_text = row["Desc"]
                flavor_text = row["Flavor Text"]

                # Replace placeholder name with card name
                if metadata.replace_reference_string_with_cardname and len(metadata.reference_card_name) > 0:
                    body_text = body_text.replace(metadata.reference_card_name, name)

                cards_dict[name] = Card(
                    name, colors, manacost, raw_mana_cost_string,
                    converted_manacost, supertype, subtype, rarity,
                    stats, body_text, flavor_text
                )

                # Card data warnings
                card_warning_messages = []
                is_creature = supertype.find("Creature") != -1
                if len(raw_mana_cost_string) == 0 and supertype.find("Land") == -1:
                    card_warning_messages.append("Missing a mana cost.")
                if len(supertype) == 0:
                    card_warning_messages.append("Missing a supertype.")
                if is_creature and len(subtype) == 0:
                    card_warning_messages.append("Missing a subtype.")
                if is_creature and stats is None:
                    card_warning_messages.append("Missing power/toughness.")
                if metadata.rarities_should_be_in_place and is_rarity_missing:
                    card_warning_messages.append("Missing rarity. Defaulting to COMMON.")
                if len(card_warning_messages) > 0:
                    if not metadata.verbose_mode_cards:
                        if not saw_card_with_errors:
                            print(">>>  You had warnings about imported card data! Check the log for more details.")
                            saw_card_with_errors = True
                    
                    log_and_print(f"Warnings for '{name}':", do_print=metadata.verbose_mode_cards)
                    for warning in card_warning_messages:
                        log_and_print(">  " + warning, do_print=metadata.verbose_mode_cards)
        if not saw_card_with_errors:
            log_and_print("No warnings about imported card data to report!", do_print=metadata.verbose_mode_cards)

    return cards_dict

def get_card_image_border_info(card_data: Card) -> list[CardImageInfo]:
    frame_supertype = "normal"
    frame_subtypes = []
    # Note that the Card's color_string is just "M" if it's gold!
    # Just to test for now...
    num_colors = len(card_data.colors_string)
    if num_colors >= 3 or card_data.colors_string.lower() == "m":
        frame_subtypes = ["m"]
    elif num_colors == 2:
        frame_subtypes = [character.lower() for character in card_data.colors_string]
    elif num_colors == 1:
        frame_subtypes = [character.lower() for character in card_data.colors_string] * 2

    if card_data.supertype.find("Artifact") != -1:
        frame_subtypes = ["artifact"]
    elif card_data.is_colorless:
        frame_subtypes = ["c"]

    # The above will bite me later if I decide to allow colored artifacts.
    # Later me problem.

    if card_data.supertype.find("Enchantment") != -1:
        frame_supertype = "enchantment"
    

    if len(frame_subtypes) > 1:
        print(frame_subtypes)
        valid_sides = ["l", "r"] if len(frame_subtypes) == 2 else ["l", "m", "r"]
        return [CardImageInfo(frame_supertype, side, frame_subtype, should_be_modified=True) for side, frame_subtype in zip(valid_sides, frame_subtypes)]
    else:
        # You have exactly 1 subtype -> we don't need to combine card frames
        return [CardImageInfo(frame_supertype, "", frame_subtypes[0], should_be_modified=False)]

def get_card_pt_image_info(card_data: Card) -> CardImageInfo:
    if card_data.is_colorless:
        frame_subtype = "c"
    elif len(card_data.colors_string) > 1:
        frame_subtype = "m"
    else:
        frame_subtype = card_data.colors_string.lower()

    if card_data.supertype.find("Artifact") != -1:
        frame_subtypes = "artifact"
    elif card_data.subtype.find("Vehicle") != -1:
        frame_subtype = "vehicle"

    return CardImageInfo("pt", "", frame_subtype, should_be_modified=False)

def generate_card_images(card_dict: dict[str, Card], images_save_filepath: str, image_assets: dict[CardImageInfo, Image]):
    num_cards_total = len(card_dict)
    current_card_index = 0

    for card_data in card_dict.values():
        try:
            card_image_total = Image.new(mode="RGB", size=card_pixel_dims, color=C_WHITE).convert("RGBA")

            # Card Base
            card_border_info: list[CardImageInfo] = get_card_image_border_info(card_data)
            for border_info in card_border_info:
                card_image_total.alpha_composite(image_assets[border_info.file_prefix])
            
            # if card_data.is_colorless:
            #     card_image_total.alpha_composite(image_assets[])
            # elif 1 <= len(card_data.colors_string) <= 2 and not card_data.is_gold:
            #     card_colors = card_data.colors_string
            #     # It's important to layer the middle part first so it can be covered up by the sides
            #     for prefix in [card_colors[-1]+"_m", card_colors[0]+"_l", card_colors[-1]+"_r"]:
            #         card_bg: Image = image_assets[prefix]
            #         card_image_total.alpha_composite(card_bg)            
            # else:
            #     card_image_total.alpha_composite(image_assets["m_"])

            if card_data.has_stats:
                card_pt_info: CardImageInfo = get_card_pt_image_info(card_data)
                card_image_total.alpha_composite(image_assets[card_pt_info.file_prefix])

            # Set Symbol
            card_image_total.alpha_composite(image_assets[set_symbol_card_image_info.file_prefix])

            # Title font config
            chosen_title_font = Fonts.font_title
            if len(card_data.name) + len(card_data.manacost) > 45:
                chosen_title_font = Fonts.font_title_small

            # Title
            ImageDraw.Draw(card_image_total).text(
                (40, 40), card_data.name, C_BLACK, font=chosen_title_font
            )

            # Mana Cost
            debug_on = False # card_data.name == "Ancient Nestite"
            mana_cost_segments: list[LineSegment] = LineSegment.split_text_for_symbols(
                card_data.raw_mana_cost_string.lower(), card_image_total, 420, 500, debug_mode=debug_on, font_override=(Fonts.font_symbols_large, Fonts.font_symbols_large_pip_bg)
            )
            
            # We assume each pip is the same width and draw them from left to right with manual offsets
            num_mana_pips = len(mana_cost_segments)
            # if debug_on:
                # log_and_print(num_mana_pips)

            if num_mana_pips > 0:
                mana_pip_width = mana_cost_segments[0].dims[0]
                margin = 0 #int(mana_pip_width * 0.1)
                left_mana_border = right_mana_border - (mana_pip_width * num_mana_pips) - (margin * (num_mana_pips-1))
                for i, segment in enumerate(mana_cost_segments):
                    segment.draw(card_image_total, (left_mana_border + ((mana_pip_width + margin) * i), 40), absolute_draw_mode=True, mana_cost_mode=True)

            # Types
            chosen_types_font = Fonts.font_types
            types_string = card_data.get_type_string()
            # Try up to five times to shrink the text based on the estimated size
            types_string_width, _ = Fonts.get_string_size(types_string, chosen_types_font)
            max_types_string_width_in_pixels = max_types_string_width_ratio * card_pixel_dims[0]
            if types_string_width > max_types_string_width_in_pixels:
                current_types_width_to_max_width_ratio = max_types_string_width_in_pixels / types_string_width
                chosen_types_font = Fonts.get_title_font(Fonts.font_types_initial_size * current_types_width_to_max_width_ratio)

            # if len(types_string) > 29:
            #     chosen_types_font = Fonts.font_types_small
            # if len(types_string) > 36:
            #     chosen_types_font = Fonts.font_types_tiny

            ImageDraw.Draw(card_image_total).text(
                (40, 413), card_data.get_type_string(), C_BLACK, font=chosen_types_font, anchor="lm"
            )

            # Body Text config
            # Go through each line of text and convert it into a series of LineSegments - each with their own font, offset, and text
            # Then draw each of their texts on the card at their offset and with their font

            segments: list[LineSegment] = LineSegment.split_text_for_symbols(
                card_data.body_text, card_image_total, 420, 500
            )

            for segment in segments:
                segment.draw(card_image_total, (44, 445))
           
            if card_data.has_stats:
                ImageDraw.Draw(card_image_total).text(
                    (433, 643), card_data.get_stats_string(), C_BLACK, Fonts.font_stats, anchor="mm"
                )
            
            rgb_image = card_image_total.convert("RGB")
            try:
                rgb_image.save(images_save_filepath + f"{card_data.name}.{CARD_PICTURE_FILE_FORMAT}", quality=100)
            except:
                raise ValueError(f"There was an issue saving the image for: {card_data.name}")

            if metadata.verbose_mode_cards:
                if current_card_index % 25 == 0:
                    log_and_print(f"Finished card {current_card_index+1}/{num_cards_total}")



            current_card_index += 1
        except Exception as e:
            log_and_print(f"There was an issue with {card_data.name}")
            log_and_print(e)
            log_and_print(traceback.format_exc())
            log_and_print()

"""
For now, this is just:
For each normal card type frame, prepare half-frames of each color and card supertype.
Save them all that the same size and the correct format for superimposing on one another.
"""
def initialize_card_image_assets(assets_filepath: str) -> dict[str, Image]:
    resized_images: dict[str, Image] = {}
    # There are certain image names we expect to see. Initialize that list first.
    # Some will be expected to have a left and right side for mixing (X/V)
    # V Normal              | WUBRGM
    # X Normal Singles      | ART, VEH, LND
    # X P/T (Normal + TOK)  | WUBRGMC, ART, VEH
    # V Enchantment         | WUBRGM
    # V Arc-style TOK       | WUBRGM
    # X Arc-style TOK Sing. | ART, VEH 
    # V Miracles            | WUBRG

    splittable_card_prefixes = ["w", "u", "b", "r", "g"]
    unsplittable_card_prefixes = ["m", "artifact", "c"]
    card_frame_type = ["normal", "enchantment"] # "token", "miracle"
    one_off_card_subtypes = ["vehicle"]

    image_prefixes  = [CardImageInfo(frame, side, color, should_be_modified=True) for frame in card_frame_type for side in ["l", "r"] for color in splittable_card_prefixes]
    image_prefixes += [CardImageInfo(frame_supertype, "", frame_subtype, should_be_modified=False) for frame_supertype in card_frame_type for frame_subtype in unsplittable_card_prefixes]
    image_prefixes += [CardImageInfo("pt", "", frame_subtype, should_be_modified=False) for frame_subtype in splittable_card_prefixes + unsplittable_card_prefixes + one_off_card_subtypes]
    image_prefixes += [set_symbol_card_image_info]

    # If the card is one that needs masking and splitting, it's marked as such 
    image_suffix: str = "_base.png"
    hybrid_card_mask_image: Image = None
    hybrid_card_masks: dict[str, Image] = {}
    try:
        # print("Accessing " + assets_filepath + "hybrid_card_mask.png")
        hybrid_card_mask_image = Image.open(assets_filepath + "hybrid_card_mask.png")
        hybrid_card_mask_image = hybrid_card_mask_image.resize(card_pixel_dims).convert("RGBA")
        hybrid_card_masks["l"] = hybrid_card_mask_image
        hybrid_card_masks["r"] = hybrid_card_mask_image.transpose(Image.FLIP_LEFT_RIGHT)
    except:
        raise ValueError("There was a problem accessing the transparency mask.")

    for prefix in image_prefixes:
        image_info: CardImageInfo = prefix
        expected_image_filepath = assets_filepath + image_info.file_prefix + image_suffix
        image_info.filepath = expected_image_filepath
        try:
            if not image_info.should_be_modified:
                # If the image isn't to be modified to generate new card borders, it should exist
                # ... and we just need to resize it and hold it in memory
                # print(f"Accessing base file {expected_image_filepath}")
                base_image: Image = Image.open(expected_image_filepath)
                resized_image: Image = base_image.resize(card_pixel_dims)
                resized_images[image_info.file_prefix] = resized_image.convert("RGBA")
            else:
                # Here the image shouldn't necessarily exist because we need to generate it.
                # We'll check if we already have:
                was_image_generated: bool = os.path.isfile(expected_image_filepath)
                base_image_filepath = assets_filepath + image_info.base_file_prefix + image_suffix
                if not was_image_generated or metadata.always_regenerate_base_card_frames:
                    log_and_print(f"To-be-generated file {expected_image_filepath} doesn't exist. Generating...", do_print=metadata.verbose_mode_files)
                    log_and_print(f"Accessing base file {base_image_filepath}", do_print=metadata.verbose_mode_files)
                    base_image = Image.open(base_image_filepath)
                    resized_image: Image = base_image.resize(card_pixel_dims)
                    masked_image = ImageChops.multiply(resized_image, hybrid_card_masks[image_info.side])
                    resized_images[image_info.file_prefix] = masked_image
                    # Save the image so we don't need to generate it next time
                    masked_image.save(expected_image_filepath, quality=100)
                else:
                    if metadata.verbose_mode_files:
                        log_and_print(f"Generated file {base_image_filepath} already exists!", do_print=metadata.verbose_mode_files)
        except:
            raise ValueError(f"There was an issue accessing image: {expected_image_filepath}.\n \
                        You may need to redownload the Playtest_Base_Images folder.")

    return resized_images

    # image_color_prefixes = [f"{color}_{side}" for side in ["l", "m", "r"] for color in "WUBRG"] + ["c_pt_", "m_", "c_", "set_symbol_"]
    # for prefix in image_color_prefixes:
    #     image_name_suffix = prefix.lower() + "base.png"
    #     image_filepath = assets_filepath + image_name_suffix
    #     try:
    #         base_image: Image = Image.open(image_filepath)
    #         resized_image: Image = base_image.resize(card_pixel_dims)
    #         resized_images[prefix] = resized_image.convert("RGBA")
    #     except:
    #         raise ValueError(f"There was an issue accessing image: {image_name_suffix}")

    return resized_images


def group_cards_by_rarity(card_rarities: list[str], cards_dict: dict[str: Card]):
    cards_by_rarity: dict[str, list[Card]] = {rarity[0].lower(): [] for rarity in card_rarities}
    for card in cards_dict.values():
        try:
            cards_by_rarity[card.rarity].append(card)
        except:
            raise ValueError(f"{card.name} didn't have a rarity and couldn't be sorted.")
            
    return cards_by_rarity

def generate_markdown_file(markdown_filepath: str, 
                           cards_dict: dict[str: Card],
                           header_string: str,
                           closer_string: str,
                           set_code: str):
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

def generate_draft_text_file(draft_text_filepath: str,
                             cards_dict: dict[str, Card],
                             draft_pack_settings_string: str,
                             uploaded_images_base_url: str,
                             card_rarities: list[str],
                             cards_by_rarity: dict[str: list[Card]]):
    with open(draft_text_filepath, 'w') as draft_text_file:
        # Write custom pack settings
        draft_text_file.write(draft_pack_settings_string)

        # Declaring custom cards
        draft_text_file.write("[CustomCards]\n[")        

        num_cards_total = len(cards_dict)

        for i, card in enumerate(cards_dict.values()):
            draft_text_file.write(card.get_draft_text_rep(uploaded_images_base_url, CARD_PICTURE_FILE_FORMAT))
            if i < num_cards_total - 1:
                draft_text_file.write(",")
        draft_text_file.write("\n]\n")

        # Writing in cards sorted by rarity
        for rarity in card_rarities:
            draft_text_file.write("[" + rarity + "]\n")
            rarity_code: str = rarity[0].lower()
            for card in cards_by_rarity[rarity_code]:
                draft_text_file.write(card.name + "\n")

