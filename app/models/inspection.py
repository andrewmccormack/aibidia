from dataclasses import dataclass, field

from app.models.schema import Schema


@dataclass
class InspectionResult:
    schema: Schema
    columns: list[str] = field(default_factory=list)
    sample: list[dict] = field(default_factory=list)
    suggestions: dict[str,str] = field(default_factory=list)

    def fields(self):
        return self.schema.definition.keys()