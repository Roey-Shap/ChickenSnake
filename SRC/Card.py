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
                flavor_text: str,
                is_token: bool
                ) -> None:

        self.name = name.replace("?", "").strip() # Would honestly be better to properly clean names of filepath-illegal characters but whatevs
        self.short_name = None
        
        self.is_token = is_token
        self.is_adventure = False

        self.colors = colors
        self.is_colorless = len(colors) == 0
        self.colors_string = self.colors
        self.converted_manacost = int(converted_manacost)
        self.manacost = manacost
        self.raw_mana_cost_string = raw_mana_cost_string
        self.split_mana_pips: list[str] = list(filter(None, [symbol.strip("{") for symbol in self.raw_mana_cost_string.split("}")]))
        found_manacost_error = False
        order_checked_pips = []
        self.corrected_pips = []
        for pip in self.split_mana_pips:
            order_checked_pip = pip
            flipped_pip = pip.lower()[::-1]
            if '/' in pip and pip not in scryfall_hybrid_format:
                order_checked_pip = flipped_pip
                self.corrected_pips.append(pip)
                found_manacost_error = True
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
        self.is_rarity_missing = len(rarity) == 0
        if self.is_rarity_missing:
            self.rarity = "c"
        rarities = {"c": "common", "u": "uncommon", "r": "rare", "m": "mythic"}
        self.rarity_name = rarities[self.rarity]

        self.stats = stats
        self.has_stats = self.stats is not None
        self.stats_are_power_toughness = isinstance(self.stats, tuple) if self.has_stats else False
        self.body_text = body_text
        self.is_miracle = "miracle" in body_text.lower()  # Obviously isn't always accurate but it's good enough for keeping iteration time low

        self.flavor_text = flavor_text
        
        self.found_manacost_error = found_manacost_error
        
        self.related_card_names: list[str] = []
        self.related_nontoken_pair_card: Card | None = None

    def set_related_card_name(self, card_name: str) -> None:
        self.related_card_names.append(card_name)
    
    def set_as_adventure(self, is_adventure: bool) -> None:
        self.is_adventure = is_adventure
    
    def set_short_name(self, short_name: str) -> None:
        self.short_name = short_name

    def get_type_string(self):
        final_string = self.supertype
        if len(self.subtype) > 0:
            final_string += " - " + self.subtype # — bugs Cockatrice out??

        return final_string

    def search_for_supertype_string(self, supertype: str) -> bool:
        return self.supertype.lower().find(supertype.lower()) != -1

    def get_stats_string(self) -> str:
        if not self.stats_are_power_toughness:
            return f"{self.stats}"
            
        star_char = "="     # We're using a font that doesn't necessary have * as the star character
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

    def get_related_cards_string(self) -> str:
        return "\n".join(f"<reverse-related>{name}</reverse-related>" for name in self.related_card_names)