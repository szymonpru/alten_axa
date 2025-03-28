import logging

from fastapi import FastAPI
from fastapi_pagination import add_pagination
from starlette.middleware.cors import CORSMiddleware

from app.api import auth, pokemons, user, user_pokemons
from app.core.logging_config import setup_logging

setup_logging()

logging.info("Starting FastAPI application...")

app = FastAPI()

origins = ["*"]  # TODO add origins to .env

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(pokemons.router)
app.include_router(user_pokemons.router)

# Pagination
add_pagination(app)
