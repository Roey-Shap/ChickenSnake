import csv
from Card import Card
from PIL import Image, ImageFont, ImageDraw, ImageTk, ImageChops
from Fonts import body_text_font_name, symbols_font_name
from LineSegment import LineSegment, hybrid_pips_with_non_wubrg_order_colors
import Fonts
import metadata
from UI import log_and_print
import os.path
import math_utils

import traceback

CARD_PICTURE_FILE_FORMAT = "jpg"

C_BLACK = (0, 0, 0)
C_WHITE = (255, 255, 255)
token_yoffset = 59
# card_pixel_dims = (375, 523)
card_pixel_dims = (500, 700)
max_types_string_width_ratio = 357 / 500
max_title_and_manacost_string_width_ratio = 415 / 500
right_mana_border = int(card_pixel_dims[0] * 0.93)

# font_body  = ImageFont.truetype(body_text_font_name, 13)
# font_body_tiny = ImageFont.truetype(body_text_font_name, 11)
# font_body_large  = ImageFont.truetype(body_text_font_name, 15)

class CardImageInfo():
        def __init__(self, frame_supertype: str, side: str, frame_subtype: str,
                     should_be_modified=False, special_card_asset_name_mode=False,
                     special_card_modifier="") -> None:
            self.frame_supertype = frame_supertype
            self.side = side
            self.frame_subtype = frame_subtype
            self.should_be_modified = should_be_modified
            extra_underscore = "_" if len(self.side) > 0 else ""
            single_underscore = "_" if not special_card_asset_name_mode else ""
            self.file_prefix = f"{self.frame_supertype}{single_underscore}{self.side}{extra_underscore}{self.frame_subtype}"
            self.base_file_prefix = f"{self.frame_supertype}_{self.frame_subtype}"
            if special_card_modifier:
                self.file_prefix = special_card_modifier + "_" + self.file_prefix
                self.base_file_prefix = special_card_modifier + "_" + self.base_file_prefix
                # self.file_prefix = special_card_modifier + "_" + self.file_prefix

            if not self.should_be_modified and not special_card_asset_name_mode:
                self.file_prefix = self.base_file_prefix
            
            self.filepath = ""

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
    verbose_mode_cards = metadata.settings_data_obj["card_semantics_settings"]["verbose_mode_cards"]

    cards_dict: dict[str, Card] = {}
    with open(card_data_filepath) as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            is_valid_nontoken_card = row["Is Card"] == "1"
            is_valid_card: bool = is_valid_nontoken_card or row["Is Token"] == "TRUE"
            if is_valid_card:
                name = row["Name"]
                colors = get_color_string(row)
                raw_mana_cost_string = row["Cost"]
                manacost = get_mana_cost_string(raw_mana_cost_string)
                converted_manacost = row["CMC"]
                supertype = row["Type"]
                subtype = row["Subtype"]
                rarity = row["Rarity"]
                is_token = row["Is Token"]

                stats = get_power_toughness(row)
                body_text = row["Desc"]
                flavor_text = row["Flavor Text"]
                related_card_names = row["Related Cards"].split(",")
                related_card_names = [name.strip() for name in related_card_names]

                # Replace placeholder name with card name
                semantics_settings = metadata.settings_data_obj["card_semantics_settings"]
                if semantics_settings["replace_reference_string_with_cardname"] and len(semantics_settings["reference_card_name"]) > 0:
                    body_text = body_text.replace(semantics_settings["reference_card_name"], name)

                loaded_card = Card(
                    name, colors, manacost, raw_mana_cost_string,
                    converted_manacost, supertype, subtype, rarity,
                    stats, body_text, flavor_text, is_token=="TRUE"
                )
                
                for related_name in related_card_names:
                    loaded_card.set_related_card_name(related_name)
                cards_dict[name] = loaded_card

    # Card data warnings
    saw_card_with_errors: bool = False
    card: Card
    for card in cards_dict.values():
        card_warning_messages = []
        is_creature = card.supertype.find("Creature") != -1
        if len(card.raw_mana_cost_string) == 0 and card.supertype.find("Land") == -1 and not card.is_token:
            card_warning_messages.append("Missing a mana cost.")
        if card.found_manacost_error and metadata.settings_data_obj["card_semantics_settings"]["warn_about_card_semantics_errors"]:
            card_warning_messages.append("Had a manacost pip-order error:")
            for pip in card.corrected_pips:
                card_warning_messages.append(f"   Correcting manacost hybrid pip order: {pip} -> {pip[::-1]}")
        if len(card.supertype) == 0:
            card_warning_messages.append("Missing a supertype.")
        if is_creature and len(card.subtype) == 0:
            card_warning_messages.append("Missing a subtype.")
        if is_creature and card.stats is None:
            card_warning_messages.append("Missing power/toughness.")
        if metadata.settings_data_obj["card_semantics_settings"]["rarities_should_be_in_place"] and card.is_rarity_missing and not card.is_token:
            card_warning_messages.append("Missing rarity. Defaulting to COMMON.")
        
        non_existing_related_cards: list[str] = []
        for related_card_name in card.related_card_names:
            if not related_card_name:
                continue
            if related_card_name.lower() not in [key.lower() for key in cards_dict]:
                non_existing_related_cards.append(related_card_name)
                
        if len(non_existing_related_cards) > 0:
            newline_string = ",\n   "
            card_warning_messages.append(f"There were cards you marked as related to this one that aren't in your database: \n   {newline_string.join(non_existing_related_cards)}")
        
        if len(card_warning_messages) > 0:
            if not verbose_mode_cards:
                if not saw_card_with_errors:
                    print(">>>  You had warnings about imported card data! Check the log for more details.")
                    saw_card_with_errors = True
            
            log_and_print(f"Warnings for '{card.name}':", do_print=verbose_mode_cards)
            for warning in card_warning_messages:
                log_and_print(">  " + warning, do_print=verbose_mode_cards)

    if not saw_card_with_errors:
        log_and_print("No warnings about imported card data to report!", do_print=verbose_mode_cards)


    return cards_dict

def get_card_image_border_info(card_data: Card) -> list[CardImageInfo]:
    frame_supertype = "normal"
    frame_subtypes = []
    frame_modifier = "token" if card_data.is_token else ""
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
        # print(frame_subtypes)
        valid_sides = ["l", "r"] if len(frame_subtypes) == 2 else ["l", "m", "r"]
        return [CardImageInfo(frame_supertype, side, frame_subtype, should_be_modified=True, special_card_modifier=frame_modifier) for side, frame_subtype in zip(valid_sides, frame_subtypes)]
    else:
        # You have exactly 1 subtype -> we don't need to combine card frames
        return [CardImageInfo(frame_supertype, "", frame_subtypes[0], should_be_modified=False, special_card_modifier=frame_modifier)]

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

def get_card_set_symbol_info(card_data: Card) -> CardImageInfo:
    return CardImageInfo(f"set_symbol_{card_data.rarity_name}", "", "", should_be_modified=False, special_card_asset_name_mode=True)

def generate_card_images(card_dict: dict[str, Card], images_save_filepath: dict[str, str], image_assets: dict[CardImageInfo, Image]):
    verbose_mode_cards = metadata.settings_data_obj["card_semantics_settings"]["verbose_mode_cards"]
    warn_about_card_semantics_errors = metadata.settings_data_obj["card_semantics_settings"]["warn_about_card_semantics_errors"]

    num_cards_total = len(card_dict)
    current_card_index = 0

    for card_data in card_dict.values():
        try:
            card_image_total = Image.new(mode="RGB", size=card_pixel_dims, color=C_WHITE).convert("RGBA")

            # Card Base
            card_border_info: list[CardImageInfo] = get_card_image_border_info(card_data)
            for border_info in card_border_info:
                card_image_total.alpha_composite(image_assets[border_info.file_prefix])

            # Power/Toughness
            if card_data.has_stats:
                card_image_total.alpha_composite(image_assets[get_card_pt_image_info(card_data).file_prefix])

            # Set Symbol
            card_image_total.alpha_composite(image_assets[get_card_set_symbol_info(card_data).file_prefix],
                                            dest=(0, token_yoffset if card_data.is_token else 0))

            # Name and Manacost #################################################
            chosen_title_font = Fonts.font_title
            chosen_manacost_font = Fonts.font_symbols_large
            chosen_manacost_bg_font = Fonts.font_symbols_large_pip_bg
            # Try a few times to shrink the text based on the estimated size

            # Mana Cost
            debug_on = False # card_data.name == "Ancient Nestite"
            # First find the mana cost's width at the current font
            mana_cost_segments, _ = LineSegment.split_text_for_symbols(
                card_data.raw_mana_cost_string.lower(), card_image_total, 420, 500, 
                debug_mode=debug_on, font_override=(chosen_manacost_font, chosen_manacost_bg_font)
            )
            mana_cost_segments: list[LineSegment] = mana_cost_segments
            # We assume each pip is the same width and draw them from left to right with manual offsets
            num_mana_pips = len(mana_cost_segments)
            mana_pip_width = mana_cost_segments[0].dims[0] if num_mana_pips > 0 else 0
            mana_cost_size = num_mana_pips
            # When templating, we prefer to shrink the title before the mana cost.
            # Therefore we'll try to fit the title in the space left by the manacost.
            max_title_and_manacost_string_width_in_pixels = max_title_and_manacost_string_width_ratio * card_pixel_dims[0]
            # We require at least one pip worth of space between the text and the pips
            space_remaining_for_title = max_title_and_manacost_string_width_in_pixels - mana_pip_width
            # Find the title font size
            title_string_width, _ = Fonts.get_string_size(card_data.name, chosen_title_font)
            if title_string_width > space_remaining_for_title:
                current_title_width_to_space_ratio = space_remaining_for_title / title_string_width
                chosen_title_font = Fonts.get_title_font(Fonts.font_title_initial_size * current_title_width_to_space_ratio)
            
            # Title
            title_color: tuple[int, int, int] = C_WHITE if card_data.is_token else C_BLACK
            title_text: str = card_data.name.upper() if card_data.is_token else card_data.name
            title_position: tuple[int, int] = math_utils.add_tuples((40, 54), (210, 1) if card_data.is_token else (0, 0))
            ImageDraw.Draw(card_image_total).text(
                title_position, title_text, title_color, font=chosen_title_font, anchor=("mm" if card_data.is_token else "lm")
            )
            # END Name and Manacost #################################################

            if debug_on:
                log_and_print(num_mana_pips)
            if num_mana_pips > 0:
                mana_pip_width = mana_cost_segments[0].dims[0]
                margin = 0 #int(mana_pip_width * 0.1)
                left_mana_border = right_mana_border - (mana_pip_width * num_mana_pips) - (margin * (num_mana_pips-1))
                for i, segment in enumerate(mana_cost_segments):
                    segment.draw(card_image_total, (left_mana_border + ((mana_pip_width + margin) * i), 40), absolute_draw_mode=True, mana_cost_mode=True)


            # Types ##########################
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

            types_string_yoffset: float = 413 + (token_yoffset if card_data.is_token else 0)
            ImageDraw.Draw(card_image_total).text(
                (40, types_string_yoffset), card_data.get_type_string(), C_BLACK, font=chosen_types_font, anchor="lm"
            )

            # Body Text ######################
            # Config
            # Go through each line of text and convert it into a series of LineSegments - each with their own font, offset, and text
            # Then draw each of their texts on the card at their offset and with their font

            # To maximize utilized card space and potentially accomodate flavor text, we impose the following basic rules:
            # Card text fits before flavor text fits
            # Strive for at most 9 lines of body text, including flavor text.
            # Now the method:
            # Calculate how much space the body text'll take up with the flavor. It they take up more than the space
            # between the top and where the stat box is (if it has one; otherwise until end of card), then
            # calculate what proportion is needed to apply to the pips'/text's fonts.
            # If you can't fit both in 9 lines, try again without the flavor text.

            # How do we calculate the new proportion?
            # For now a naive binary search approach will do. 
            # If you took more than 9 lines, go between min font size (minFS) and current size.
            # Then if that's less than 9 lines, go halfway between that and the last size, and so on (maybe add some max attempts parameter)

            pip_BG_size_factor = 0.9
            total_card_body_text: str = card_data.body_text #+ ("\n" + card_data.flavor_text if len(card_data.flavor_text) > 0 else "")
            segments, went_over_line_limit = LineSegment.split_text_for_symbols(total_card_body_text, card_image_total, 420, 500, get_bounding_box_mode=True, font_override=(Fonts.font_body, Fonts.font_body_italic, Fonts.font_symbols, Fonts.get_symbol_font(Fonts.font_symbols_initial_size * pip_BG_size_factor)))
            segments: list[LineSegment] = segments
            current_font_size = Fonts.font_body_initial_size
            current_mana_font_size = Fonts.font_symbols_initial_size
            current_font_max, current_font_min = Fonts.font_body_max_size, Fonts.font_body_min_size
            resized_text_font, resized_symbols_font = None, None
            body_text_too_large = went_over_line_limit
            tries = 5
            # we could also try making text larger than normal, but so long as the initial text size is reasonable we don't need to
            # for now this just corrects for too-large bodies of text
            if went_over_line_limit:
                if warn_about_card_semantics_errors:
                    log_and_print(f"{card_data.name}'s text is too large for default font size. Resizing...", do_print=verbose_mode_cards)
                while tries > 0:
                    # print(body_text_too_large)
                    if body_text_too_large:
                        current_font_max = current_font_size
                    else:
                        current_font_min = current_font_size

                    current_font_size = (current_font_min + current_font_max) / 2

                    ratio_from_max_to_current = current_font_size / Fonts.font_body_max_size
                    current_mana_font_size = Fonts.font_symbols_initial_size * ratio_from_max_to_current
                    
                    resized_text_font = Fonts.get_body_font(current_font_size)
                    resized_italic_font = Fonts.get_body_font(current_font_size, italic=True)
                    resized_symbols_font = Fonts.get_symbol_font(current_mana_font_size)
                    segments, body_text_too_large = LineSegment.split_text_for_symbols(total_card_body_text, card_image_total, 420, 500, get_bounding_box_mode=True, font_override=(resized_text_font, resized_italic_font, resized_symbols_font, Fonts.get_symbol_font(current_mana_font_size * pip_BG_size_factor)))

                    tries -= 1
                    # print(card_data.name)
                    # print(tries, body_text_too_large, current_font_max, current_font_min, current_font_size)

            if body_text_too_large and warn_about_card_semantics_errors:
                log_and_print(f"{card_data.name}'s text was too large to fit properly.", do_print=verbose_mode_cards)

            body_text_position: tuple[int, int] = math_utils.add_tuples((44, 445), (0, token_yoffset) if card_data.is_token else (0, 0))
            for segment in segments:
                segment.draw(card_image_total, body_text_position)
           
            if card_data.has_stats:
                ImageDraw.Draw(card_image_total).text(
                    (433, 643), card_data.get_stats_string(), C_BLACK, Fonts.font_stats, anchor="mm"
                )
            
            rgb_image = card_image_total.convert("RGB")
            try:
                corresponding_filepath: str = images_save_filepath["token" if card_data.is_token else "normal"]
                rgb_image.save(corresponding_filepath + f"{card_data.name}.{CARD_PICTURE_FILE_FORMAT}", quality=100)
            except:
                raise ValueError(f"There was an issue saving the image for: {card_data.name}")

            if verbose_mode_cards:
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
def initialize_card_image_assets(assets_filepath: dict[str, str]) -> dict[str, Image]:
    resized_images: dict[str, Image] = {}
    verbose_mode_files = metadata.settings_data_obj["card_semantics_settings"]["verbose_mode_files"]
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
    special_card_modifiers = ["", "token"]

    image_prefixes  = [CardImageInfo(frame, side, color, should_be_modified=True, special_card_modifier=modifier) for frame in card_frame_type for side in ["l", "r"] for color in splittable_card_prefixes for modifier in special_card_modifiers]
    image_prefixes += [CardImageInfo(frame_supertype, "", frame_subtype, should_be_modified=False, special_card_modifier=modifier) for frame_supertype in card_frame_type for frame_subtype in unsplittable_card_prefixes for modifier in special_card_modifiers]
    image_prefixes += [CardImageInfo("pt", "", frame_subtype, should_be_modified=False) for frame_subtype in splittable_card_prefixes + unsplittable_card_prefixes + one_off_card_subtypes]
    image_prefixes += [CardImageInfo(f"set_symbol_{rarity}", "", "", should_be_modified=False, special_card_asset_name_mode=True) for rarity in ["common", "uncommon", "rare", "mythic"]]

    # If the card is one that needs masking and splitting, it's marked as such 
    image_suffix: str = "_base.png"
    hybrid_card_mask_image: Image = None
    hybrid_card_masks: dict[str, Image] = {}
    try:
        hybrid_card_mask_image = Image.open(assets_filepath["pre-set"] + "hybrid_card_mask.png")
        hybrid_card_mask_image = hybrid_card_mask_image.resize(card_pixel_dims).convert("RGBA")
        hybrid_card_masks["l"] = hybrid_card_mask_image
        hybrid_card_masks["r"] = hybrid_card_mask_image.transpose(Image.FLIP_LEFT_RIGHT)
    except:
        raise ValueError("There was a problem accessing the transparency mask.")

    for prefix in image_prefixes:
        image_info: CardImageInfo = prefix
        base_folder_path: str = assets_filepath["generated" if image_info.should_be_modified else "pre-set"]
        expected_image_filepath = base_folder_path + image_info.file_prefix + image_suffix
        image_info.filepath = expected_image_filepath
        try:
            if not image_info.should_be_modified:
                # If the image isn't to be modified to generate new card borders, it should exist
                # ... and we just need to resize it and hold it in memory
                log_and_print(f"Accessing base file to simply load it into memory {expected_image_filepath}", do_print=verbose_mode_files)
                base_image: Image = Image.open(expected_image_filepath)
                resized_image: Image = base_image.resize(card_pixel_dims)
                resized_images[image_info.file_prefix] = resized_image.convert("RGBA")
            else:
                # Here the image shouldn't necessarily exist because we need to generate it.
                # We'll check if we already have:
                was_image_generated: bool = os.path.isfile(expected_image_filepath)
                base_image_filepath = assets_filepath["pre-set"] + image_info.base_file_prefix + image_suffix
                if not was_image_generated or metadata.settings_data_obj["asset_loading_settings"]["always_regenerate_base_card_frames"]:
                    log_and_print(f"To-be-generated file {expected_image_filepath} doesn't exist. Generating...", do_print=verbose_mode_files)
                    log_and_print(f"Accessing base file {base_image_filepath} to mask it", do_print=verbose_mode_files)
                    base_image = Image.open(base_image_filepath)
                    resized_image: Image = base_image.resize(card_pixel_dims)
                    masked_image = ImageChops.multiply(resized_image, hybrid_card_masks[image_info.side])
                    resized_images[image_info.file_prefix] = masked_image
                    # Save the image so we don't need to generate it next time
                    masked_image.save(expected_image_filepath, quality=100)
                else:
                    log_and_print(f"Generated file {base_image_filepath} already exists! Simply loading/resizing.", do_print=verbose_mode_files)
                    loaded_image = Image.open(expected_image_filepath)
                    resized_image: Image = loaded_image.resize(card_pixel_dims)
                    resized_images[image_info.file_prefix] = resized_image
        except:
            raise ValueError(f"There was an issue accessing image: {expected_image_filepath}.\n \
                        You may need to redownload the Playtest_Base_Images folder.")

    return resized_images

def group_cards_by_rarity(card_rarities: list[str], cards_dict: dict[str: Card]):
    cards_by_rarity: dict[str, list[Card]] = {rarity[0].lower(): [] for rarity in card_rarities}
    for card in cards_dict.values():
        try:
            cards_by_rarity[card.rarity].append(card)
        except:
            raise ValueError(f"{card.name} didn't have a rarity and couldn't be sorted.")
            
    return cards_by_rarity

def generate_markdown_file(markdown_filepath: dict[str, str], 
                           cards_dict: dict[str: Card],
                           header_string: dict[str, str],
                           closer_string: dict[str, str],
                           set_code: str):
    # Make normal cards markdown
    with open(markdown_filepath["normal"], 'w') as markdown_file:
        markdown_file.write(header_string["normal"])
        for card in cards_dict.values():
            if card.is_token:
                continue

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

        markdown_file.write(closer_string["normal"])

    # Make tokens markdown
    with open(markdown_filepath["token"], 'w') as markdown_file:
        markdown_file.write(header_string["token"])
        for card in cards_dict.values():
            if not card.is_token:
                continue

            markdown_file.write(
f"""
<card>
    <name>{card.name}</name>
    <set picURL="{f"/{card.name}.full.{CARD_PICTURE_FILE_FORMAT}"}" picURLHq="" picURLSt="">{set_code}</set>
    <color>{card.colors}</color>
    <manacost>{card.manacost}</manacost>
    <type>Token {card.get_type_string()}</type>{"" if card.stats is None else f"{chr(10) + chr(9)}<pt>{card.stats[0]}/{card.stats[1]}</pt>"}
    <tablerow>0</tablerow>
    <text>{card.body_text}</text>
    {card.get_related_cards_string()}
</card>
"""
    )

        markdown_file.write(closer_string["token"])

    

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

        num_non_token_cards = 0
        for card in cards_dict.values():
            if not card.is_token:
                num_non_token_cards += 1

        i: int = 0
        for card in cards_dict.values():
            if card.is_token:
                continue

            draft_text_file.write(card.get_draft_text_rep(uploaded_images_base_url, CARD_PICTURE_FILE_FORMAT))
            if i < num_non_token_cards - 1:
                draft_text_file.write(",")

            i += 1
        draft_text_file.write("\n]\n")

        # Writing in cards sorted by rarity
        for rarity in card_rarities:
            draft_text_file.write("[" + rarity + "]\n")
            rarity_code: str = rarity[0].lower()
            for card in cards_by_rarity[rarity_code]:
                if not card.is_token:
                    draft_text_file.write(card.name + "\n")

