from pathlib import Path
from typing import Iterator, Protocol, Optional
from app.models.schema import Schema
import json
import logging

logger = logging.getLogger(__name__)


class SchemaRepository(Protocol):
    def get_all_schemas(self) -> Iterator[Schema]: ...
    def save_schema(self, schema: Schema) -> None: ...


class LocalSchemaRepository(SchemaRepository):
    def __init__(self, schema_folder: str) -> None:
        self.path = Path(schema_folder)
        if not self.path.exists():
            self.path.mkdir(parents=True)

    def get_all_schemas(self) -> Iterator[Schema]:
        for file in self.path.glob("*.json"):
            with open(file) as jsonfile:
                try:
                    definition = json.load(jsonfile)
                    yield Schema(file.stem, definition)
                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    logger.warning(f"Error reading file {file.name}: {e}")
                    continue

    def save_schema(self, schema: Schema) -> None:
        with open(self.path / f"{schema.name}.json", "w") as f:
            json.dump(schema.definition, f)


class SchemaRegistry:
    def __init__(self, repository: SchemaRepository) -> None:
        self.repository = repository
        self.schemas = {s.name: s for s in self.repository.get_all_schemas()}

    def available_schemas(self) -> list[str]:
        return list(self.schemas.keys())

    def get_schema(self, schema_name: str) -> Optional[Schema]:
        return self.schemas.get(schema_name)

    def register_schema(self, schema: Schema) -> None:
        self.repository.save_schema(schema)
        self.schemas[schema.name] = schema
