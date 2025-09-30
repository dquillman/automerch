import os
import typer
from alembic import command
from alembic.config import Config

app = typer.Typer(help="AutoMerch management commands")


def _cfg() -> Config:
    cfg = Config("alembic.ini")
    # Ensure env respects AUTORMERCH_DB if set
    if os.getenv("AUTOMERCH_DB"):
        cfg.set_main_option("sqlalchemy.url", os.getenv("AUTOMERCH_DB"))
    return cfg


@app.command()
def db_upgrade(revision: str = "head"):
    """Upgrade DB to revision (default head)."""
    command.upgrade(_cfg(), revision)


@app.command()
def db_revision(message: str = typer.Option(..., "-m", help="Revision message"), autogenerate: bool = True):
    """Create a new Alembic revision (autogenerate by default)."""
    command.revision(_cfg(), message=message, autogenerate=autogenerate)


if __name__ == "__main__":
    app()

