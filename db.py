import os
from sqlmodel import SQLModel, create_engine, Session

DB_URL = os.getenv("AUTOMERCH_DB", "sqlite:///automerch.db")
engine = create_engine(DB_URL, echo=False)


def init_db():
    from models import Product, RunLog, OAuthToken
    # If ALEMBIC is preferred, allow env to control
    if os.getenv("USE_ALEMBIC", "false").lower() == "true":
        try:
            from alembic import command
            from alembic.config import Config
            cfg = Config(str((os.path.dirname(__file__) or '.') + '/alembic.ini'))
            if os.getenv("AUTOMERCH_DB"):
                cfg.set_main_option("sqlalchemy.url", os.getenv("AUTOMERCH_DB"))
            command.upgrade(cfg, 'head')
            return
        except Exception:
            pass
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
            if 'thumbnail_url' not in cols:
                to_add.append("ALTER TABLE product ADD COLUMN thumbnail_url VARCHAR")
            if 'variant_id' not in cols:
                to_add.append("ALTER TABLE product ADD COLUMN variant_id INTEGER")
            if 'printful_variant_id' not in cols:
                to_add.append("ALTER TABLE product ADD COLUMN printful_variant_id VARCHAR")
            if 'etsy_listing_id' not in cols:
                to_add.append("ALTER TABLE product ADD COLUMN etsy_listing_id VARCHAR")
            if 'quantity' not in cols:
                to_add.append("ALTER TABLE product ADD COLUMN quantity INTEGER")
            if 'printful_file_id' not in cols:
                to_add.append("ALTER TABLE product ADD COLUMN printful_file_id INTEGER")
            for stmt in to_add:
                conn.exec_driver_sql(stmt)
        except Exception:
            pass


def get_session():
    return Session(engine)
