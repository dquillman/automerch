import os
from sqlmodel import SQLModel, create_engine, Session

DB_URL = os.getenv('AUTOMERCH_DB', 'sqlite:///automerch.db')
engine = create_engine(DB_URL, echo=False)


def init_db():
    from models import Product, RunLog
    SQLModel.metadata.create_all(engine)


def get_session():
    return Session(engine)
