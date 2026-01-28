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
                if classify_creature(subtype) not in ["humanish", "warriorish"]:
                    if subtype not in SubtypeImageModifier.modifier_subtypes:
                        return creature_class

    return "humanish"

class ImageElementBodyData():
    def __init__(self, head_offset: Tupe, 
                       eye_offset: Tupe,
                       head_scale: float,
                       back_offset: Tupe):
        # these values describe offsets from the center of the creature image 
        IMAGE_CENTER_COORD = Tupe(200, 200).scale(0.5)
        Y_CORRECTION = Tupe(1, 1)
        self.head_offset: Tupe = (head_offset - IMAGE_CENTER_COORD) * Y_CORRECTION
        self.eye_offset: Tupe  = (eye_offset - IMAGE_CENTER_COORD) * Y_CORRECTION
        self.head_scale: float = head_scale
        self.back_offset: Tupe = (back_offset - IMAGE_CENTER_COORD) * Y_CORRECTION

creature_base_image_body_data_map = {
    # these ultimately represent offsets from the center of the creature image
    # but the coordinates fed into the objects is the actual coordinate of the head in the image
    # found simply by hovering over it in an image editor and then finetuned after seeing some images generated

    "humanish":     ImageElementBodyData(Tupe(  94,   60), Tupe(  94,   74), 1.00, Tupe(  92,  116)),
    "alienish":     ImageElementBodyData(Tupe( 120,   70), Tupe( 110,  117), 0.55, Tupe( 113,  121)),
    "rodentish":    ImageElementBodyData(Tupe(  62,   96), Tupe(  62,  106), 0.60, Tupe( 107,   92)),
    "grazing":      ImageElementBodyData(Tupe(  95,   70), Tupe(  82,  118), 0.85, Tupe(   0,    0)),
    "objectish":    ImageElementBodyData(Tupe( 101,  100), Tupe( 103,  124), 1.00, Tupe( 103,  124)),
    "abstract":     ImageElementBodyData(Tupe( 107,   63), Tupe(  73,   82), 0.70, Tupe( 132,   75)),
    "beastish":     ImageElementBodyData(Tupe( 110,   85), Tupe( 125,   65), 1.10, Tupe( 125,  138)),
    "birdish":      ImageElementBodyData(Tupe(  75,   85), Tupe(  75,  104), 1.50, Tupe( 111,   96)),
    "catish":       ImageElementBodyData(Tupe(  82,   97), Tupe(  78,   92), 0.90, Tupe( 138,  109)),
    "fishish":      ImageElementBodyData(Tupe(  73,  115), Tupe(  67,  107), 0.40, Tupe(  95,  101)),
    "dogish":       ImageElementBodyData(Tupe(  98,   82), Tupe(  98,  102), 1.20, Tupe(  97,  142)),
    "robotish":     ImageElementBodyData(Tupe(  94,   50), Tupe(  95,   66), 1.20, Tupe(  96,  102)),
    "snakish":      ImageElementBodyData(Tupe(  62,   60), Tupe(  80,   70), 0.50, Tupe( 120,   78)),
    "eggish":       ImageElementBodyData(Tupe( 100,   62), Tupe( 102,  112), 1.00, Tupe( 100,   83)),
    "plantish":     ImageElementBodyData(Tupe( 117,   88), Tupe( 108,  112), 0.80, Tupe( 101,  139)),
    "dark":         ImageElementBodyData(Tupe(  73,   75), Tupe(  75,   84), 1.10, Tupe( 122,  113)),
    "mythical":     ImageElementBodyData(Tupe( 102,   71), Tupe( 107,  102), 1.10, Tupe( 110,   85))

    #                                      # Head pos       # Eye pos  # Scale    # Back pos
    # "humanish":     ImageElementBodyData(Tupe(- 15,   80), Tupe(   0,   65), 1.00, Tupe(   0,     0)), #
    # "alienish":     ImageElementBodyData(Tupe(  20,   70), Tupe( 120,   70), 0.55, Tupe(   0,     0)),
    # "rodentish":    ImageElementBodyData(Tupe(  61,  107), Tupe(  61,  107), 0.60, Tupe(   0,     0)),
    # "grazing":      ImageElementBodyData(Tupe(- 45,   60), Tupe(- 30,   85), 0.85, Tupe(   0,     0)), #
    # "objectish":    ImageElementBodyData(Tupe( 101,  100), Tupe( 101,  100), 1.00, Tupe(   0,     0)),
    # "abstract":     ImageElementBodyData(Tupe( 143,  100), Tupe( 143,  100), 0.70, Tupe(   0,     0)),
    # "beastish":     ImageElementBodyData(Tupe( 102,   82), Tupe( 102,   82), 1.10, Tupe(   0,     0)),
    # "birdish":      ImageElementBodyData(Tupe(  82,   97), Tupe(  82,   97), 0.90, Tupe(   0,     0)),
    # "catish":       ImageElementBodyData(Tupe(- 30,   95), Tupe( 109,   77), 1.50, Tupe(   0,     0)), #
    # "fishish":      ImageElementBodyData(Tupe(- 55,   10), Tupe(- 65,    0), 0.40, Tupe(   0,     0)), #
    # "dogish":       ImageElementBodyData(Tupe( 101,   95), Tupe(  35, - 75), 1.20, Tupe(   0,     0)), #
    # "robotish":     ImageElementBodyData(Tupe(- 20,  120), Tupe(  10,  120), 1.20, Tupe(   0,     0)), #
    # "snakish":      ImageElementBodyData(Tupe(  86,   71), Tupe(  86,   71), 0.50, Tupe(   0,     0)),
    # "eggish":       ImageElementBodyData(Tupe(- 10,   70), Tupe(- 25, -170), 3.50, Tupe(   0,     0)), #
    # "plantish":     ImageElementBodyData(Tupe( 108,  122), Tupe( 108,  122), 0.80, Tupe(   0,     0)),
    # "dark":         ImageElementBodyData(Tupe(  80,   80), Tupe(  80,   80), 1.10, Tupe(   0,     0)), 
    # "mythical":     ImageElementBodyData(Tupe(  80,   80), Tupe(  80,   80), 1.10, Tupe(- 15,    35))  #
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
