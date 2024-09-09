import csv
from Card import Card
from PIL import Image, ImageFont, ImageDraw, ImageTk
from Fonts import body_text_font_name, symbols_font_name
from LineSegment import LineSegment
import Fonts
from LineSegment import hybrid_pips_with_non_wubrg_order_colors
import metadata
from UI import log_and_print

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

def generate_card_images(card_dict: dict[str, Card], images_save_filepath: str, image_assets: dict[str, Image]):
    num_cards_total = len(card_dict)
    current_card_index = 0

    for card_data in card_dict.values():
        try:
            card_image_total = Image.new(mode="RGB", size=card_pixel_dims, color=C_WHITE).convert("RGBA")

            # Card Base
            if card_data.is_colorless:
                card_image_total.alpha_composite(image_assets["c_"])
            elif 1 <= len(card_data.colors_string) <= 2 and not card_data.is_gold:
                card_colors = card_data.colors_string
                # It's important to layer the middle part first so it can be covered up by the sides
                for prefix in [card_colors[-1]+"_m", card_colors[0]+"_l", card_colors[-1]+"_r"]:
                    card_bg: Image = image_assets[prefix]
                    card_image_total.alpha_composite(card_bg)            
            else:
                card_image_total.alpha_composite(image_assets["m_"])

            if card_data.has_stats:
                card_image_total.alpha_composite(image_assets["c_pt_"])

            # Set Symbol
            card_image_total.alpha_composite(image_assets["set_symbol_"])

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

def initialize_card_image_assets(assets_filepath: str) -> dict[str, Image]:
    resized_images: dict[str, Image] = {}
    image_color_prefixes = [f"{color}_{side}" for side in ["l", "m", "r"] for color in "WUBRG"] + ["c_pt_", "m_", "c_", "set_symbol_"]
    for prefix in image_color_prefixes:
        image_name_suffix = prefix.lower() + "base.png"
        image_filepath = assets_filepath + image_name_suffix
        try:
            base_image: Image = Image.open(image_filepath)
            resized_image: Image = base_image.resize(card_pixel_dims)
            resized_images[prefix] = resized_image.convert("RGBA")
        except:
            raise ValueError(f"There was an issue accessing image: {image_name_suffix}")

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

