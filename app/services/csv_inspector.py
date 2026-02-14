from typing import Protocol
import pandas as pd
from app.models.inspection import InspectionResult
from app.services.file_storage import FileStorage
from app.services.schema_registry import SchemaRegistry
from app.utils.file import get_encoding


class CSVInspector:
    def __init__(self, file_storage: FileStorage, schemas: SchemaRegistry) -> None:
        self.file_storage = file_storage
        self.schemas = schemas

    def inspect(self, file_path: str, schema: str = "default") -> InspectionResult:
        try:

            schema = self.schemas.get_schema(schema)
            path = self.file_storage.resolve_path(file_path)
            encoding = get_encoding(path)
            df = pd.read_csv(path, encoding=encoding, nrows=5)
            columns = [str(col) for col in df.columns]
            sample = df.to_dict(orient="records")
            return InspectionResult(schema, columns, sample, suggestions=schema.suggestions(columns, sample))
        except Exception as e:
            raise ValueError(f"Error reading file {file_path}: {e}")

