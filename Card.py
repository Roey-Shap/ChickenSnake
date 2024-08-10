
class Card():
    def __init__(self,
                name: str,
                colors: str,
                manacost: str,
                converted_manacost: int,
                supertype: str,
                subtype: str,
                stats: tuple[int, int] | None,
                body_text: str,
                flavor_text: str
                ) -> None:
        self.name = name.replace("?", "") # Would honestly be better to properly clean names of filepath-illegal characters but whatevs
        self.colors = colors
        self.is_gold = len(colors) >= 3
        self.is_colorless = len(colors) == 0
        self.colors_string = self.colors
        if self.is_gold:
            self.colors_string = "M"
        elif self.is_colorless:
            self.colors_string = ""
        self.manacost = manacost
        self.converted_manacost = converted_manacost
        self.supertype = supertype
        self.subtype = subtype
        self.stats = stats
        self.body_text = body_text
        self.flavor_text = flavor_text

    def get_type_string(self):
        final_string = self.supertype
        if len(self.subtype) > 0:
            final_string += " - " + self.subtype

        return final_string