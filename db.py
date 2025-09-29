import os
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel import text

DB_URL = os.getenv('AUTOMERCH_DB', 'sqlite:///automerch.db')
engine = create_engine(DB_URL, echo=False)


def init_db():
    from models import Product, RunLog
    SQLModel.metadata.create_all(engine)
    migrate_db()


def migrate_db():
    # Minimal SQLite migration: add missing Product columns
    with engine.connect() as conn:
        try:
            res = conn.exec_driver_sql("PRAGMA table_info('product')")
            cols = {row[1] for row in res}
            to_add = []
            if 'name' not in cols:
                to_add.append("ALTER TABLE product ADD COLUMN name VARCHAR")
            if 'description' not in cols:
                to_add.append("ALTER TABLE product ADD COLUMN description VARCHAR")
            if 'price' not in cols:
                to_add.append("ALTER TABLE product ADD COLUMN price FLOAT")
            if 'created_at' not in cols:
                to_add.append("ALTER TABLE product ADD COLUMN created_at TIMESTAMP")
            for stmt in to_add:
                conn.exec_driver_sql(stmt)
        except Exception:
            pass


def get_session():
    return Session(engine)
