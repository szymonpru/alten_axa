from typing import Optional

from pydantic import BaseModel

from app.utils import PokemonType, PokemonRarity


class PokemonResponse(BaseModel):
    pokemon_id: str
    name: str
    hp: int
    attack: int
    defense: int
    speed: int
    type: PokemonType
    rarity: PokemonRarity


class PokemonDetailsResponse(PokemonResponse):
    description: Optional[str] = None
