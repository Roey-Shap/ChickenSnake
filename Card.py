
class Card():
    def __init__(self,
                name: str,
                colors: str,
                manacost: str,
                raw_mana_cost_string: str,
                converted_manacost: int,
                supertype: str,
                subtype: str,
                stats: tuple[int, int] | None,
                body_text: str,
                flavor_text: str
                ) -> None:
        self.name = name.replace("?", "").strip() # Would honestly be better to properly clean names of filepath-illegal characters but whatevs
        self.colors = colors
        self.is_gold = len(colors) >= 3
        self.is_colorless = len(colors) == 0
        self.colors_string = self.colors
        if self.is_gold:
            self.colors_string = "M"
        elif self.is_colorless:
            self.colors_string = ""
        self.manacost = manacost
        self.raw_mana_cost_string = raw_mana_cost_string
        self.converted_manacost = converted_manacost
        self.supertype = supertype
        self.subtype = subtype
        self.stats = stats
        self.has_stats = self.stats is not None
        self.body_text = body_text
        self.flavor_text = flavor_text

    def get_type_string(self):
        final_string = self.supertype
        if len(self.subtype) > 0:
            final_string += " - " + self.subtype

        return final_string

    def get_stats_string(self):
        star_char = "="
        power     = star_char if self.stats == "*" else self.stats[0] 
        toughness = star_char if self.stats == "*" else self.stats[1]
        return f"{power}/{toughness}"

    def get_draft_text_rep(self, uploaded_images_base_url: str, card_picture_file_format: str) -> str:
        final_string = \
    f"""
    {{
        "name":  "{self.name}",
        "mana_cost":  "{self.manacost}",
        "type":  "{self.supertype}",
        "rarity":  "rare",
        "image_uris":  {{
                            "en":  "{uploaded_images_base_url}{self.name}.{card_picture_file_format}"
                        }}
    }}"""
        return final_string