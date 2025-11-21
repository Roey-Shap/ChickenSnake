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

def find_creature_class(subtypes: str) -> str:
    dominant_subtype: str = sorted(subtypes.split(" "))[0]
    for creature_class in creature_subtype_generalization:
        if dominant_subtype in creature_subtype_generalization[creature_class]:
            return creature_class

    return "humanish"

class SubtypeImageModifier:
    helmet_subtypes = ["warrior"]
    wing_subtypes = ["harpy", "faerie", "angel", "archon"]
    wizard_hat_subtypes = ["warlock", "wizard", "spellshaper", "druid"]
    eye_patch_subtypes = ["pirate"]
    horn_subtypes = ["devil", "demon"]
    on_cloud_subtypes = ["djinn", "efreet"]
    remove_eye_subtypes = ["cyclops"]
    short_subtypes = ["kithkin", "homunculus", "halfling", "gnome", "dwarf", "beeble", "child"]
    sanddune_subtypes = ["sand"]
    translucent_subtypes = ["glimmer", "illusion"]

    def __init__(self):
        self.helmet = False
        self.wings = False
        self.wizard_hat = False
        self.eye_patch = False
        self.horns = False
        self.on_cloud = False
        self.remove_eye = False
        self.short = False
        self.sanddune = False
        self.translucent = False


    def assign_modifiers_from_creature_subtypes(self, subtypes: list[str]):
        for subtype in subtypes:
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
