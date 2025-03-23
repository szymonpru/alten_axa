import uuid
from typing import Any

import factory
from factory import alchemy, enums
from factory.alchemy import SQLAlchemyOptions
from factory.base import Factory, FactoryMetaClass, StubObject, T
from factory.errors import UnknownStrategy
from faker import Faker
from sqlalchemy.util import await_only, greenlet_spawn

from app.models import Pokemon, User
from app.utils import PokemonRarity, PokemonType

fake = Faker()


class AsyncFactoryMetaClass(FactoryMetaClass):
    async def __call__(cls, **kwargs: Any) -> T | StubObject:
        if cls._meta.strategy == enums.BUILD_STRATEGY:
            return cls.build(**kwargs)

        if cls._meta.strategy == enums.CREATE_STRATEGY:
            return await cls.create(**kwargs)

        if cls._meta.strategy == enums.STUB_STRATEGY:
            return cls.stub(**kwargs)

        raise UnknownStrategy(
            f"Unknown '{cls.__name__}.Meta.strategy': {cls._meta.strategy}"
        )


class AsyncSQLAlchemyModelFactory(Factory, metaclass=AsyncFactoryMetaClass):
    _options_class = SQLAlchemyOptions

    class Meta:
        abstract = True

    @classmethod
    async def create(cls, **kwargs: Any) -> T:  # noqa: ANN401
        return await greenlet_spawn(cls._generate, enums.CREATE_STRATEGY, kwargs)

    @classmethod
    async def create_batch(cls, size: int, **kwargs: Any) -> list[T]:  # noqa: ANN401
        return [await cls.create(**kwargs) for _ in range(size)]

    @classmethod
    def _create(cls, model_class: type[Any], *args: Any, **kwargs: Any) -> T:  # noqa: ANN401
        meta = cls._meta

        session = meta.sqlalchemy_session
        if (
            session is None
            and (session_factory := meta.sqlalchemy_session_factory) is not None
        ):
            session = session_factory()

        if not session:
            class_name = cls.__name__
            raise RuntimeError(
                f"No session: "
                f"set '{class_name}.Meta.sqlalchemy_session' or '{class_name}.Meta.sqlalchemy_session_factory'"
            )

        instance = model_class(*args, **kwargs)
        session.add(instance)

        session_persistence = meta.sqlalchemy_session_persistence
        if session_persistence == alchemy.SESSION_PERSISTENCE_FLUSH:
            await_only(session.flush())
        elif session_persistence == alchemy.SESSION_PERSISTENCE_COMMIT:
            await_only(session.commit())

        return instance


class BaseFactory(AsyncSQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session_persistence = alchemy.SESSION_PERSISTENCE_COMMIT

    @classmethod
    def set_session(cls, session):
        # Get all subclasses of BaseFactory, including nested subclasses
        def get_all_subclasses(cls):
            all_subclasses = []
            for subclass in cls.__subclasses__():
                all_subclasses.append(subclass)
                all_subclasses.extend(get_all_subclasses(subclass))
            return all_subclasses

        # Set the session for all factory classes
        for factory_cls in get_all_subclasses(cls):
            if hasattr(factory_cls, "_meta"):
                factory_cls._meta.sqlalchemy_session = session


class PokemonFactory(BaseFactory):
    class Meta:
        model = Pokemon

    pokemon_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"Pokemon{n}")
    description = factory.LazyAttribute(lambda o: f"{o.name} is awesome!")

    hp = factory.LazyFunction(lambda: 100)
    attack = factory.LazyFunction(lambda: 100)
    defense = factory.LazyFunction(lambda: 100)
    speed = factory.LazyFunction(lambda: 100)

    type = factory.Iterator(PokemonType, cycle=True)
    rarity = factory.Iterator(PokemonRarity, cycle=True)


class UserFactory(BaseFactory):
    class Meta:
        model = User

    email = f"{fake.first_name()}.{fake.last_name()}@test.com"
    hashed_password = fake.password()
