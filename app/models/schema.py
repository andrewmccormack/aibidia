from dataclasses import dataclass, field
from pathlib import Path
import json


@dataclass
class Schema:
    name: str
    definition: dict = field(default_factory=dict)

    def fields(self) -> set[str]:
        return set(self.definition.keys())
