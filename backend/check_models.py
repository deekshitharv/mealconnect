"""Throwaway script: checks the models are valid and prints the SQL for each table.
It does NOT connect to the database or create anything."""
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import configure_mappers
from sqlalchemy.schema import CreateTable

from app.db.session import Base
import app.models  # noqa: F401  (registers all models)

configure_mappers()  # fails loudly if any relationship is wrong
print("Relationships OK\n")

for table in Base.metadata.sorted_tables:
    print(CreateTable(table).compile(dialect=postgresql.dialect()))