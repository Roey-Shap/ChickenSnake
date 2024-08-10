from PIL import Image, ImageFont, ImageDraw, ImageTk
import re
from Fonts import body_text_font_name, symbols_font_name

font_body  = ImageFont.truetype(body_text_font_name, 22)
font_body_tiny = ImageFont.truetype(body_text_font_name, 16)

font_symbols = ImageFont.truetype(symbols_font_name, 22)
font_symbols_small = ImageFont.truetype(symbols_font_name, 18)

class LineSegment():
    def __init__(self, text: str, 
                 font: ImageFont, offset: tuple[int, int],
                 color: tuple[int, int, int]=(0, 0, 0)):
        self.text = text
        self.font = font
        self.offset = offset
        self.color = color
        self.spacing = 2

    def draw(self, image: Image, relative_offset: tuple[int, int]):
        ImageDraw.Draw(image).text(
            (self.offset[0] + relative_offset[0], self.offset[1] + relative_offset[1]), 
            self.text, self.color, self.font, spacing=self.spacing
        )

    @staticmethod
    def split_text_for_symbols(
        raw_text: str, image: ImageDraw.Image, 
        max_width: int, max_height: int, small_text_mode: bool = False):
        # Split text into bracketed tokens and normal strings
        rebracketed_newlines_replaced = (raw_text.replace("{", "<{").replace("}", "}>").replace('\n', "&#").split("#"))
        print(rebracketed_newlines_replaced)
        print()
        newlines_split = flatten([re.split(r"[<>]", split_piece) for split_piece in rebracketed_newlines_replaced])
        print(newlines_split)
        print()
        tokenized_strings = [string.replace(" ", " |") for string in newlines_split if len(string) > 0]
        line_segments = []
        max_lineheight_seen = 0
        current_x_offset = 0
        current_y_offset = 0
        line_count = 1
        max_line_count = 9

        draw_context = ImageDraw.Draw(image)

        chosen_font_text = font_body if not small_text_mode else font_body_tiny
        chosen_font_symbols = font_symbols if not small_text_mode else font_symbols_small

        for raw_segment in flatten(segment.split("|") for segment in tokenized_strings):
            # print(raw_segment)
            if line_count > max_line_count and not small_text_mode:
                print("===================")
                print("going small!")
                print("===================")
                return LineSegment.split_text_for_symbols(raw_text, image, max_width, max_height, small_text_mode=True)

            is_symbol = re.match(r"[{}]", raw_segment)
            string_bbox = None
            chosen_font = None
            parsed_text = ""
            if is_symbol:
                parsed_text = raw_segment.strip(r"{}")
                chosen_font = chosen_font_symbols
            else:
                parsed_text = raw_segment.replace("&", "")
                chosen_font = chosen_font_text

            string_bbox = draw_context.multiline_textbbox(
                (current_x_offset, current_y_offset), 
                parsed_text,
                chosen_font
            )
            string_width = string_bbox[2] - string_bbox[0]
            string_height = string_bbox[3] - string_bbox[1]
            print(string_width)

            max_lineheight_seen = max(max_lineheight_seen, string_height)

            adding_word_overruns = current_x_offset + string_width > max_width
            if adding_word_overruns:
                print("OVERUN")
                current_x_offset = 0
                current_y_offset += max_lineheight_seen
                line_count += 1                

            # Add the word in the proper place, given that 
            line_segments.append(LineSegment(
                parsed_text.replace("&", ""), chosen_font, (current_x_offset, line_count-1) 
            ))

            current_x_offset += string_width

            # Account for in-text newlines
            if '&' in raw_segment:
                print("NEWLINE")
                current_x_offset = 0
                current_y_offset += max_lineheight_seen
                line_count += 1
            
        for segment in line_segments:
            segment.offset = (segment.offset[0], segment.offset[1] * max_lineheight_seen)

        return line_segments

def flatten(xss):
    return [x for xs in xss for x in xs]