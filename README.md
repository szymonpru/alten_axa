## TASK

Please create a simple application with a Python back end.
The back end should offer a RESTful API endpoint which in turn communicates with a database of your choice to persists
some data received in the RESTful call. We would like to see automated tests, input sanitisation. Consider error
handling and observability. Create a local Git repository for this project.
We do not expect perfection, but would like to see confidence and good practices.
Please share the code with us (ideally using GitHub).

## Project description
A simple async FastAPI API built with JWT authentication for user management.
Users can register, access a pre-populated Pokemon list, and save favorites using a many-to-many relationship. 
Powered by asyncio, SQLAlchemy 2.0 (async ORM), and PostgreSQL in a local Docker container. 
Includes example tests for Pokemon endpoints.


## TOOLS
### Poetry dependencies

Add new

```
poertry add <dependency>
```

### Alembic migrations

New migration

```
alembic revision --autogenerate -m "create_pet_model"
```

Apply migration using alembic upgrade

```
alembic upgrade head
```