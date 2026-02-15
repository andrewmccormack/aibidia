import pytest
from app.models.schema import Schema


def test_schema_fields_returns_set_of_definition_keys():
    schema = Schema("test", {"a": {"type": "string"}, "b": {"type": "integer"}})
    assert schema.fields() == {"a", "b"}


def test_schema_fields_empty_definition():
    schema = Schema("empty", {})
    assert schema.fields() == set()


def test_schema_name_and_definition_stored():
    definition = {"email": {"type": "string"}}
    schema = Schema("user", definition)
    assert schema.name == "user"
    assert schema.definition == definition
