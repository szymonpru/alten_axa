import uuid

from sqlalchemy import String, Uuid, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import User
from app.models.base import Base
from app.utils import PokemonType, PokemonRarity


class Pokemon(Base):
    __tablename__ = "pokemons"

    pokemon_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False), primary_key=True, default=lambda _: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(500), nullable=True)

    hp: Mapped[int] = mapped_column(nullable=False, default=100)
    attack: Mapped[int] = mapped_column(nullable=False, default=100)
    defense: Mapped[int] = mapped_column(nullable=False, default=100)
    speed: Mapped[int] = mapped_column(nullable=False, default=100)

    type: Mapped[PokemonType] = mapped_column(Enum(PokemonType), nullable=False)
    rarity: Mapped[PokemonRarity] = mapped_column(Enum(PokemonRarity), nullable=False, default=PokemonRarity.COMMON)

    user_pokemons: Mapped[list["UserPokemon"]] = relationship("UserPokemon", back_populates="pokemon")


class UserPokemon(Base):
    __tablename__ = "users_pokemons"

    id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False), primary_key=True, default=lambda _: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False), ForeignKey("users.user_id"), nullable=False
    )
    pokemon_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False), ForeignKey("pokemons.pokemon_id"), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="user_pokemons")
    pokemon: Mapped["Pokemon"] = relationship("Pokemon", back_populates="user_pokemons")
