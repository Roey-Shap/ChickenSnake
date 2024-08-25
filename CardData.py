import csv
from Card import Card
from PIL import Image, ImageFont, ImageDraw, ImageTk
from Fonts import body_text_font_name, symbols_font_name
from LineSegment import LineSegment
import Fonts
from LineSegment import hybrid_pips_with_non_wubrg_order_colors

import traceback

CARD_PICTURE_FILE_FORMAT = "jpg"

C_BLACK = (0, 0, 0)
C_WHITE = (255, 255, 255)
# card_pixel_dims = (375, 523)
card_pixel_dims = (500, 700)
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
                stats = get_power_toughness(row)
                body_text = row["Desc"]
                flavor_text = row["Flavor Text"]

                cards_dict[name] = Card(
                    name, colors, manacost, raw_mana_cost_string,
                    converted_manacost, supertype, subtype,
                    stats, body_text, flavor_text
                )

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
                # print(num_mana_pips)

            if num_mana_pips > 0:
                mana_pip_width = mana_cost_segments[0].dims[0]
                margin = 0 #int(mana_pip_width * 0.1)
                left_mana_border = right_mana_border - (mana_pip_width * num_mana_pips) - (margin * (num_mana_pips-1))
                for i, segment in enumerate(mana_cost_segments):
                    segment.draw(card_image_total, (left_mana_border + ((mana_pip_width + margin) * i), 40), absolute_draw_mode=True, mana_cost_mode=True)

            # Types
            chosen_types_font = Fonts.font_types
            types_string = card_data.get_type_string()
            if len(types_string) > 32:
                chosen_types_font = Fonts.font_types_small
            if len(types_string) > 40:
                chosen_types_font = Fonts.font_types_tiny

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

            if current_card_index % 25 == 0:
                print(f"Finished card {current_card_index+1}/{num_cards_total}")



            current_card_index += 1
        except Exception as e:
            print(f"There was an issue with {card_data.name}")
            print(e)
            print(traceback.format_exc())
            print()

def initialize_card_image_assets(assets_filepath: str) -> dict[str, Image]:
    resized_images: dict[str, Image] = {}
    image_color_prefixes = [f"{color}_{side}" for side in ["l", "m", "r"] for color in "WUBRG"] + ["c_pt_", "m_", "c_"]
    for prefix in image_color_prefixes:
        image_filepath = assets_filepath + prefix.lower() + "base.png"
        print("Opening:", image_filepath)
        base_image: Image = Image.open(image_filepath)
        resized_image: Image = base_image.resize(card_pixel_dims)
        resized_images[prefix] = resized_image.convert("RGBA")
    
    return resized_images