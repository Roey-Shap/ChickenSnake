class Card():
    def __init__(self,
                name: str,
                colors: str,
                manacost: str,
                raw_mana_cost_string: str,
                converted_manacost: int,
                supertype: str,
                subtype: str,
                rarity: str,
                stats: tuple[int, int] | None,
                body_text: str,
                flavor_text: str
                ) -> None:

        self.name = name.replace("?", "").strip() # Would honestly be better to properly clean names of filepath-illegal characters but whatevs

        self.colors = colors
        # self.is_gold = len(colors) >= 3
        self.is_colorless = len(colors) == 0
        self.colors_string = self.colors
        # if self.is_gold:
        #     self.colors_string = "M"
        # elif self.is_colorless:
        #     self.colors_string = ""

        self.converted_manacost = converted_manacost
        self.manacost = manacost
        self.raw_mana_cost_string = raw_mana_cost_string
        self.split_mana_pips: list[str] = list(filter(None, [symbol.strip("{") for symbol in self.raw_mana_cost_string.split("}")]))
        # Pure hybrid cards are those that can be played for only 2 or 3 colors and all of the pips are hybrid or whole of those colors
        is_two_or_three_color = 2 <= len(self.colors) <= 3
        has_only_those_colors = all(len(set(pip.strip('p/')).difference(set(self.colors))) == 0 for pip in self.split_mana_pips)
        has_hybrid_pip = any(pip.find('/') != -1 for pip in self.split_mana_pips)
        self.is_pure_hybrid = is_two_or_three_color and has_only_those_colors and has_hybrid_pip
        self.is_gold = len(self.colors) >= 2 and not self.is_pure_hybrid
        if self.is_gold:
            self.colors_string = "M"
        if self.is_colorless:
            self.colors_string = ""

        self.supertype = supertype
        self.subtype = subtype
        self.rarity = rarity

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
        "image_uris":  {{
                            "en":  "{uploaded_images_base_url}{self.name}.{card_picture_file_format}"
                        }}
    }}"""
        return final_string