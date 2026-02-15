from dataclasses import dataclass, field
from typing import Self

from app.models.schema import Schema
from uuid import UUID


class ColumnMappings:
    name: str = field(default="")
    mappings: dict[str, str] = field(default_factory=dict)


@dataclass
class CSVValidationRequest:
    id: UUID
    file: str
    schema: str
    mappings: dict[str, str] = field(default_factory=dict)
    error_threshold: int = field(default=100)


@dataclass
class CSVValidationError:
    row_numer: int
    error: str


@dataclass
class CSVValidationResponse:
    request_id: UUID
    file: str
    schema: str
    errors: list[CSVValidationError] = field(default_factory=list)

    def is_valid(self) -> bool:
        return len(self.errors) == 0

    @classmethod
    def invalid_file(cls, request: CSVValidationRequest) -> Self:
        return CSVValidationResponse(
            request_id=request.id,
            file=request.file,
            schema=request.schema,
            errors=[CSVValidationError(row_numer=0, error="Could not read file")],
        )

    @classmethod
    def from_request(self, request: CSVValidationRequest) -> Self:
        return CSVValidationResponse(
            request_id=request.id, file=request.file, schema=request.schema
        )
