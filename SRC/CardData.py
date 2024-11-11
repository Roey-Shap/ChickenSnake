import csv
import traceback
import os.path

from PIL import Image, ImageFont, ImageDraw, ImageTk, ImageChops

from Card import Card
from Fonts import body_text_font_name, symbols_font_name
from LineSegment import LineSegment, hybrid_pips_with_non_wubrg_order_colors
import Fonts
import metadata
from UI import log_and_print
import math_utils


CARD_PICTURE_FILE_FORMAT = "jpg"

C_BLACK = (0, 0, 0)
C_WHITE = (255, 255, 255)

CARD_PIXEL_DIMS = (500, 700)
def scale_to_card_dims(percent_x, percent_y) -> tuple[float, float]:
    return (percent_x * CARD_PIXEL_DIMS[0], percent_y * CARD_PIXEL_DIMS[1])



TOKEN_TEXT_YOFFSET                              = 0.08429 * CARD_PIXEL_DIMS[1]
MAX_TYPES_STRING_WIDTH_IN_PIXELS                = 0.71 * CARD_PIXEL_DIMS[0]
MAX_TITLE_AND_MANACOST_STRING_WIDTH_IN_PIXELS   = 0.83 * CARD_PIXEL_DIMS[0]
CARD_IMAGE_RIGHT_MANA_BORDER_NORMAL_CARD        = 0.93 * CARD_PIXEL_DIMS[0]
CARD_IMAGE_RIGHT_MANA_BORDER_ADVENTURE          = 0.49 * CARD_PIXEL_DIMS[0]

TITLE_OFFSET_BASE_PIXELS                        = scale_to_card_dims(0.08, 0.0771)
TOKEN_TITLE_OFFSET_PIXELS                       = scale_to_card_dims(0.42, 0.00142857)
TITLE_OFFSET_BASE_ADVENTURE_PIXELS              = scale_to_card_dims(0.07, 0.65714)
TYPES_STRING_OFFSET_Y_PIXELS                    = 0.59 * CARD_PIXEL_DIMS[1]

BODY_TEXT_OFFSET_NORMAL_CARD                    = scale_to_card_dims(0.088, 0.6357)
BODY_TEXT_MAX_DIMS_NORMAL_CARD                  = scale_to_card_dims(0.84, 0.264)

BODY_TEXT_OFFSET_ADVENTURE_LEFT                 = scale_to_card_dims(0.07, 0.72857)
BODY_TEXT_OFFSET_ADVENTURE_RIGHT                = math_utils.add_tuples(BODY_TEXT_OFFSET_ADVENTURE_LEFT, scale_to_card_dims(0.45, -0.085714))
BODY_TEXT_MAX_DIMS_ADVENTURE                    = scale_to_card_dims(0.45, 0.13)

MAX_TYPES_STRINGS_WIDTH_ADVENTURE_IN_PIXELS = BODY_TEXT_MAX_DIMS_ADVENTURE[0]

MANACOST_YOFFSET_PIXELS                         = 0.057143 * CARD_PIXEL_DIMS[1]
MANACOST_YOFFSET_PIXELS_ADVENTURE               = 0.6357 * CARD_PIXEL_DIMS[1]

MAX_MANACOST_TEXT_DIMS                          = scale_to_card_dims(0.84, 0.71429)

CARD_IMAGE_POWER_TOUGHNESS_POSITION             = scale_to_card_dims(0.866, 0.92143)

markdown_closer_string_normal = \
f"""
</cards>
</cockatrice_carddatabase>
"""

markdown_closer_string_tokens = \
f"""
</cards>
</cockatrice_carddatabase>
"""

class CardImageInfo():
    """
    A CardImageInfo object holds information about an image which is a component of building up card images.
    For example, half of a blue border, or a colorless power/toughness box image.
    """
    def __init__(self, frame_supertype: str, side: str, frame_subtype: str,
                    should_be_modified=False, special_card_asset_name_mode=False,
                    special_card_modifier="", position_on_card=(0, 0)) -> None:
        self.frame_supertype = frame_supertype
        self.side = side
        self.frame_subtype = frame_subtype
        self.should_be_modified = should_be_modified
        self.position_on_card = (position_on_card[0], position_on_card[1]) # Copy the tuple
        # TODO: This whole underscore business is super messy
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

def get_color_string_from_csv_row(csv_row: dict[str, str]) -> str:
    """
    Returns:
        str: A string of up to five colors or the empty string if the card is colorless.
    """
    color_string = ""
    color_string += "W" if csv_row["Is White"] == "1" else ""
    color_string += "U" if csv_row["Is Blue"] == "1" else ""
    color_string += "B" if csv_row["Is Black"] == "1" else ""
    color_string += "R" if csv_row["Is Red"] == "1" else ""
    color_string += "G" if csv_row["Is Green"] == "1" else ""

    return color_string

def get_power_toughness_from_csv_row(csv_row: dict[str, str]) -> tuple[int|str, int|str] | int | str | None:
    """
    Tries to return a tuple with the power/toughness of the card, accomodating *-power/toughness cards.
    Note that if one or more of the values is blank or can't be interpreted as an int, you'll get None.
    """
    power_string = csv_row["Power"]
    toughness_string = csv_row["Toughness"]
    try:
        power_len = len(power_string)
        tough_len = len(toughness_string)
        if power_string == "*":
            power = "*"
        else:
            power = int(power_string)
            if tough_len == 0:
                return power
        
        if toughness_string == "*":
            toughness = "*"
        else:
            toughness = int(toughness_string)

        return (power, toughness)
    except:
        return None

def get_mana_cost_string(raw_mana_cost: str) -> str:
    """
    Returns:
        str: A Cockatrice/Draftmancer-standardized string representing the mana cost of a card. Uses UPPERCASE, properly
        orders hybrid pips, and puts everything back with {brackets}.
    """
    tokens = raw_mana_cost.split('{')
    stripped = [s.removesuffix('}').upper() for s in tokens if len(s) > 0]
    hybrid = ["{" + reorder_mana_string(s) + "}" if '/' in s else s for s in stripped]
    joined = ''.join(hybrid)

    return joined

def reorder_mana_string(stripped_cost: str) -> str:
    """
    Reorders the colors in a single hybrid pip to be Scryfall-standardized.
    """
    if stripped_cost.lower() in hybrid_pips_with_non_wubrg_order_colors or "p" in stripped_cost.lower():
        first, second = stripped_cost.split('/')
        return second + '/' + first
    else:
        return stripped_cost

def get_card_data_from_spreadsheet(card_data_filepath) -> dict[str, Card]:
    """
    Gives a dictionary of cardname-Card data pairs (ChickenSnake's representation of a card, anyway) by reading
    data from the given full filepath of a CSV spreadsheet file. 
    """
    verbose_mode_cards = metadata.settings_data_obj["card_semantics_settings"]["verbose_mode_cards"]
    semantics_settings = metadata.settings_data_obj["card_semantics_settings"]
    reference_card_name = semantics_settings["reference_card_name"]

    cards_dict: dict[str, Card] = {}

    with open(card_data_filepath) as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            is_valid_nontoken_card = row["Is Card"] == "1"
            is_valid_card: bool = is_valid_nontoken_card or row["Is Token"] == "TRUE"
            if is_valid_card:
                name = row["Name"]
                colors = get_color_string_from_csv_row(row)
                raw_mana_cost_string = row["Cost"]
                manacost = get_mana_cost_string(raw_mana_cost_string)
                converted_manacost = row["CMC"]
                supertype = row["Type"]
                subtype = row["Subtype"]
                rarity = row["Rarity"]
                is_token = row["Is Token"] == "TRUE"

                stats = get_power_toughness_from_csv_row(row)
                body_text = row["Desc"]
                flavor_text = row["Flavor Text"]
                related_card_names = row["Related Cards"].split(",") # @TODO change this delimeter. Some cardnames have ",". Greedy match by regex...?
                related_card_names = [name.strip() for name in related_card_names if len(name) > 0]

                # Replace placeholder name with card name
                _replacement_name = name
                _can_shorten_name = "," in name
                _replacement_name_short = name.split(",")[0] if _can_shorten_name else None
                if semantics_settings["replace_reference_string_with_cardname"] and len(reference_card_name) > 0:
                    if semantics_settings["shortened_reference_card_name_when_able"] and _can_shorten_name:
                        _replacement_name = _replacement_name_short
                        
                    body_text = body_text.replace(reference_card_name, _replacement_name)

                loaded_card = Card(
                    name, colors, manacost, raw_mana_cost_string,
                    converted_manacost, supertype, subtype, rarity,
                    stats, body_text, flavor_text, is_token
                )
                
                if row["Is Adventure"] == "TRUE":
                    loaded_card.set_as_adventure(True)

                if _can_shorten_name:
                    loaded_card.set_short_name(_replacement_name_short)

                
                # Find which cards mention this one (if this card is a token, for example)
                for related_name in related_card_names:
                    loaded_card.set_related_card_name(related_name)

                cards_dict[name] = loaded_card

    for card in cards_dict.values():
        found_related_nontoken_card = False
        for related_card in card.related_card_names:
            related_card_data = cards_dict[related_card]
            if not related_card_data.is_token:
                found_related_nontoken_card = True
                card.related_nontoken_pair_card = related_card_data
                break

    # Card data warnings
    saw_card_with_errors: bool = False
    card: Card
    for card in cards_dict.values():
        card_warning_messages = []
        is_creature = card.search_for_supertype_string("creature")
        is_land = card.search_for_supertype_string("land")
        is_battle = card.search_for_supertype_string("battle")
        is_planeswalker = card.search_for_supertype_string("planeswalker")
        if len(card.raw_mana_cost_string) == 0 and is_land and not card.is_token:
            card_warning_messages.append("Missing a mana cost.")

        if card.found_manacost_error and metadata.settings_data_obj["card_semantics_settings"]["warn_about_card_semantics_errors"]:
            card_warning_messages.append("Had a manacost pip-order error:")
            for pip in card.corrected_pips:
                card_warning_messages.append(f"   Correcting manacost hybrid pip order: {pip} -> {pip[::-1]}")

        if len(card.supertype) == 0:
            card_warning_messages.append("Missing a supertype.")
        if (is_creature or is_battle or is_planeswalker) and len(card.subtype) == 0:
            card_warning_messages.append("Missing a subtype.")
        if is_creature and not card.stats_are_power_toughness:
            card_warning_messages.append("Missing power/toughness.")

        if (card.stats_are_power_toughness or not card.has_stats) and (is_battle or is_planeswalker):
            _reason_for_stat_problem = "without stats" if not card.has_stats else "with power/toughness"
            _supertype_string = "Battle" if is_battle else "Planeswalker"
            _counter_type = "defense" if is_battle else "loyalty"
            card_warning_messages.append(f"{_supertype_string} is {_reason_for_stat_problem}. Leave only one of power/toughness as its {_counter_type}.")
                
        if metadata.settings_data_obj["card_semantics_settings"]["rarities_should_be_in_place"] and card.is_rarity_missing and not card.is_token:
            card_warning_messages.append("Missing rarity. Defaulting to COMMON.")
        
        # Warn about cards that are tokens and related to an adventure-base card
        if card.related_nontoken_pair_card is not None and card.is_token:
            card_warning_messages.append("Card is a token but also an adventure. Formatting currently unsupported!")
        
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
    """
    Gives a list of images (in CardImageInfo object form) that a card will need for its image to be generated.
    """
    frame_supertypes = ["normal"]
    frame_subtypes = []
    frame_modifier = "token" if card_data.is_token else ""
    # Note that the Card's color_string is just "M" if it's gold!
    # ... just to test for now...
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
        frame_supertypes[0] = "enchantment"
    if card_data.is_miracle:
        frame_supertypes.append("miracle")
    if card_data.is_adventure:
        frame_supertypes = ["adventureleft"]
    elif card_data.related_nontoken_pair_card:
        if card_data.related_nontoken_pair_card.is_adventure:
            frame_supertypes.append("adventureright")

    infos: list[CardImageInfo] = []
    if len(frame_subtypes) > 1:
        # print(frame_subtypes)
        valid_sides = ["l", "r"] if len(frame_subtypes) == 2 else ["l", "m", "r"]
        infos = [CardImageInfo(frame_supertype, side, frame_subtype, should_be_modified=True, special_card_modifier=frame_modifier) for side, frame_subtype in zip(valid_sides, frame_subtypes) for frame_supertype in frame_supertypes]
    else:
        # You have exactly 1 subtype -> we don't need to combine card frames
        infos = [CardImageInfo(frame_supertype, "", frame_subtypes[0], should_be_modified=False, special_card_modifier=frame_modifier) for frame_supertype in frame_supertypes]

    for i, info in enumerate(infos):
        if "adventureleft" in info.file_prefix:
            infos[i].position_on_card = (0.045, 0.625)
        elif "adventureright" in info.file_prefix:
            infos[i].position_on_card = (0.495, 0.625)

    return infos

def get_card_pt_image_info(card_data: Card) -> CardImageInfo:
    """
    Gives the image (in CardImageInfo representation) for a card's power/toughness
    """
    if not card_data.stats_are_power_toughness:
        return CardImageInfo("defense", "", "", should_be_modified=False, special_card_asset_name_mode=True)

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
    """
    Gives the image (in CardImageInfo representation) for a card's set symbol based on the card's rarity.
    """
    return CardImageInfo(f"set_symbol_{card_data.rarity_name}", "", "", should_be_modified=False, special_card_asset_name_mode=True)

def card_image_draw_title_and_mana_cost(card_data, card_image_total, max_manacost_text_dims,
                                        text_font_size, mana_font_size, title_position_offset,
                                        total_mana_cost_and_title_width,
                                        adventure_mode=False, debug_mode=False):
    # When templating, we prefer to shrink the title before the mana cost.
    # Therefore we'll try to fit the title in the space left by the manacost.
                                        
    # === Manacost ===
    # First find the mana cost's width at the current font
    mana_cost_segments, _, _= LineSegment.split_text_for_symbols(
        card_data.raw_mana_cost_string.lower(), card_image_total, 10000, 10000,
        Fonts.title_text_font_name, Fonts.symbols_font_name, text_font_size, mana_font_size
    )
    mana_cost_segments: list[LineSegment] = mana_cost_segments
    num_mana_pips = len(mana_cost_segments)

    _total_manacost_width = sum(segment.dims[0] for segment in mana_cost_segments)

    _right_border = CARD_IMAGE_RIGHT_MANA_BORDER_ADVENTURE if adventure_mode else CARD_IMAGE_RIGHT_MANA_BORDER_NORMAL_CARD
    if num_mana_pips > 0:    
        _margin = 0 #int(mana_pip_width * 0.1)
        _left_mana_border = _right_border - _total_manacost_width - (_margin * (num_mana_pips-1))
        _yoffset: int = MANACOST_YOFFSET_PIXELS_ADVENTURE if adventure_mode else MANACOST_YOFFSET_PIXELS
        _total_manacost_width_drawn: float = 0
        for segment in mana_cost_segments:
            segment.draw(card_image_total, ((_left_mana_border + _total_manacost_width_drawn), _yoffset), absolute_draw_mode=True, mana_cost_mode=True)
            _total_manacost_width_drawn += segment.dims[0] + _margin
    
    # === Title ===
    chosen_title_font = Fonts.get_title_font(text_font_size)

    # Note that the total manacost width drawn includes an extra _margin. We're ok with that natural buffer.
    space_remaining_for_title = total_mana_cost_and_title_width - _total_manacost_width_drawn
    # Find the title font size
    title_string_width, _ = Fonts.get_string_size(card_data.name, chosen_title_font)
    if title_string_width > space_remaining_for_title:
        current_title_width_to_space_ratio = space_remaining_for_title / title_string_width
        # if debug_mode:
            # print(current_title_width_to_space_ratio)
            # print(card_data.name)
        chosen_title_font = Fonts.get_title_font(text_font_size * current_title_width_to_space_ratio)
    
    title_color: tuple[int, int, int] = C_WHITE if (card_data.is_token or adventure_mode) else C_BLACK
    title_text: str = card_data.name.upper() if card_data.is_token else card_data.name
    title_position: tuple[int, int] = math_utils.add_tuples(title_position_offset, TOKEN_TITLE_OFFSET_PIXELS if card_data.is_token else (0, 0))
    ImageDraw.Draw(card_image_total).text(
        title_position, title_text, title_color, font=chosen_title_font, anchor=("mm" if card_data.is_token else "lm")
    )
    
    

def card_image_draw_body_text(card_data, card_image_total,
                              warn_about_card_semantics_errors=False, verbose_mode_cards=False):
    # Go through each line of text and convert it into a series of LineSegments - each with their own font, offset, and text
    # Then draw each of their texts on the card at their offset and with their font

    # To maximize utilized card space and potentially accomodate flavor text, we impose the following basic rules:
    # Card text fits before flavor text fits
    # Strive for at most 9 lines of body text, not including flavor text.
    # Now the method: TODO Make a better one to accomodate for flavor text that won't be blocked by the power/toughness
    # Calculate how much space the body text'll take up with the flavor. It they take up more than the space
    # between the top and where the stat box is (if it has one; otherwise until end of card), then
    # calculate what proportion is needed to apply to the pips'/text's fonts.
    # If you can't fit both in 9 lines, try again without the flavor text.

    # How do we calculate the new proportion?
    # For now a naive binary search approach will do. 
    # If you took more than 9 lines, go between min font size (minFS) and current size.
    # Then if that's less than 9 lines, go halfway between that and the last size, and so on until some MAX_ATTEMPTS.

    is_adventure_right = card_data.related_nontoken_pair_card is not None
    is_adventure_left = card_data.is_adventure
    adventure_mode = is_adventure_left or is_adventure_right
    _font_size_factor = Fonts.ADVENTURE_FONT_SIZE_FACTOR if adventure_mode else 1

    max_text_width, max_text_height = BODY_TEXT_MAX_DIMS_ADVENTURE if adventure_mode else BODY_TEXT_MAX_DIMS_NORMAL_CARD

    text_font_size = Fonts.font_title_initial_size
    mana_font_size = Fonts.font_symbols_initial_size

    total_card_body_text: str = card_data.body_text #+ ("\n" + card_data.flavor_text if len(card_data.flavor_text) > 0 else "")
    segments, went_over_line_limit, _ = LineSegment.split_text_for_symbols(
                        total_card_body_text, card_image_total, 
                        max_text_width, max_text_height, 
                        Fonts.body_text_font_name, Fonts.symbols_font_name, 
                        text_font_size * _font_size_factor, mana_font_size * _font_size_factor
                        )
    segments: list[LineSegment] = segments # For type hinting :,-)
    current_font_size = text_font_size
    current_mana_font_size = Fonts.font_symbols_initial_size
    current_font_max, current_font_min = Fonts.font_body_max_size, Fonts.font_body_min_size

    body_text_too_large = went_over_line_limit
    tries = 8
    more_than_max_lines = False

    # TODO: we could also try making text larger than normal, but so long as the initial text size is reasonable we don't need to
    # for now this just corrects for too-large bodies of text
    if went_over_line_limit:
        if warn_about_card_semantics_errors:
            log_and_print(f"{card_data.name}'s text is too large for default font size. Resizing...", do_print=verbose_mode_cards)
        while tries > 1 or (tries == 1 and body_text_too_large):
            # print(body_text_too_large)
            if body_text_too_large:
                current_font_max = current_font_size
            else:
                current_font_min = current_font_size

            current_font_size = (current_font_min + current_font_max) / 2

            ratio_from_max_to_current = current_font_size / Fonts.font_body_max_size
            current_mana_font_size = Fonts.font_symbols_initial_size * ratio_from_max_to_current
            
            segments, body_text_too_large, more_than_max_lines = LineSegment.split_text_for_symbols(
                    total_card_body_text, card_image_total, 
                    BODY_TEXT_MAX_DIMS_NORMAL_CARD[0], BODY_TEXT_MAX_DIMS_NORMAL_CARD[1],
                    Fonts.body_text_font_name, Fonts.symbols_font_name, 
                    current_font_size * _font_size_factor, current_mana_font_size * _font_size_factor
                    )

            tries -= 1
            # print(card_data.name)
            # print(f"{tries: <5}, {body_text_too_large: <5}, {current_font_max: <5}, {current_font_min: <5}, {current_font_size: <5}")

    if more_than_max_lines and warn_about_card_semantics_errors:
        log_and_print(f"{card_data.name}'s text was was more than {LineSegment.MAX_LINE_COUNT} even at the smallest font.", do_print=verbose_mode_cards)

    body_text_position: tuple[int, int] = math_utils.add_tuples(BODY_TEXT_OFFSET_NORMAL_CARD, (0, token_yoffset) if card_data.is_token else (0, 0))
    if is_adventure_left:
        body_text_position = BODY_TEXT_OFFSET_ADVENTURE_LEFT
    elif is_adventure_right:
        body_text_position = BODY_TEXT_OFFSET_ADVENTURE_RIGHT

    for segment in segments:
        segment.draw(card_image_total, body_text_position)

def card_image_draw_types_text(card_data: Card, card_image_total, adventure_mode=False):
    _font = Fonts.get_title_font(Fonts.font_types_initial_size * (Fonts.ADVENTURE_FONT_SIZE_FACTOR if adventure_mode else 1))
    _max_types_string_width = MAX_TYPES_STRINGS_WIDTH_ADVENTURE_IN_PIXELS if adventure_mode else MAX_TYPES_STRING_WIDTH_IN_PIXELS

    types_string = card_data.get_type_string()

    types_string_width, _ = Fonts.get_string_size(types_string, _font)
    # print(f"Name: {card_data.name} | Width: {types_string_width}")
    if types_string_width > _max_types_string_width:
        current_types_width_to_max_width_ratio = _max_types_string_width / types_string_width
        _font = Fonts.get_title_font(_font.size * current_types_width_to_max_width_ratio)

    types_string_xoffset = (CARD_PIXEL_DIMS[0] * 40 / 500)
    types_string_yoffset: float = TYPES_STRING_OFFSET_Y_PIXELS + (token_yoffset if card_data.is_token else 0)
    if adventure_mode:
        types_string_xoffset = (CARD_PIXEL_DIMS[0] * 37 / 500)
        types_string_yoffset = round(CARD_PIXEL_DIMS[1] * 490 / 700)
        
    ImageDraw.Draw(card_image_total).text(
        (types_string_xoffset, types_string_yoffset), card_data.get_type_string(), C_WHITE if adventure_mode else C_BLACK, font=_font, anchor="lm"
    )

def generate_card_images(card_dict: dict[str, Card], images_save_filepath: str, image_assets: dict[CardImageInfo, Image]):
    verbose_mode_cards = metadata.settings_data_obj["card_semantics_settings"]["verbose_mode_cards"]
    warn_about_card_semantics_errors = metadata.settings_data_obj["card_semantics_settings"]["warn_about_card_semantics_errors"]

    num_cards_total = len(card_dict)
    current_card_index = 0

    for card_data in card_dict.values():
        related_adventure_spell_data = None # If you're an adventure spell for example, to store the base card

        if card_data.is_adventure:
            continue

        try:
            if len(card_data.related_card_names) == 1 and card_dict[card_data.related_card_names[0]].is_adventure:
                related_adventure_spell_data = card_dict[card_data.related_card_names[0]]

            card_image_total = Image.new(mode="RGB", size=CARD_PIXEL_DIMS, color=C_WHITE).convert("RGBA")

            # Card Base
            card_border_info: list[CardImageInfo] = get_card_image_border_info(card_data)
            for border_info in card_border_info:
                pos = math_utils.multiply_tuples(border_info.position_on_card, CARD_PIXEL_DIMS)
                card_image_total.alpha_composite(image_assets[border_info.file_prefix], dest=(round(pos[0]), round(pos[1])))

            if related_adventure_spell_data:
                adventure_border_info: list[CardImageInfo] = get_card_image_border_info(related_adventure_spell_data)
                for border_info in adventure_border_info:
                    pos =  math_utils.multiply_tuples(border_info.position_on_card, CARD_PIXEL_DIMS)
                    card_image_total.alpha_composite(image_assets[border_info.file_prefix], dest=(round(pos[0]), round(pos[1])))


            # Power/Toughness
            if card_data.has_stats:
                card_image_total.alpha_composite(image_assets[get_card_pt_image_info(card_data).file_prefix])

            # Set Symbol
            card_image_total.alpha_composite(image_assets[get_card_set_symbol_info(card_data).file_prefix],
                                            dest=(0, token_yoffset if card_data.is_token else 0))

            # Name and Manacost #################################################
            card_image_draw_title_and_mana_cost(card_data, card_image_total, 
                                                MAX_MANACOST_TEXT_DIMS, 
                                                Fonts.font_title_initial_size, Fonts.font_symbols_big_initial_size,
                                                TITLE_OFFSET_BASE_PIXELS, MAX_TITLE_AND_MANACOST_STRING_WIDTH_IN_PIXELS)

            if related_adventure_spell_data:
                card_image_draw_title_and_mana_cost(related_adventure_spell_data, card_image_total, 
                                                MAX_MANACOST_TEXT_DIMS, 
                                                Fonts.font_title_initial_size * Fonts.ADVENTURE_FONT_SIZE_FACTOR, 
                                                Fonts.font_symbols_big_initial_size * Fonts.ADVENTURE_FONT_SIZE_FACTOR,
                                                TITLE_OFFSET_BASE_ADVENTURE_PIXELS, round(0.35 * CARD_PIXEL_DIMS[0]),
                                                adventure_mode=True)

            # END Name and mana cost #################################################

            # Types ##########################
            card_image_draw_types_text(card_data, card_image_total)
            if related_adventure_spell_data:
                card_image_draw_types_text(related_adventure_spell_data, card_image_total, adventure_mode=True)

            # Body text
            card_image_draw_body_text(card_data, card_image_total,
                              warn_about_card_semantics_errors=warn_about_card_semantics_errors, verbose_mode_cards=verbose_mode_cards)
            if related_adventure_spell_data:
                card_image_draw_body_text(related_adventure_spell_data, card_image_total,
                    warn_about_card_semantics_errors=warn_about_card_semantics_errors, verbose_mode_cards=verbose_mode_cards)
                
            # Draw power/toughness or analogous stat (loyalty, defense, etc.)
            if card_data.has_stats:
                _stats_color = C_BLACK if card_data.stats_are_power_toughness else C_WHITE
                _stats_position = math_utils.add_tuples(CARD_IMAGE_POWER_TOUGHNESS_POSITION,
                                        (0, 0) if card_data.stats_are_power_toughness else (-3  * CARD_PIXEL_DIMS[0]/500, 0)) 
                ImageDraw.Draw(card_image_total).text(
                    _stats_position, card_data.get_stats_string(), _stats_color, Fonts.font_stats, anchor="mm"
                )
            
            rgb_image = card_image_total.convert("RGB")

            try:
                corresponding_filepath: str = images_save_filepath
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

def initialize_card_image_assets(assets_filepath: dict[str, str]) -> dict[str, Image]:
    """
    Initializes a bunch of card images from a few base images.
    That is, it resizes each to be at same size, masks colored borders halfway to make hybrid cards later,
    and saves these images to be used later so we don't need to invoke this heavy operation every time
    ChickenSnake is run.

    For now, this is just:
    For each normal card type frame, prepare half-frames of each color and card supertype.
    Save them all that the same size and the correct format for superimposing on one another.
    """
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
    card_frame_type = ["normal", "enchantment"]
    splittable_overlays = ["miracle"]
    unsplittable_overlays = ["miracle"]
    adventure_image_data = ["adventureleft", "adventureright"]
    one_off_card_subtypes = ["vehicle"]
    special_card_modifiers = ["", "token"]

    image_prefixes  = [CardImageInfo(frame, side, color, should_be_modified=True, special_card_modifier=modifier) for frame in card_frame_type for side in ["l", "r"] for color in splittable_card_prefixes for modifier in special_card_modifiers]
    image_prefixes += [CardImageInfo(frame_supertype, "", frame_subtype, should_be_modified=False, special_card_modifier=modifier) for frame_supertype in card_frame_type for frame_subtype in unsplittable_card_prefixes for modifier in special_card_modifiers]
    
    # Generic overlays 
    image_prefixes += [CardImageInfo(frame_supertype, side, frame_subtype, should_be_modified=True) for frame_supertype in splittable_overlays for side in ["l", "r"] for frame_subtype in splittable_card_prefixes]
    image_prefixes += [CardImageInfo(frame_supertype, "", frame_subtype, should_be_modified=False) for frame_supertype in unsplittable_overlays for frame_subtype in unsplittable_card_prefixes]
    
    # Adventures
    image_prefixes += [CardImageInfo(frame_supertype, side, frame_subtype, should_be_modified=True) for frame_subtype in splittable_card_prefixes for side in ["l", "r"] for frame_supertype in adventure_image_data]
    image_prefixes += [CardImageInfo(frame_supertype, "", frame_subtype, should_be_modified=False) for frame_subtype in unsplittable_card_prefixes for frame_supertype in adventure_image_data]

    image_prefixes += [CardImageInfo("pt", "", frame_subtype, should_be_modified=False) for frame_subtype in splittable_card_prefixes + unsplittable_card_prefixes + one_off_card_subtypes]
    image_prefixes += [CardImageInfo(f"set_symbol_{rarity}", "", "", should_be_modified=False, special_card_asset_name_mode=True) for rarity in ["common", "uncommon", "rare", "mythic"]]
    image_prefixes += [CardImageInfo("defense", "", "", should_be_modified=False, special_card_asset_name_mode=True)]

    # Random card art generation assets
    # @TODO add prefixes given that they're in a separate folder
    # image_prefixes += [CardImageInfo("character", "", art_number, should_be_modified=False) for art_number in range(1, 3 + 1)]
    # image_prefixes += [CardImageInfo("fx", "", art_number, should_be_modified=False) for art_number in range(1, 3 + 1)]
    # image_prefixes += [CardImageInfo("large_fx", "", art_number, should_be_modified=False) for art_number in range(1, 2 + 1)]

    # If the card is one that needs masking and splitting, it's marked as such 
    image_suffix: str = "_base.png"
    hybrid_card_mask_image: Image = None
    hybrid_card_masks: dict[str, Image] = {}
    try:
        hybrid_card_mask_image = Image.open(assets_filepath["pre-set"] + "hybrid_card_mask.png")
        hybrid_card_mask_image = hybrid_card_mask_image.resize(CARD_PIXEL_DIMS).convert("RGBA")
        # Adventure pages mask
        _factor = 1
        adventure_pixel_dims: tuple[int, int] = (round(CARD_PIXEL_DIMS[0] * 0.9197 * 0.5 * _factor), round(CARD_PIXEL_DIMS[1] * 0.32 * _factor))
        hybrid_adventure_mask_image = hybrid_card_mask_image.resize(adventure_pixel_dims)

        hybrid_card_masks["l"] = hybrid_card_mask_image
        hybrid_card_masks["r"] = hybrid_card_mask_image.transpose(Image.FLIP_LEFT_RIGHT)
        hybrid_card_masks["l_adventure"] = hybrid_adventure_mask_image
        hybrid_card_masks["r_adventure"] = hybrid_adventure_mask_image.transpose(Image.FLIP_LEFT_RIGHT)

    except:
        raise ValueError("There was a problem accessing the transparency mask.")

    for prefix in image_prefixes:
        image_info: CardImageInfo = prefix
        base_folder_path: str = assets_filepath["generated" if image_info.should_be_modified else "pre-set"]
        expected_image_filepath = base_folder_path + image_info.file_prefix + image_suffix
        image_info.filepath = expected_image_filepath
        try:
            is_adventure_card_image: bool = "adventure" in prefix.file_prefix
            if not image_info.should_be_modified:
                # If the image isn't to be modified to generate new card borders, it should exist
                # ... and we just need to resize it and hold it in memory
                log_and_print(f"Accessing base file to simply load it into memory {expected_image_filepath}", do_print=verbose_mode_files)
                base_image: Image = Image.open(expected_image_filepath)
                resized_image = base_image.resize(adventure_pixel_dims if "adventure" in prefix.file_prefix else CARD_PIXEL_DIMS)
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
                    resized_image: Image = None
                    if is_adventure_card_image:
                        hybrid_mask = hybrid_card_masks[f"{image_info.side}_adventure"]
                        resized_image = base_image.resize(adventure_pixel_dims)
                    else:
                        hybrid_mask = hybrid_card_masks[image_info.side]
                        resized_image: Image = base_image.resize(CARD_PIXEL_DIMS)
                        
                    masked_image = ImageChops.multiply(resized_image, hybrid_mask)
                    resized_images[image_info.file_prefix] = masked_image
                    # Save the image so we don't need to generate it next time
                    masked_image.save(expected_image_filepath, quality=100)
                else:
                    log_and_print(f"Generated file {base_image_filepath} already exists! Simply loading/resizing.", do_print=verbose_mode_files)
                    loaded_image = Image.open(expected_image_filepath)
                    resized_image: Image = loaded_image.resize(adventure_pixel_dims if is_adventure_card_image else CARD_PIXEL_DIMS)
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

def get_markdown_file_header_strings(version_code, set_code, set_longname, release_date):
    header_string = \
f"""<?xml version="{version_code}" encoding="UTF-8"?>
<cockatrice_carddatabase version="3">
<sets>
<set>
<name>{set_code}</name>
<longname>{set_longname}</longname>
<releasedate>{release_date}</releasedate>
<settype>Custom</settype>
</set>
</sets>
<cards>
"""

    header_string_tokens = \
f"""<?xml version="{version_code}" encoding="UTF-8"?>
<cockatrice_carddatabase version="3">
<cards>
<!-- 
<card>
    <name></name>
    <set picURL=""></set>
    <color></color>
    <manacost></manacost>
    <type>Token Creature - </type>
    <pt>/</pt>
    <tablerow>1</tablerow>
    <text></text>
    <token>1</token>
</card>
    -->
"""

    return header_string, header_string_tokens

def generate_markdown_file(markdown_filepath: dict[str, str], 
                           cards_dict: dict[str: Card],
                           header_string: dict[str, str],
                           closer_string: dict[str, str],
                           set_code: str):
    """
    Generates the files used by Cockatrice to represent its cards.
    They're Markdown (XML) files that store everything needed to play with a card,
    even if you don't have a pretty image to represent it.
    """
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
    <type>{card.get_type_string()}</type>{"" if card.stats is None else f"{chr(10) + chr(9)}<pt>{card.get_stats_string()}</pt>"}
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
    <type>Token {card.get_type_string()}</type>{"" if card.stats is None else f"{chr(10) + chr(9)}<pt>{card.get_stats_string()}</pt>"}
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
    """
    Generates a text file for Draftmancer to use in drafting.
    Defines basic rarity parameters based on those in the user-defined settings, lists 
    the cards sorted by rarity, and gives each one an image URL to display from while drafting.
    """
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

            # Add a comma at the end of each line that isn't the last one
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

