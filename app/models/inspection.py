from dataclasses import dataclass, field

from app.models.schema import Schema


@dataclass
class InspectionResult:
    schema: Schema
    columns: list[str] = field(default_factory=set)
    sample: list[dict] = field(default_factory=list)
    suggestions: dict[str, str] = field(default_factory=list)

    @property
    def score(self) -> float:
        schema_fields = self.schema.fields()
        mapped_columns = set(self.suggestions.values())
        intersection = mapped_columns.intersection(schema_fields)
        return len(intersection) / len(schema_fields)
