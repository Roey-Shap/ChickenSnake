from PIL import Image, ImageFont, ImageDraw, ImageTk

title_text_font_name = "./Fonts/Beleren2016-Bold.ttf"
body_text_font_name = "./Fonts/mplantin.ttf"
body_text_italic_font_name = "./Fonts/mplantinit.ttf"
symbols_font_name = "./Fonts/MTG.TTF"

blank_image_dims = (3000, 3000)
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

def get_font(font_name: str, font_size: float) -> ImageFont.ImageFont:
    return ImageFont.truetype(font_name, font_size)

ADVENTURE_FONT_SIZE_FACTOR = 0.85
HYBRID_PIP_SIZE_FACTOR = 1.15

font_body_initial_size = 23
font_body_max_size = 25
font_body_min_size = 18
font_body           = ImageFont.truetype(body_text_font_name, font_body_initial_size)
font_body_italic    = ImageFont.truetype(body_text_italic_font_name, font_body_initial_size)
font_body_tiny = ImageFont.truetype(body_text_font_name, 18)

font_symbols_big_initial_size = 25
font_symbols_large_pip_bg = ImageFont.truetype(symbols_font_name, font_symbols_big_initial_size * 24/font_symbols_big_initial_size)
font_symbols_large = ImageFont.truetype(symbols_font_name, font_symbols_big_initial_size)
font_symbols_initial_size = 21
font_symbols_min_size = font_symbols_initial_size * font_body_min_size / font_body_initial_size
font_symbols = get_symbol_font(font_symbols_initial_size)

font_title_initial_size = 27
font_title_initial_size_adventure = font_title_initial_size * ADVENTURE_FONT_SIZE_FACTOR

font_types_initial_size = 24

font_stats = ImageFont.truetype(title_text_font_name, 27)
