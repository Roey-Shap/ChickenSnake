from PIL import Image, ImageFont, ImageDraw, ImageTk

title_text_font_name = "./Fonts/Beleren2016-Bold.ttf"
body_text_font_name = "./Fonts/mplantin.ttf"
body_text_italic_font_name = "./Fonts/mplantinit.ttf"
symbols_font_name = "./Fonts/MTG.TTF"

blank_image_dims = (3000,3000)
blank_image = Image.new(mode="RGB", size=blank_image_dims, color=(255,255,255)).convert("RGBA")
blank_draw_context = ImageDraw.Draw(blank_image)

def get_title_font(size: float) -> ImageFont.ImageFont:
    return ImageFont.truetype(title_text_font_name, size)

def get_body_font(size: float, italic: bool=False) -> ImageFont.ImageFont:
    return ImageFont.truetype(body_text_italic_font_name if italic else body_text_font_name, size)

def get_symbol_font(size: float) -> ImageFont.ImageFont:
    return ImageFont.truetype(symbols_font_name, size)

def get_string_size(text: str, font: ImageFont.ImageFont) -> tuple[float, float]:
    string_bbox = blank_draw_context.multiline_textbbox((500, 500), text, font)
    return (string_bbox[2] - string_bbox[0], string_bbox[3] - string_bbox[1])

font_body_initial_size = 23
font_body_max_size = 25
font_body_min_size = 18
font_body           = ImageFont.truetype(body_text_font_name, font_body_initial_size)
font_body_italic    = ImageFont.truetype(body_text_italic_font_name, font_body_initial_size)
font_body_tiny = ImageFont.truetype(body_text_font_name, 18)

# There'll be three main sizes of symbol text:
# Small, medium, and large - and the CMC always uses the large one
font_symbols_small_pip_background = ImageFont.truetype(symbols_font_name, 17)
font_symbols_small = ImageFont.truetype(symbols_font_name, 20)
font_symbols_pip_background = ImageFont.truetype(symbols_font_name, 21)
font_symbols = ImageFont.truetype(symbols_font_name, 24)
# 
font_symbols_big_initial_size = 25
font_symbols_large_pip_bg = ImageFont.truetype(symbols_font_name, font_symbols_big_initial_size * 24/font_symbols_big_initial_size)
font_symbols_large = ImageFont.truetype(symbols_font_name, font_symbols_big_initial_size)
font_symbols_initial_size = 21
font_symbols_min_size = font_symbols_initial_size * font_body_min_size / font_body_initial_size
font_symbols = get_symbol_font(font_symbols_initial_size)

font_title_initial_size = 27
font_title = ImageFont.truetype(title_text_font_name, font_title_initial_size)
font_title_small = ImageFont.truetype(body_text_font_name, 18)

font_types_initial_size = 24
font_types = ImageFont.truetype(title_text_font_name, font_types_initial_size)

font_types_small = ImageFont.truetype(title_text_font_name, 20)
font_types_tiny = ImageFont.truetype(title_text_font_name, 18)

font_stats = ImageFont.truetype(body_text_font_name, 30)
