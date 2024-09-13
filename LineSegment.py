from PIL import Image, ImageFont, ImageDraw, ImageTk
import re
import Fonts
import metadata
from UI import log_and_print
from math_utils import flatten, strings_have_overlap, add_tuples

font_symbols_map_init: dict[str, str] = \
{
   "w/u": "A",
   "w/b": "O",
   "w/r": "B",
   "w/g": "N",
   "u/b": "D",
   "u/r": "I",
   "u/g": "M",
   "b/r": "R",
   "b/g": "C",
   "r/g": "G",
   "r/b": "R",
   "p/w": "P",
   "p/u": "P",
   "p/b": "P",
   "p/r": "P",
   "p/g": "P",
   "p/c": "P",
   "2/w": "M",
   "2/u": "M",
   "2/b": "M",
   "2/r": "M",
   "2/g": "M",
   "ut": "q",
   "c": "s"
}

# wb, wu, ub, br, rg, gw
# wb, bg, gu, ur, rw, wu
# flipped ones are gw, gu, rw
hybrid_pips_with_non_wubrg_order_colors = ["w/g", "u/g", "w/r"]

# Now we'll just duplicate each entry 
font_symbols_map: dict[str, str] = {}
for key, value in font_symbols_map_init.items():
    flipped_key = key[-1] + '/' + key[0]
    if flipped_key in hybrid_pips_with_non_wubrg_order_colors:
        font_symbols_map[flipped_key] = value
    font_symbols_map[key] = value


color_code_map: dict[str: tuple[int, int, int]] = \
{
    'w': (220,215,183),
    'u': (191,225,249),
    'b': (210,210,210),
    'r': (248,172,142),
    'g': (176,215,220),
    'c': (201,197,194),
    '#': (0  ,0  ,0  ) 
}

C_PIP_BG = '#'
CHAR_PIP_BG = 'H'

class LineSegment():
    def __init__(self, text: str, 
                 font: ImageFont, offset: tuple[int, int],
                 is_symbol: bool, dims: tuple[int, int],
                 color: tuple[int, int, int]=(0, 0, 0)):
        self.text = text
        self.font = font
        self.font_secondary = None
        self.offset = offset
        self.is_symbol: bool = is_symbol
        self.color = color
        self.dims = dims
        self.spacing = 2
        if self.is_symbol and '/' in self.text and self.text not in font_symbols_map:
            self.text = self.text[::-1]

    def set_secondary_font(self, font):
        self.font_secondary = font
        return self

    def draw(self, image: Image, relative_offset: tuple[int, int], 
             absolute_draw_mode=False, mana_cost_mode=False):
        absolute_pos = (self.offset[0] + relative_offset[0], self.offset[1] + relative_offset[1])
        if absolute_draw_mode:
            absolute_pos = relative_offset

        # This'll be either base text font or the mana symbol font
        font = self.font
        symbol_font_bg = Fonts.font_symbols_pip_background
        if mana_cost_mode:
            font = Fonts.font_symbols_large
            symbol_font_bg = Fonts.font_symbols_large_pip_bg

        if self.is_symbol:
            if mana_cost_mode:
                bg_offset_position = add_tuples(absolute_pos, (-2, 2))
                draw_pip_color_background(C_PIP_BG, C_PIP_BG, bg_offset_position, image, symbol_font_bg)

            is_phyrexian = 'p' in self.text
            is_hybrid = '/' in self.text
            is_two_hybrid = '2' in self.text and is_hybrid
            is_numeric = self.text.isdecimal()
            color_text = self.text 
            # If the text is tap, colorless, or 'X', make the background colorless
            if strings_have_overlap("xct", self.text.lower()) or self.text.isdecimal():
                color_text = 'c'

            background_color = self.text.strip("p/")
            c1, c2 = None, None
            if is_phyrexian:
                c1, c2 = background_color, background_color
            elif is_two_hybrid:
                c1 = 'c'
                c2 = background_color.strip("2/")
            elif is_hybrid:
                if self.text in hybrid_pips_with_non_wubrg_order_colors:
                    c1, c2 = self.text[::-1].split('/')
                else:
                    c1, c2 = self.text.split('/')
            else:
                c1, c2 = color_text, color_text

            draw_pip_color_background(c1, c2, absolute_pos, image, symbol_font_bg)

            # Draw final symbol overlay
            symbol_string = ""
            if is_hybrid:
                symbol_string = font_symbols_map[self.text]
            elif is_numeric or strings_have_overlap("tx", self.text.lower()):
                symbol_string = self.text
            elif not strings_have_overlap('wubrg', self.text.lower()):
                symbol_string = font_symbols_map[color_text]
            else:
                symbol_string = self.text

            symbol_string_pos_offset = (-1, -1)
            if is_numeric:
                symbol_string_pos_offset = (0, 0)
            if not is_hybrid:
                symbol_string_pos_offset = (0, symbol_string_pos_offset[1])
            if not mana_cost_mode:
                if is_numeric:
                    symbol_string_pos_offset = (1, 0)
                else:
                    if is_hybrid:
                        symbol_string_pos_offset = (-0.5, 0)
                    else:
                        symbol_string_pos_offset = (1, 0)

            final_symbol_string_pos = add_tuples(absolute_pos, symbol_string_pos_offset)
            ImageDraw.Draw(image).text(
                final_symbol_string_pos, symbol_string, self.color, font, spacing=self.spacing
            )
        else:
            ImageDraw.Draw(image).text(
                absolute_pos, self.text, self.color, font, spacing=self.spacing
            )

    @staticmethod
    def tokenize_card_text(raw_text: str, debug_mode=False) -> list[str]:
        # if debug_mode:
        #     log_and_print(raw_text)
        rebracketed_newlines_replaced = (raw_text.replace("{", "<{").replace("}", "}>").replace('\n', "&#").split("#"))
        # if debug_mode:
        #     log_and_print(rebracketed_newlines_replaced)
        newlines_split = flatten([re.split(r"[<>]", split_piece) for split_piece in rebracketed_newlines_replaced])
        # if debug_mode:
        #     log_and_print(newlines_split)
        tokenized_strings = [string.replace(" ", " |") for string in newlines_split if len(string) > 0]
        # if debug_mode:
        #     log_and_print(tokenized_strings)
        return flatten(segment.split("|") for segment in tokenized_strings)

    @staticmethod
    def split_text_for_symbols(
        raw_text: str, image: ImageDraw.Image, 
        max_width: int, max_height: int, small_text_mode: bool=False, 
        debug_mode=False, font_override=None, get_bounding_box_mode=False):
        # Split text into bracketed tokens and normal strings
        # log_and_print(rebracketed_newlines_replaced)
        # log_and_print()
        # log_and_print(newlines_split)
        # log_and_print()
        tokenized_strings = LineSegment.tokenize_card_text(raw_text, debug_mode)
        line_segments = []
        max_lineheight_seen = 0
        current_x_offset = 0
        line_count = 1
        max_line_count = 9

        draw_context = ImageDraw.Draw(image)

        chosen_font_text = Fonts.font_body if not small_text_mode else Fonts.font_body_tiny
        chosen_font_symbols = Fonts.font_symbols if not small_text_mode else Fonts.font_symbols_small
        chosen_font_symbols_bg = Fonts.font_symbols_pip_background if not small_text_mode else Fonts.font_symbols_small_pip_background

        for raw_segment in tokenized_strings:
            if line_count > max_line_count and not small_text_mode and not get_bounding_box_mode:
                # log_and_print("===================")
                # log_and_print("going small!")
                # log_and_print("===================")
                return LineSegment.split_text_for_symbols(raw_text, image, max_width, max_height, small_text_mode=True)

            is_symbol = re.match(r"[{}]", raw_segment)
            string_bbox = None
            chosen_font = None
            parsed_text = ""
            # if debug_mode:
            #     log_and_print(raw_segment)
            if is_symbol:
                parsed_text = raw_segment.strip(r"{}")
                chosen_font = chosen_font_symbols
            else:
                parsed_text = raw_segment.replace("&", "")
                chosen_font = chosen_font_text

            if font_override:
                if get_bounding_box_mode:
                    chosen_font, chosen_font_symbols_bg, chosen_font_symbols_ACTUAL_BACKGROUND = font_override
                    if is_symbol:
                        chosen_font = chosen_font_symbols_bg
                        chosen_font_symbols_bg = chosen_font_symbols_ACTUAL_BACKGROUND
                else:
                    chosen_font, chosen_font_symbols_bg = font_override


            string_bbox = draw_context.multiline_textbbox(
                (current_x_offset, 0), 
                CHAR_PIP_BG if is_symbol else parsed_text,
                chosen_font
            )

            string_width = string_bbox[2] - string_bbox[0]
            string_height = string_bbox[3] - string_bbox[1]
            # log_and_print(string_width)

            if not is_symbol:
                max_lineheight_seen = max(max_lineheight_seen, string_height)

            adding_word_overruns = current_x_offset + string_width > max_width
            if adding_word_overruns:
                # log_and_print("OVERUN")
                current_x_offset = 0
                line_count += 1                

            new_segment: LineSegment = LineSegment(
                parsed_text.replace("&", ""), chosen_font, 
                (current_x_offset, line_count-1), is_symbol,
                (string_width, string_height)
            )
            new_segment.set_secondary_font(chosen_font_symbols_bg)

            line_segments.append(new_segment)

            current_x_offset += string_width

            # Account for in-text newlines
            if '&' in raw_segment:
                current_x_offset = 0
                line_count += metadata.card_line_height_between_abilities
            
        for segment in line_segments:
            segment.offset = (segment.offset[0], segment.offset[1] * max_lineheight_seen * metadata.card_line_height_normal)

        return line_segments, line_count > 9

def draw_pip_color_background(c1: str, c2: str, 
                              pos: tuple[int, int], image: Image, 
                              font: ImageFont.FreeTypeFont):
    
    ImageDraw.Draw(image).text(
        pos, CHAR_PIP_BG, color_code_map[c1.lower()], font
    )

    ImageDraw.Draw(image).text(
        pos, "J", color_code_map[c2.lower()], font
    )