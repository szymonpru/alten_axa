from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.dependencies import get_current_user
from app.models import Pokemon, UserPokemon, User
from app.schemas.base import CustomPage
from app.schemas.pokemon import PokemonResponse

router = APIRouter(prefix="/user/pokemons", tags=["User favourite pokemons"])


@router.post("/bulk", response_model=List[PokemonResponse])
async def add_favorite_pokemons_bulk(
        pokemon_ids: List[UUID],
        session: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)  # Get current user
) -> List[Pokemon]:
    # Fetch all pokemons in the provided pokemon_ids
    result = await session.execute(select(Pokemon).filter(Pokemon.pokemon_id.in_(pokemon_ids)))
    pokemons = result.scalars().all()

    # Check if any Pokémon in the list doesn't exist
    if len(pokemons) != len(pokemon_ids):
        missing_pokemon_ids = set(pokemon_ids) - {pokemon.pokemon_id for pokemon in pokemons}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Pokemons not found: {', '.join(map(str, missing_pokemon_ids))}")

    # Fetch existing favorite relations to avoid duplicates
    stmt = select(UserPokemon.pokemon_id).filter(
        UserPokemon.user_id == current_user.user_id,
        UserPokemon.pokemon_id.in_(pokemon_ids)
    )
    result = await session.execute(stmt)
    existing_fav_ids = {fav for fav in result.scalars()}

    # Filter out already favorited Pokémon
    pokemon_ids_to_add = [str(pokemon_id) for pokemon_id in pokemon_ids if str(pokemon_id) not in existing_fav_ids]

    # If no new favorites are left, return the existing ones
    if not pokemon_ids_to_add:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="All Pokémon are already assigned as favorites")

    # Create new relations for the remaining Pokémon
    user_pokemons_to_add = [
        UserPokemon(user_id=current_user.user_id, pokemon_id=pokemon_id)
        for pokemon_id in pokemon_ids_to_add
    ]

    # Add all new favorites in bulk
    session.add_all(user_pokemons_to_add)
    await session.commit()

    # Return only the Pokémon that were successfully added
    return [pokemon for pokemon in pokemons if pokemon.pokemon_id in pokemon_ids_to_add]


@router.get("/", response_model=CustomPage[PokemonResponse])
async def get_user_pokemons(
        session: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)  # Get current user
) -> CustomPage[PokemonResponse]:
    query = (
        select(Pokemon)
        .join(UserPokemon, UserPokemon.pokemon_id == Pokemon.pokemon_id)
        .filter(UserPokemon.user_id == current_user.user_id)
    )
    return await paginate(session, query)


@router.delete("/{pokemon_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite_pokemon(
        pokemon_id: UUID,
        session: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)  # Get current user
) -> None:
    # Fetch the UserPokemon relationship by pokemon_id and current_user.user_id
    user_pokemon = await session.scalar(
        select(UserPokemon).where(
            UserPokemon.pokemon_id == pokemon_id,
            UserPokemon.user_id == current_user.user_id
        )
    )

    # If the relationship doesn't exist, raise a 404 error
    if not user_pokemon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pokemon not assigned as favorite")

    # Delete the relationship
    await session.delete(user_pokemon)
    await session.commit()
