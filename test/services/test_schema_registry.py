import pytest
import json
from app.services import LocalSchemaRepository
from app.services.schema_registry import SchemaRegistry
from app.models.schema import Schema


@pytest.fixture
def temp_schema_dir(tmp_path):
    d = tmp_path / "schemas"
    d.mkdir()
    schema_file = d / "user_schema.json"
    schema_file.write_text(json.dumps({"name": {"type": "string", "required": True}}))
    broken_file = d / "broken.json"
    broken_file.write_text("invalid json content")
    return d


def test_get_all_schemas_ignores_broken_files(temp_schema_dir):
    repo = LocalSchemaRepository(str(temp_schema_dir))
    schemas = list(repo.get_all_schemas())

    # Should only yield the valid 'user_schema', skipping 'broken'
    assert len(schemas) == 1
    assert schemas[0] == Schema(
        name="user_schema",
        definition={"name": {"required": True, "type": "string"}},
    )


def test_save_schema_creates_file(temp_schema_dir):
    repo = LocalSchemaRepository(str(temp_schema_dir))
    new_schema = Schema("order", {"id": {"type": "integer"}})
    repo.save_schema(new_schema)

    expected_file = temp_schema_dir / "order.json"
    assert expected_file.exists()
    assert "integer" in expected_file.read_text()


# --- SchemaRegistry ---


def test_registry_available_schemas(temp_schema_dir):
    registry = SchemaRegistry(LocalSchemaRepository(str(temp_schema_dir)))
    names = registry.available_schemas()
    assert names == ["user_schema"]


def test_registry_get_schema_returns_schema(temp_schema_dir):
    registry = SchemaRegistry(LocalSchemaRepository(str(temp_schema_dir)))
    schema = registry.get_schema("user_schema")
    assert schema is not None
    assert schema.name == "user_schema"
    assert "name" in schema.definition


def test_registry_get_schema_returns_none_for_unknown(temp_schema_dir):
    registry = SchemaRegistry(LocalSchemaRepository(str(temp_schema_dir)))
    assert registry.get_schema("nonexistent") is None


def test_register_schema_persists_and_adds_to_registry(temp_schema_dir):
    repo = LocalSchemaRepository(str(temp_schema_dir))
    registry = SchemaRegistry(repo)
    new_schema = Schema("payment", {"amount": {"type": "float"}})
    registry.register_schema(new_schema)

    assert registry.get_schema("payment") is not None
    assert registry.get_schema("payment").definition == {"amount": {"type": "float"}}
    assert (temp_schema_dir / "payment.json").exists()
    assert "float" in (temp_schema_dir / "payment.json").read_text()