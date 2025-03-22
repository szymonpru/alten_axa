from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.dependencies import get_current_user
from app.models import Pokemon
from app.schemas.base import CustomPage
from app.schemas.pokemon import PokemonResponse, PokemonDetailsResponse

router = APIRouter(
    prefix="/pokemons",
    tags=["Pokemons"],
    dependencies=[Depends(get_current_user)]
)


@router.get("/", response_model=CustomPage[PokemonResponse])
async def get_all_pokemons(session: AsyncSession = Depends(get_db)):
    query = select(Pokemon).order_by(Pokemon.created_at)
    return await paginate(session, query)


@router.get("/{pokemon_id}", response_model=PokemonDetailsResponse)
async def get_pokemon_with_details(pokemon_id: UUID, session: AsyncSession = Depends(get_db)):
    db_pokemon = await session.scalar(select(Pokemon).where(Pokemon.pokemon_id == pokemon_id))
    if db_pokemon is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pokemon not found")
    return db_pokemon
