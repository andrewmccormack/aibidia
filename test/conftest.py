import pytest
import json
from pathlib import Path

from app import create_app
from app.models.schema import Schema
from app.services.csv_storage import LocalFileStorage
from app.services.schema_registry import SchemaRegistry


@pytest.fixture
def app():
    """Application fixture with test config."""
    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["UPLOAD_FOLDER"] = "test/tmp/uploads"
    app.config["SCHEMA_FOLDER"] = "test/tmp/schemas"
    app.config["MAX_FILE_SIZE"] = 10 * 1024 * 1024
    return app


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture
def sample_schema():
    """Schema used across service tests."""
    return Schema(
        name="test",
        definition={
            "user_email": {"type": "string", "regex": r"[^@]+@[^@]+\.[^@]+"},
            "transaction_amount": {"type": "float", "min": 0},
            "signup_date": {"type": "date"},
        },
    )


@pytest.fixture
def temp_schema_dir(tmp_path):
    """Temporary directory with valid and broken schema files."""
    d = tmp_path / "schemas"
    d.mkdir()
    (d / "user_schema.json").write_text(
        json.dumps({"name": {"type": "string", "required": True}})
    )
    (d / "broken.json").write_text("invalid json content")
    return d


@pytest.fixture
def schema_registry(sample_schema):
    """SchemaRegistry that yields sample_schema (for csv_service tests)."""
    from app.services.schema_registry import SchemaRegistry, SchemaRepository

    class MockSchemaRepository(SchemaRepository):
        def get_all_schemas(self):
            yield sample_schema

        def save_schema(self, schema: Schema) -> None:
            pass

    return SchemaRegistry(MockSchemaRepository())
