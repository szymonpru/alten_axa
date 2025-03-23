from http import HTTPStatus

import pytest
from httpx import AsyncClient

from app.tests.factories import PokemonFactory


@pytest.mark.asyncio(loop_scope="session")
async def test_get_all_pokemons_default_pagination(
    client: AsyncClient,
) -> None:
    size = 10
    total = 19

    response = await client.get("/pokemons/")

    # Check status code
    assert response.status_code == HTTPStatus.OK

    # Parse response
    data = response.json()

    # Verify pagination structure
    assert "items" in data
    assert "page" in data
    assert "pages" in data
    assert "size" in data
    assert "total" in data

    # Verify specific values
    assert data["page"] == 1
    assert data["size"] == size
    assert len(data["items"]) == size
    assert data["total"] == total

    first_pokemon = data["items"][0]
    assert set(first_pokemon.keys()) == {
        "pokemon_id",
        "name",
        "type",
        "hp",
        "attack",
        "defense",
        "speed",
        "rarity",
    }
    assert first_pokemon["name"] == "Pikachu"
    assert first_pokemon["type"] == "Electric"


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("size", [1, 2, 5, 10, 15])
async def test_get_all_pokemons_page_size(client: AsyncClient, size: int) -> None:
    response = await client.get(f"/pokemons/?page=1&size={size}")
    assert response.status_code == HTTPStatus.OK
    data = response.json()

    assert data["page"] == 1
    assert data["size"] == size
    assert len(data["items"]) == size

    total = data["total"]
    expected_pages = (total + size - 1) // size  # Use actual total
    assert data["pages"] == expected_pages


@pytest.mark.asyncio(loop_scope="session")
async def test_get_by_id(client):
    pokemon = await PokemonFactory(name="TEST")
    response = await client.get(f"/pokemons/{pokemon.pokemon_id}")
    assert response.status_code == HTTPStatus.OK
    data = response.json()

    assert data["name"] == pokemon.name
    assert data["description"] == pokemon.description
    assert data["type"] == pokemon.type
