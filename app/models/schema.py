from dataclasses import dataclass, field
from pathlib import Path
import json

from cerberus import Validator
@dataclass
class Schema:
    name: str
    definition: dict = field(default_factory=dict)

    def validator(self) -> Validator:
        return Validator(self.definition)

    def suggestions(self, columns, sample):
        suggestions = {}
        fields = self.definition.keys()
        for column in columns:
            normalized = column.lower().replace(" ", "_")
            if normalized in fields:
                suggestions[column] = normalized
                continue

        return suggestions

    @classmethod
    def from_file(cls, file:Path) -> Schema:
        with open(file) as jsonfile:
            definition = json.load(jsonfile)
            return Schema(file.stem, definition)

