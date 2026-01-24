from dataclasses import dataclass

from CardData import scale_to_card_dims
import math_utils
from math_utils import Tupe

""" in the end we have: 
    alien, rodent, grazing animal, object, abstract, 
    warrior, beast, bird, cat, dog, mythic, fish, 
    robot, snake, egg, plant, dark, human
"""
creature_subtype_generalization: dict[str: list[str]] = \
{
    "alienish": 
    [
        "Aetherborn", 
        "Alien", 
        "Atog", 
        "Beholder", 
        "Carrier", 
        "Eldrazi", 
        "Eye", 
        "Hellion", 
        "Homarid",
        "Mite", 
        "Mutant", 
        "Necron", 
        "Phyrexian", 
        "Primarch", 
        "Spawn", 
        "Spider", 
    ],
    "rodentish":
    [
        "Armadillo", 
        "Badger", 
        "Beaver", 
        "Brushwagg", 
        "Capybara", 
        "Ferret", 
        "Hamster", 
        "Mole", 
        "Mongoose",
        "Mouse",  
        "Noggle",
        "Porcupine", 
        "Possum", 
        "Rabbit", 
        "Raccoon", 
        "Rat", 
        "Skunk", 
        "Sloth", 
        "Squirrel", 
        "Weasel", 
        "Wombat", 
        "Varmint", 

    ],
    "grazing":
    [
        "Antelope", 
        "Archon",   # special rule that adds wings?
        "Astartes", 
        "Camel", 
        "Caribou", 
        "Centaur", 
        "Elephant", 
        "Elf", 
        "Elk", 
        "Goat", 
        "Horse", 
        "Mount", 
        "Llama", 
        "Ox", 
        "Rhino", 
        "Unicorn", 
        "Sheep", 

    ],
    "objectish":
    [
        "Balloon", 
        "Orb", 
        "Prism", 
        "Sculpture", 
        "Toy", 
        "Wall", 
    ],
    "abstract":
    [
        "Blinkmoth", 
        "Elemental", 
        "Fractal", 
        "Germ", 
        "Glimmer",      # special rule to make them slightly transparent
        "Illusion",     # special rule to make them slightly transparent
        "Incarnation", 
        "Inkling", 
        "Nightmare", 
        "Nightstalker", 
        "Ooze", 
        "Weird", 
        "Nephilim", 
        "Reflection",  
        "Sand",             # adds a sanddune in the back...?
        "Spirit", 

    ],
    "warriorish": # Adds a helmet and sword to the base shape (default base shape is humanish)
    [
        "Archer", 
        "Assassin", 
        "Barbarian", 
        "Berserker", 
        "Custodes", 
        "Knight", 
        "Monger", 
        "Samurai", 
        "Soldier", 
        "Warrior", 
    ],
    "beastish":
    [
        "Bear", 
        "Beast", 
        "Boar", 
        "Bringer", 
        "Dinosaur", 
        "Hippo", 
        "Kavu", 
        "Lhurgoyf", 
        "Minotaur", 
        "Thrull", 
        "Yeti", 

    ],
    "birdish":
    [
        "Bat", 
        "Bird", 
        "Dragon",       
        "Drake", 
        "Insect",       # sure
        "Phoenix", 

    ],
    "catish":
    [
        "Cat", 
        "Otter", 
    ],
    "dogish":
    [
        "Coyote", 
        "Dog", 
        "Fox", 
        "Hyena", 
        "Jackal", 
        "Werewolf", 
        "Wolf", 
        "Wolverine", 

    ],
    "mythical":
    [
        "Aurochs", 
        "Basilisk", 
        "Chimera", 
        "Cockatrice", 
        "Gargoyle", 
        "Griffin", 
        "Hippogriff", 
        "Hydra", 
        "Manticore", 
        "Masticore", 
        "Lammasu", 
        "Pegasus", 
        "Phelddagrif", 
        "Sphinx", 

    ],
    "fishish":
    [
        "Camarid", 
        "Crab", 
        "Crocodile", 
        "Fish", 
        "Frog", 
        "Horror", 
        "Jellyfish", 
        "Kraken", 
        "Leviathan",        
        "Nautilus", 
        "Octopus", 
        "Oyster", 
        "Walrus", 
        "Whale", 
        "Sponge", 
        "Squid", 
        "Starfish", 
        "Shark", 
        "Tentacle", 
        "Trilobite", 
        "Turtle", 

    ],
    "robotish":
    [
        "Assembly-Worker", 
        "Construct", 
        "Cyberman", 
        "Dalek", 
        "Dreadnought", 
        "Drone", 
        "Golem", 
        "Juggernaut", 
        "Myr", 
        "Processor", 
        "Robot", 
        "Servo", 
        "Thopter", 

    ],
    "snakish":
    [
        "Worm", 
        "Wurm", 
        "Lamia", 
        "Leech", 
        "Lizard", 
        "Licid", 
        "Pangolin", 
        "Salamander",       
        "Serpent", 
        "Slug", 
        "Snail", 
        "Snake", 
    ],
    "eggish":
    [
        "Egg", 

    ],
    "plantish":
    [
        "Dryad",        
        "Fungus", 
        "Plant", 
        "Saproling", 
        "Treefolk", 
    ],
    "dark":
    [
        "Graveborn", 
        "Skeleton", 
        "Specter", 
        "Wraith", 
        "Vampire", 
        "Zombie", 
    ],
    "humanish": 
    [
        "Advisor", 
        "Ally", 
        "Angel",        # add wings
        "Ape", 
        "Army", 
        "Artificer", 
        "Avatar", 
        "Azra", 
        "Bard", 
        "Beeble",       # start 'small humanoids' group? Special rule to make it small?
        "Child",        # special rule to make it small
        "Citizen", 
        "Cleric", 
        "Clown", 
        "Coward", 
        "C’tan", 
        "Cyclops",      # special rule to give the face one eye
        "Dauthi", 
        "Demigod", 
        "Demon",        # special rule to give the base horns
        "Deserter", 
        "Detective",    # special rule to give the base a detective hat
        "Devil",        # special rule to give the base horns
        "Djinn",        # special rule to make the base sit on a cloud
        "Doctor",       # put a stethoscope on them?
        "Druid",        # put a wizard hat on base
        "Dwarf",        # make them 0.75 y-scale
        "Efreet",       # same as Djinn
        "Elder", 
        "Employee", 
        "Faerie",       # special rule to give the base wings
        "Flagbearer", 
        "Gamer", 
        "Giant",        # special rule to make it large
        "Gith", 
        "Gnoll", 
        "Gnome",        # special rule 0.75 y-scale
        "Goblin", 
        "God",          
        "Gorgon",       # special rule to add snakes on head
        "Gremlin",      
        "Guest", 
        "Hag", 
        "Halfling",     # special rule 0.75 y-scale
        "Harpy",        # speial rule to give the base wings
        "Homunculus",   # special rule 0.75 y-scale
        "Human", 
        "Imp", 
        "Inquisitor", 
        "Kirin", 
        "Kithkin",      # special rule 0.75 y-scale 
        "Kobold", 
        "Kor", 
        "Mercenary", 
        "Merfolk", 
        "Metathran", 
        "Minion", 
        "Monk", 
        "Monkey", 
        "Moonfolk", 
        "Mystic", 
        "Ninja", 
        "Noble", 
        "Nomad", 
        "Nymph", 
        "Orc", 
        "Orgg", 
        "Ogre", 
        "Ouphe", 
        "Peasant", 
        "Pentavite", 
        "Performer", 
        "Pilot",            # special rule to put them in a plane?
        "Pincher",      
        "Pirate",           # eyepatch?
        "Ranger",  
        "Rebel", 
        "Pest", 
        "Praetor", 
        "Rigger", 
        "Rogue", 
        "Sable", 
        "Satyr", 
        "Scarecrow", 
        "Scientist", 
        "Scion", 
        "Scorpion", 
        "Scout", 
        "Serf", 
        "Shade", 
        "Shaman", 
        "Shapeshifter", 
        "Siren", 
        "Slith", 
        "Sliver", 
        "Soltari", 
        "Spellshaper",      # put a wizard hat on base
        "Spike", 
        "Splinter", 
        "Surrakar", 
        "Survivor", 
        "Synth", 
        "Tetravite", 
        "Thalakos", 
        "Tiefling", 
        "Triskelavite", 
        "Troll", 
        "Tyranid", 
        "Vedalken", 
        "Volver", 
        "Warlock",          # put a wizard hat on base 
        "Wizard",           # put a wizard hat on base
        "Zubera"
        ]
}

def classify_creature(subtype: str) -> str:
    for creature_class in creature_subtype_generalization:
        if subtype.capitalize() in creature_subtype_generalization[creature_class]:
            return creature_class

    return "humanish"

def find_dominant_creature_class(subtypes: str) -> str:
    non_human_default: str = ""

    for subtype in subtypes.split(" "):
        for creature_class in creature_subtype_generalization:
            if subtype.capitalize() in creature_subtype_generalization[creature_class]:
                if classify_creature(subtype) != "humanish":
                    if subtype not in SubtypeImageModifier.modifier_subtypes:
                        return creature_class

    return "humanish"

class ImageElementBodyData():
    def __init__(self, head_offset: Tupe, 
                       eye_offset: Tupe,
                       head_scale: float,
                       back_offset: Tupe):
        # these values describe offsets from the center of the creature image 
        ELEMENT_HALF_DIMS = Tupe(200, 200).scale(0.5, do_round=True)
        Y_CORRECTION = Tupe(1, -1)
        self.head_offset: Tupe = head_offset * Y_CORRECTION
        self.eye_offset: Tupe = eye_offset * Y_CORRECTION
        self.head_scale: float = head_scale
        self.back_offset: Tupe = back_offset * Y_CORRECTION

creature_base_image_body_data_map = {
                                         # Head pos       # Eye pos  # Scale    # Back pos
    "humanish":     ImageElementBodyData(Tupe(-15,  80), Tupe(  0,  65), 1.00, Tupe(114, 109)),
    "alienish":     ImageElementBodyData(Tupe(120,  70), Tupe(120,  70), 0.55, Tupe(110, 117)),
    "rodentish":    ImageElementBodyData(Tupe( 61, 107), Tupe( 61, 107), 0.60, Tupe(111,  84)),
    "grazing":      ImageElementBodyData(Tupe(-45,  60), Tupe(-30,  85), 0.85, Tupe( 82, 118)),
    "objectish":    ImageElementBodyData(Tupe(101, 100), Tupe(101, 100), 1.00, Tupe(102, 122)),
    "abstract":     ImageElementBodyData(Tupe(143, 100), Tupe(143, 100), 0.70, Tupe( 75,  91)),
    "beastish":     ImageElementBodyData(Tupe(102,  82), Tupe(102,  82), 1.10, Tupe(120, 134)),
    "birdish":      ImageElementBodyData(Tupe( 82,  97), Tupe( 82,  97), 0.90, Tupe(117,  92)),
    "catish":       ImageElementBodyData(Tupe(-30,  60), Tupe(109,  77), 1.10, Tupe(149,  70)),
    "fishish":      ImageElementBodyData(Tupe( 58, 155), Tupe( 58, 155), 0.50, Tupe( 78,  97)),
    "dogish":       ImageElementBodyData(Tupe(101,  95), Tupe(101,  95), 1.20, Tupe( 96, 140)),
    "robotish":     ImageElementBodyData(Tupe( 94,  70), Tupe( 94,  70), 1.00, Tupe( 95, 104)),
    "snakish":      ImageElementBodyData(Tupe( 86,  71), Tupe( 86,  71), 0.50, Tupe(117,  81)),
    "eggish":       ImageElementBodyData(Tupe(101,  98), Tupe(101,  98), 0.80, Tupe(102, 130)),
    "plantish":     ImageElementBodyData(Tupe(108, 122), Tupe(108, 122), 0.80, Tupe( 98, 145)),
    "dark":         ImageElementBodyData(Tupe( 80,  80), Tupe( 80,  80), 1.10, Tupe(120,  92))
}

        
class SubtypeImageModifier:
    helmet_subtypes = [subtype.lower() for subtype in creature_subtype_generalization["warriorish"]]
    wing_subtypes = ["harpy", "faerie", "angel", "archon"]
    wizard_hat_subtypes = ["warlock", "wizard", "spellshaper", "druid"]
    eye_patch_subtypes = ["pirate"]
    horn_subtypes = ["devil", "demon"]
    on_cloud_subtypes = ["djinn", "efreet"]
    remove_eye_subtypes = ["cyclops"]
    short_subtypes = ["kithkin", "homunculus", "halfling", "gnome", "dwarf", "beeble", "child"]
    sanddune_subtypes = ["sand"]
    translucent_subtypes = ["glimmer", "illusion"]

    modifier_subtypes = helmet_subtypes + wing_subtypes + wizard_hat_subtypes + \
                        eye_patch_subtypes + horn_subtypes + on_cloud_subtypes + \
                        remove_eye_subtypes + short_subtypes + sanddune_subtypes + \
                        translucent_subtypes

    def __init__(self):
        self.helmet: bool = False
        self.wings: bool = False
        self.wizard_hat: bool = False
        self.eye_patch: bool = False
        self.horns: bool = False
        self.on_cloud: bool = False
        self.remove_eye: bool = False
        self.short: bool = False
        self.sanddune: bool = False
        self.translucent: bool = False


    def assign_modifiers_from_creature_subtypes(self, subtypes: list[str]):
        for subtype in subtypes:
            subtype = subtype.lower()
            self.helmet     |= subtype in SubtypeImageModifier.helmet_subtypes
            self.wings      |= subtype in SubtypeImageModifier.wing_subtypes 
            self.wizard_hat |= subtype in SubtypeImageModifier.wizard_hat_subtypes
            self.eye_patch  |= subtype in SubtypeImageModifier.eye_patch_subtypes
            self.horns      |= subtype in SubtypeImageModifier.horn_subtypes
            self.on_cloud   |= subtype in SubtypeImageModifier.on_cloud_subtypes
            self.remove_eye |= subtype in SubtypeImageModifier.remove_eye_subtypes
            self.short      |= subtype in SubtypeImageModifier.short_subtypes
            self.sanddune   |= subtype in SubtypeImageModifier.sanddune_subtypes
            self.translucent|= subtype in SubtypeImageModifier.translucent_subtypes
