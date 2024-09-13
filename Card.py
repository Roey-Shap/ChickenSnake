from LineSegment import hybrid_pips_with_non_wubrg_order_colors, font_symbols_map_init
import metadata
import UI
from LineSegment import scryfall_hybrid_format

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
        self.is_colorless = len(colors) == 0
        self.colors_string = self.colors
        self.converted_manacost = converted_manacost
        self.manacost = manacost
        self.raw_mana_cost_string = raw_mana_cost_string
        self.split_mana_pips: list[str] = list(filter(None, [symbol.strip("{") for symbol in self.raw_mana_cost_string.split("}")]))
        found_manacost_error = False
        order_checked_pips = []
        for pip in self.split_mana_pips:
            found_manacost_error = True
            order_checked_pip = pip
            flipped_pip = pip.lower()[::-1]
            if '/' in pip and pip not in scryfall_hybrid_format:
                order_checked_pip = flipped_pip
                if metadata.warn_about_card_semantics_errors:
                    # UI.log_and_print(f"{name}: {pip}", do_print=metadata.verbose_mode_cards)
                    UI.log_and_print(f"Correcting manacost hybrid pip order: {pip}", do_print=metadata.verbose_mode_cards)
            order_checked_pips.append("{" + order_checked_pip + "}")

        self.draftmancer_cost = "".join(order_checked_pips).upper()

        # Pure hybrid cards are those that can be played for only 2 or 3 colors and all of the pips are hybrid or whole of those colors
        is_two_or_three_color = 2 <= len(self.colors) <= 3
        has_only_those_colors = all(set(pip.strip('p/')).issuperset(set(self.colors.lower())) for pip in filter(lambda pip: not pip.isnumeric(), self.split_mana_pips))
        has_hybrid_pip = any(pip.find('/') != -1 for pip in self.split_mana_pips)
        self.is_pure_hybrid = is_two_or_three_color and has_only_those_colors and (has_hybrid_pip or len(self.raw_mana_cost_string) == 0)
        self.is_gold = len(self.colors) >= 2 and not self.is_pure_hybrid
        if self.is_gold:
            self.colors_string = "M"
        if self.is_colorless:
            self.colors_string = ""

        self.supertype = supertype
        self.subtype = subtype
        self.rarity = rarity
        rarities = {"c": "common", "u": "uncommon", "r": "rare", "m": "mythic"}
        self.rarity_name = rarities[self.rarity]

        self.stats = stats
        self.has_stats = self.stats is not None
        self.body_text = body_text
        self.flavor_text = flavor_text
        
        self.found_manacost_error = found_manacost_error

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
        "mana_cost":  "{self.draftmancer_cost}",
        "type":  "{self.supertype}",
        "image_uris":  {{
                            "en":  "{uploaded_images_base_url}{self.name}.{card_picture_file_format}"
                        }}
    }}"""
        return final_string