from PIL import Image, ImageFont, ImageDraw, ImageTk
import re
from Fonts import body_text_font_name, symbols_font_name

font_body  = ImageFont.truetype(body_text_font_name, 22)
font_body_tiny = ImageFont.truetype(body_text_font_name, 18)

font_symbols = ImageFont.truetype(symbols_font_name, 21)
font_symbols_small = ImageFont.truetype(symbols_font_name, 17)

font_symbols_map: dict[str, str] = \
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
   "2/w": "M",
   "2/u": "M",
   "2/b": "M",
   "2/r": "M",
   "2/g": "M",
   "ut": "q",
   "c": "s"
}

color_code_map: dict[str: tuple[int, int, int]] = \
{
    "w": (220,215,183),
    "u": (191,225,249),
    "b": (210,210,210),
    "r": (248,172,142),
    "g": (176,215,220),
    "c": (201,197,194)
}

class LineSegment():
    def __init__(self, text: str, 
                 font: ImageFont, offset: tuple[int, int],
                 is_symbol: bool, dims: tuple[int, int],
                 color: tuple[int, int, int]=(0, 0, 0)):
        self.text = text
        self.font = font
        self.offset = offset
        self.is_symbol: bool = is_symbol
        self.color = color
        self.dims = dims
        self.spacing = 2

    def draw(self, image: Image, relative_offset: tuple[int, int], 
             absolute_draw_mode=False, font_override=None):
        absolute_pos = (self.offset[0] + relative_offset[0], self.offset[1] + relative_offset[1])
        if absolute_draw_mode:
            absolute_pos = relative_offset
        font = font_override if font_override is not None else self.font

        if self.is_symbol:
            is_phyrexian = 'p' in self.text
            is_hybrid = '/' in self.text
            is_two_hybrid = '2' in self.text and is_hybrid
            color_text = self.text 
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
                c1, c2 = self.text.split('/')
            else:
                c1, c2 = color_text, color_text

            draw_pip_color_background(c1, c2, absolute_pos, image, font)

            # Draw final symbol overlay
            symbol_string = ""
            if is_hybrid:
                symbol_string = font_symbols_map[self.text]
            elif self.text.isdecimal() or strings_have_overlap("tx", self.text.lower()):
                symbol_string = self.text
            elif not strings_have_overlap('wubrg', self.text.lower()):
                symbol_string = font_symbols_map[color_text]
            else:
                symbol_string = self.text

            # print(self.font.getname())
            # print(symbol_string)
            ImageDraw.Draw(image).text(
                absolute_pos, symbol_string, self.color, font, spacing=self.spacing
            )
        else:
            ImageDraw.Draw(image).text(
                absolute_pos, self.text, self.color, font, spacing=self.spacing
            )

    @staticmethod
    def tokenize_card_text(raw_text: str, debug_mode=False) -> list[str]:
        if debug_mode:
            print(raw_text)
        rebracketed_newlines_replaced = (raw_text.replace("{", "<{").replace("}", "}>").replace('\n', "&#").split("#"))
        if debug_mode:
            print(rebracketed_newlines_replaced)
        newlines_split = flatten([re.split(r"[<>]", split_piece) for split_piece in rebracketed_newlines_replaced])
        if debug_mode:
            print(newlines_split)
        tokenized_strings = [string.replace(" ", " |") for string in newlines_split if len(string) > 0]
        if debug_mode:
            print(tokenized_strings)
        return flatten(segment.split("|") for segment in tokenized_strings)

    @staticmethod
    def split_text_for_symbols(
        raw_text: str, image: ImageDraw.Image, 
        max_width: int, max_height: int, small_text_mode: bool = False, 
        debug_mode=False, font_override=None):
        # Split text into bracketed tokens and normal strings
        # print(rebracketed_newlines_replaced)
        # print()
        # print(newlines_split)
        # print()
        tokenized_strings = LineSegment.tokenize_card_text(raw_text, debug_mode)
        line_segments = []
        max_lineheight_seen = 0
        current_x_offset = 0
        line_count = 1
        max_line_count = 9

        draw_context = ImageDraw.Draw(image)

        chosen_font_text = font_body if not small_text_mode else font_body_tiny
        chosen_font_symbols = font_symbols if not small_text_mode else font_symbols_small

        for raw_segment in tokenized_strings:
            if line_count > max_line_count and not small_text_mode:
                # print("===================")
                # print("going small!")
                # print("===================")
                return LineSegment.split_text_for_symbols(raw_text, image, max_width, max_height, small_text_mode=True)

            is_symbol = re.match(r"[{}]", raw_segment)
            string_bbox = None
            chosen_font = None
            parsed_text = ""
            if debug_mode:
                print(raw_segment)
            if is_symbol:
                parsed_text = raw_segment.strip(r"{}")
                chosen_font = chosen_font_symbols
            else:
                parsed_text = raw_segment.replace("&", "")
                chosen_font = chosen_font_text

            chosen_font = font_override if font_override is not None else chosen_font 

            string_bbox = draw_context.multiline_textbbox(
                (current_x_offset, 0), 
                parsed_text[0] if is_symbol else parsed_text,
                chosen_font
            )

            string_width = string_bbox[2] - string_bbox[0]
            string_height = string_bbox[3] - string_bbox[1]
            # print(string_width)

            max_lineheight_seen = max(max_lineheight_seen, string_height)

            adding_word_overruns = current_x_offset + string_width > max_width
            if adding_word_overruns:
                # print("OVERUN")
                current_x_offset = 0
                line_count += 1                

            # Add the word in the proper place, given that 
            line_segments.append(LineSegment(
                parsed_text.replace("&", ""), chosen_font, 
                (current_x_offset, line_count-1), is_symbol,
                (string_width, string_height)
            ))

            current_x_offset += string_width

            # Account for in-text newlines
            if '&' in raw_segment:
                current_x_offset = 0
                line_count += 1
            
        for segment in line_segments:
            segment.offset = (segment.offset[0], segment.offset[1] * max_lineheight_seen)

        return line_segments

def flatten(xss):
    return [x for xs in xss for x in xs]

def draw_pip_color_background(c1: str, c2: str, 
                              pos: tuple[int, int], image: Image, font: ImageFont.FreeTypeFont):
    
    pos = (pos[0] - 2, pos[1])
    ImageDraw.Draw(image).text(
        pos, "H", color_code_map[c1.lower()], font
    )
    ImageDraw.Draw(image).text(
        pos, "J", color_code_map[c2.lower()], font
    )

def strings_have_overlap(s1, s2):
    return len(set(s1).intersection(set(s2))) > 0