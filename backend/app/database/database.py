from sqlmodel import SQLModel, create_engine, Session
from ..core.config import settings

engine = create_engine(settings.database_url)

def get_session():
    with Session(engine) as session:
        yield session   

def init_db():
    SQLModel.metadata.create_all(engine)
    print("Database initialized successfully.")
    yield from get_session()