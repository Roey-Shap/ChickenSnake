import csv
from Card import Card
from PIL import Image, ImageFont, ImageDraw, ImageTk
from Fonts import body_text_font_name, symbols_font_name
from LineSegment import LineSegment

C_BLACK = (0, 0, 0)
C_WHITE = (255, 255, 255)
# card_pixel_dims = (375, 523)
card_pixel_dims = (500, 700)
font_title = ImageFont.truetype(body_text_font_name, 26)
font_title_small = ImageFont.truetype(body_text_font_name, 18)

font_types = ImageFont.truetype(body_text_font_name, 24)
font_types_small = ImageFont.truetype(body_text_font_name, 15)

font_stats = ImageFont.truetype(body_text_font_name, 30)

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

def get_power_toughness(csv_row: dict[str, str]) -> tuple[int, int] | None:
    power_string = csv_row["Power"]
    toughness_string = csv_row["Toughness"]
    try:
        power, toughness = int(power_string), int(toughness_string)
        return (power, toughness)
    except:
        return None

def get_mana_cost_string(raw_mana_cost: str) -> str:
    tokens = raw_mana_cost.split('{')
    stripped = [s.removesuffix('}').upper() for s in tokens if len(s) > 0]
    hybrid = ["{" + s + "}" if '/' in s else s for s in stripped]
    joined = ''.join(hybrid)

    return joined

def get_card_data_from_spreadsheet(card_data_filepath) -> dict[str, Card]:
    cards_dict: dict[str, Card] = {}
    with open(card_data_filepath) as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if row["Is Card"] == "1":
                name = row["Name"]
                colors = get_color_string(row)
                manacost = get_mana_cost_string(row["Cost"])
                converted_manacost = row["CMC"]
                type = row["Type"]
                subtype = row["Subtype"]
                stats = get_power_toughness(row)
                body_text = row["Desc"]
                flavor_text = row["Flavor Text"]

                cards_dict[name] = Card(
                    name, colors, manacost, 
                    converted_manacost, type, subtype,
                    stats, body_text, flavor_text
                )

    return cards_dict

def generate_card_images(card_dict: dict[str, Card], images_save_filepath: str, image_assets: dict[str, Image]):
    num_cards_total = len(card_dict)
    current_card_index = 0

    for card_data in card_dict.values():
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
        chosen_title_font = font_title
        chosen_manacost_font = font_types
        if len(card_data.name) + len(card_data.manacost) > 25:
            chosen_title_font = font_title_small
            chosen_manacost_font = font_types_small

        # Title
        ImageDraw.Draw(card_image_total).text(
            (40, 40), card_data.name, C_BLACK, font=chosen_title_font
        )

        # Mana Cost
        ImageDraw.Draw(card_image_total).text(
            (343, 50), card_data.manacost, C_BLACK, font=chosen_manacost_font, anchor="rt"
        )

        # Types
        ImageDraw.Draw(card_image_total).text(
            (40, 400), card_data.get_type_string(), C_BLACK, font=font_types
        )

        # Body Text config
        # Go through each line of text and convert it into a series of LineSegments - each with their own font, offset, and text
        # Then draw each of their texts on the card at their offset and with their font

        segments: list[LineSegment] = LineSegment.split_text_for_symbols(
            card_data.body_text, card_image_total, 420, 500
        )

        for segment in segments:
            segment.draw(card_image_total, (40, 450))
        # chosen_body_font = font_body
        # chosen_body_max_width = 300
        # if len(card_data.body_text.split()) > 65:
        #     chosen_body_font = font_body_tiny
        #     chosen_body_max_width = 355
        # elif len(card_data.body_text.split()) < 35:
        #     chosen_body_font = font_body_large
        #     chosen_body_max_width = 250



        # ImageDraw.Draw(card_image_total).text(
        #     (36, 330), get_wrapped_text(card_data.body_text, font_body, chosen_body_max_width), C_BLACK, chosen_body_font, spacing=2
        # )

        if card_data.has_stats:
            ImageDraw.Draw(card_image_total).text(
                (433, 643), f"{card_data.stats[0]}/{card_data.stats[1]}", C_BLACK, font_stats, anchor="mm"
            )

        try:
            card_image_total.save(images_save_filepath + f"{card_data.name}.png", quality=100)
        except:
            print(f"There was an issue saving the image for: {card_data.name}")

        if current_card_index % 25 == 0:
            print(f"Finished card {current_card_index+1}/{num_cards_total}")



        current_card_index += 1
        return

        
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

# Initially from Stack Overflow "Wrap text in PIL", modified to account for text that already has newlines
def get_wrapped_text(text: str, font: ImageFont.ImageFont, line_length: int, debug_mode=False):
    lines_init = text.split("\n")
    lines_total = []
    for line_init in lines_init:
        lines = [""]
        for word in line_init.split():
            line = f"{lines[-1]} {word}".strip()
            if font.getlength(line) <= line_length:
                lines[-1] = line
            else:
                lines.append(word)
        
        lines_total += lines

    return '\n'.join(lines_total)