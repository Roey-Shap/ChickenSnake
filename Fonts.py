from PIL import Image, ImageFont, ImageDraw, ImageTk

body_text_font_name = "./Fonts/mplantin.ttf"
symbols_font_name = "./Fonts/MTG.TTF"


font_body  = ImageFont.truetype(body_text_font_name, 22)
font_body_tiny = ImageFont.truetype(body_text_font_name, 18)

# There'll be three main sizes of symbol text:
# Small, medium, and large - and the CMC always uses the large one
font_symbols_small_pip_background = ImageFont.truetype(symbols_font_name, 17)
font_symbols_small = ImageFont.truetype(symbols_font_name, 20)
font_symbols_pip_background = ImageFont.truetype(symbols_font_name, 21)
font_symbols = ImageFont.truetype(symbols_font_name, 24)
font_symbols_large_pip_bg = ImageFont.truetype(symbols_font_name, 24)
font_symbols_large = ImageFont.truetype(symbols_font_name, 27)

font_title = ImageFont.truetype(body_text_font_name, 26)
font_title_small = ImageFont.truetype(body_text_font_name, 18)

font_types = ImageFont.truetype(body_text_font_name, 24)
font_types_small = ImageFont.truetype(body_text_font_name, 20)
font_types_tiny = ImageFont.truetype(body_text_font_name, 18)

font_stats = ImageFont.truetype(body_text_font_name, 30)