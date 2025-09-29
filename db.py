import os
from sqlmodel import SQLModel, create_engine
engine = create_engine('sqlite:///automerch.db', echo=False)

def init_db():
    from models import Product, RunLog
    SQLModel.metadata.create_all(engine)
