from sqlmodel import SQLModel, Field
class Product(SQLModel, table=True):
    sku: str = Field(primary_key=True)
class RunLog(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
