from enum import Enum


class PokemonType(str, Enum):
    NORMAL = "Normal"
    FIRE = "Fire"
    WATER = "Water"
    ELECTRIC = "Electric"
    GRASS = "Grass"
    ICE = "Ice"
    FIGHTING = "Fighting"
    POISON = "Poison"
    GROUND = "Ground"
    FLYING = "Flying"
    PSYCHIC = "Psychic"
    BUG = "Bug"
    ROCK = "Rock"
    GHOST = "Ghost"
    DRAGON = "Dragon"
    DARK = "Dark"
    STEEL = "Steel"
    FAIRY = "Fairy"


class PokemonRarity(str, Enum):
    COMMON = "Common"
    UNCOMMON = "Uncommon"
    RARE = "Rare"
    LEGENDARY = "Legendary"
    MYTHICAL = "Mythical"
