import csv
from Card import Card
from PIL import Image, ImageFont, ImageDraw, ImageTk

C_BLACK = (0, 0, 0)
C_WHITE = (255, 255, 255)
# card_pixel_dims = (375, 523)
card_pixel_dims = (500, 700)

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
    font_title = ImageFont.truetype("OpenSans-Regular.ttf", 22)
    font_title_small = ImageFont.truetype("OpenSans-Regular.ttf", 18)

    font_types = ImageFont.truetype("OpenSans-Regular.ttf", 18)
    font_types_small = ImageFont.truetype("OpenSans-Regular.ttf", 15)

    font_body  = ImageFont.truetype("OpenSans-Regular.ttf", 13)
    font_body_tiny = ImageFont.truetype("OpenSans-Regular.ttf", 11)
    font_body_large  = ImageFont.truetype("OpenSans-Regular.ttf", 15)
    num_cards_total = len(card_dict)
    current_card_index = 0

    # base_names_from_colors: dict[str, str] = {
    #     "W": "white_base",
    #     "U": "blue_base",
    #     "B": "black_base", 
    #     "R": "red_base",
    #     "G": "green_base",
    #     "M": "multicolored_base",
    #     "C": "colorless_base"
    # }
    # image_base_colors: dict[str, tuple[int, int, int]] = {
    #     "W": C_WHITE,
    #     "U": (150, 150, 200),
    #     "B": (130, 130, 130),
    #     "R": (200, 150, 150),
    #     "G": (150, 200, 150),
    #     "M": (200, 200, 150),
    #     "C": (200, 200, 200)
    # }

    for card_data in card_dict.values():

        card_image_total = Image.new(mode="RGB", size=card_pixel_dims, color=C_WHITE).convert("RGBA")

        # match len(card_data.colors_string):
        #     case 0:
        #         card_image_total.col
        #     case 1 | 2:
        #         pass
        #     case _:
        #         pass

        # if card_data.is_colorless:
        #     card_base_image = image_assets[base_names_from_colors["C"]]
        # elif len(card_data.colors_string) > 1:
        #     card_base_image = image_assets[base_names_from_colors["M"]]
        # else:
        #     card_base_image = image_assets[base_names_from_colors[card_data.colors_string]]


        # Card Base
        if 1 <= len(card_data.colors_string) <= 2 and not card_data.is_gold and not card_data.is_colorless:
            card_colors = card_data.colors_string
            for prefix in [card_colors[0]+"_l", card_colors[-1]+"_r"]:
                card_bg: Image = image_assets[prefix]
                card_image_total.alpha_composite(card_bg)
        elif card_data.is_colorless:
            # print("c")
            card_image_total.alpha_composite(image_assets["c_"])
        else:
            # print("gold")
            card_image_total.alpha_composite(image_assets["m_"])

        Image.alpha_composite(card_image_total, image_assets["c_pt_"])
        # alpha_composite(image_assets["c_pt_"])

        # Title font config
        chosen_title_font = font_title
        chosen_manacost_font = font_types
        if len(card_data.name) + len(card_data.manacost) > 25:
            chosen_title_font = font_title_small
            chosen_manacost_font = font_types_small

        # Title
        ImageDraw.Draw(card_image_total).text(
            (32, 26), card_data.name, C_BLACK, font=chosen_title_font
        )

        # Mana Cost
        ImageDraw.Draw(card_image_total).text(
            (343, 35), card_data.manacost, C_BLACK, font=chosen_manacost_font, anchor="rt"
        )

        # Types
        ImageDraw.Draw(card_image_total).text(
            (36, 294), card_data.get_type_string(), C_BLACK, font=font_types
        )

        # Body Text config
        chosen_body_font = font_body
        chosen_body_max_width = 300
        if len(card_data.body_text.split()) > 65:
            chosen_body_font = font_body_tiny
            chosen_body_max_width = 355
        elif len(card_data.body_text.split()) < 35:
            chosen_body_font = font_body_large
            chosen_body_max_width = 250

        ImageDraw.Draw(card_image_total).text(
            (36, 330), get_wrapped_text(card_data.body_text, font_body, chosen_body_max_width), C_BLACK, chosen_body_font, spacing=2
        )

        if card_data.stats is not None:
            ImageDraw.Draw(card_image_total).text(
                (293, 462), f"{card_data.stats[0]}/{card_data.stats[1]}", C_BLACK, font_title
            )

        try:
            card_image_total.save(images_save_filepath + f"{card_data.name}.png", quality=100)
        except:
            print(f"There was an issue saving the image for: {card_data.name}")

        if current_card_index % 25 == 0:
            print(f"Finished card {current_card_index+1}/{num_cards_total}")



        current_card_index += 1

        
def initialize_card_image_assets(assets_filepath: str) -> dict[str, Image]:
    resized_images: dict[str, Image] = {}
    image_color_prefixes = [f"{color}_{side}" for side in ["l", "r"] for color in "WUBRG"] + ["c_pt_", "m_", "c_"]
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