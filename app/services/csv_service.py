import logging
from typing import Protocol
from pandas import DataFrame
from werkzeug.datastructures import FileStorage

from app.models.schema import Schema
from app.models.inspection import InspectionResult
from app.models.process import CSVValidationRequest, CSVValidationResponse, CSVValidationError
from app.services.csv_storage import CSVStorage
from app.services.schema_registry import SchemaRegistry
from cerberus import Validator

logger = logging.getLogger(__name__)

class CsvService(Protocol):
    def available_schemas(self) -> list[str]: ...
    def upload_file(self, file: FileStorage) -> str: ...
    def validate(self, request:CSVValidationRequest) -> CSVValidationResponse: ...
    def inspect(self, file_path: str, schema: str = "default", sample_size = 5) -> InspectionResult: ...
    def recommend_schema(self, file_path: str, threshold: float = 0.8) -> Schema: ...

def guess_by_content(sample: list, schema: Schema, threshold: float = 0.8) -> str | None:
    validator = Validator(schema.definition, allow_unknown=True)
    if sample is None:
        return None

    for field_name, rules in schema.definition.items():
        match_count = 0
        for value in sample:
            if validator.validate({field_name: value}, {field_name: rules}):
                match_count += 1

        if match_count / len(sample) > threshold:
            return field_name

    return None

def get_suggested_columns_mappings(df:DataFrame, schema: Schema, threshold: float = 0.8) -> dict[str,str|None]:
    sample = df.to_dict(orient="list")
    schema_fields = schema.definition.keys()
    suggestions = {}
    for col in df.columns:
        key = str(col)
        normalized = str(col).lower().replace(" ", "_")
        if normalized in schema_fields:
            suggestions[key] = normalized
            continue

        suggestions[key] = guess_by_content(sample[col], schema, threshold)

    return suggestions


def inspect(df:DataFrame, schema: Schema) -> InspectionResult:
    columns = [str(col) for col in df.columns]
    sample = df.to_dict(orient="records")
    schema_fields = schema.definition.keys()
    suggestions = get_suggested_columns_mappings(df, schema)
    return InspectionResult(schema, columns, sample, suggestions)



class CSVServiceImpl(CsvService):
    def __init__(self, csv_store: CSVStorage, schema_registry: SchemaRegistry) -> None:
        self.csv_store = csv_store
        self.schema_registry = schema_registry
        self.default_schema = self.schema_registry.get_schema("default")

    def available_schemas(self) -> list[str]:
        return self.schema_registry.available_schemas()

    def upload_file(self, file: FileStorage) -> str:
        uploaded_file = self.csv_store.save_uploaded_file(file)
        return uploaded_file.name

    def validate(self, request:CSVValidationRequest) -> CSVValidationResponse:
        schema = self.schema_registry.get_schema(request.schema)
        validator = Validator(schema.definition)

        chunks = self.csv_store.read_chunk(request.file)
        if chunks is None:
            return CSVValidationResponse.invalid_file(request)

        response = CSVValidationResponse.from_request(request)
        for chunk in chunks:
            chunk = chunk.rename(columns=request.mappings)
            records = chunk.to_dict('records')
            offset = chunk.index[0]
            for index, record in enumerate(records):
                if not validator.validate(record):
                    # Calculate global row index based on chunk offset
                    row = offset + index
                    response.errors.append(
                        CSVValidationError(row_numer=row, error=validator.errors)
                    )

            if len(response.errors) > request.error_threshold:
                break

        return response

    def recommend_schema(self, file_path: str, threshold: float = 0.8) -> Schema:
        try:
            best_match = None
            highest_score = 0.0
            for schema in self.available_schemas():
                inspection = self.inspect(file_path, schema)
                if inspection.score > highest_score:
                    best_match = inspection.schema
                    highest_score = inspection.score
            return best_match if highest_score > threshold else self.default_schema
        except Exception as e:
            logger.warning(f"Problem recommending schema for {file_path}: {e}", exc_info=True)
            raise ValueError(f"Error reading file {file_path}: {e}")

    def inspect(self, file_path: str, schema: str = "default", sample_size: int = 5) -> InspectionResult:
        try:
            schema = self.schema_registry.get_schema(schema)
            df = self.csv_store.peek(file_path, rows=sample_size)
            return inspect(df, schema)
        except Exception as e:
            raise ValueError(f"Error reading file {file_path}: {e}")