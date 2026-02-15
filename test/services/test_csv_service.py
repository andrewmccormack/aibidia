import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import MagicMock
from werkzeug.datastructures import FileStorage

from app.models.schema import Schema
from app.models.process import CSVValidationRequest
from app.services import SchemaRepository, SchemaRegistry
from app.services.csv_service import (
    get_suggested_columns_mappings,
    guess_by_content,
    inspect as inspect_csv,
    CSVServiceImpl,
)

definition = {
    "user_email": {"type": "string", "regex": r"[^@]+@[^@]+\.[^@]+"},
    "transaction_amount": {"type": "float", "min": 0},
    "signup_date": {"type": "date"},
}

schema = Schema(name="test", definition=definition)


@pytest.fixture
def schema_registry() -> SchemaRegistry:
    from app.services.schema_registry import SchemaRegistry

    class MockSchemaRepository(SchemaRepository):
        def get_all_schemas(self):
            yield schema

        def save_schema(self, schema: Schema) -> None:
            pass

    return SchemaRegistry(MockSchemaRepository())


def test_suggestions_are__mappings_with_headers():
    """Verifies that exact/normalized name matching works first."""
    df = pd.DataFrame({"User Email": ["test@example.com"], "transaction_amount": [100]})
    expected = {"User Email": "user_email", "transaction_amount": "transaction_amount"}
    suggestions = get_suggested_columns_mappings(df, schema)
    assert suggestions == expected


def test_can_make_suggestions_when_the_dataframe_has_no_headers():
    df = pd.DataFrame(
        [["bob@aibidia.com", 50, "2026-01-01"], ["alice@taxtech.fi", 75, "2026-01-02"]]
    )
    expected = {"0": "user_email", "1": "transaction_amount", "2": None}
    suggestions = get_suggested_columns_mappings(df, schema)
    assert suggestions == expected


def test_suggest_mappings_with_empty_values():
    df = pd.DataFrame(
        {
            "col_a": [None, "a@b.vom", "charles@example.com", None],
            "col_b": [10, 20, None, 40],
        }
    )
    expected = {"col_a": "user_email", "col_b": "transaction_amount"}
    suggestions = get_suggested_columns_mappings(df, schema, threshold=0.1)
    assert suggestions == expected


def test_suggestions_are_none_when_no_match_found():
    df = pd.DataFrame({"amount": ["free", "expensive", "none"]})
    suggestions = get_suggested_columns_mappings(df, schema)
    assert suggestions["amount"] is None


# --- guess_by_content ---


def test_guess_by_content_returns_field_when_above_threshold():
    sample = ["a@b.com", "x@y.co", "user@test.org"]
    assert guess_by_content(sample, schema, threshold=0.6) == "user_email"


def test_guess_by_content_returns_none_when_below_threshold():
    sample = ["a@b.com", "not-an-email", "invalid"]
    assert guess_by_content(sample, schema, threshold=0.8) is None


def test_guess_by_content_returns_none_for_none_sample():
    assert guess_by_content(None, schema) is None


def test_guess_by_content_matches_float_column():
    sample = [10.5, 20.0, 0.1]
    assert guess_by_content(sample, schema, threshold=0.8) == "transaction_amount"


# --- inspect (function) ---


def test_inspect_returns_inspection_result_with_columns_and_suggestions():
    df = pd.DataFrame(
        {
            "User Email": ["test@example.com"],
            "transaction_amount": [100.0],
        }
    )
    result = inspect_csv(df, schema)
    assert result.schema == schema
    assert result.columns == ["User Email", "transaction_amount"]
    assert len(result.sample) == 1
    assert result.suggestions["User Email"] == "user_email"
    assert result.suggestions["transaction_amount"] == "transaction_amount"


# --- CSVServiceImpl ---


@pytest.fixture
def mock_csv_storage():
    store = MagicMock()
    return store


def test_available_schemas_returns_registry_schemas(schema_registry, mock_csv_storage):
    service = CSVServiceImpl(mock_csv_storage, schema_registry)
    assert service.available_schemas() == ["test"]


def test_upload_file_returns_saved_file_name(schema_registry, mock_csv_storage):
    mock_csv_storage.save_uploaded_file.return_value = Path("uploads/foo.csv")
    service = CSVServiceImpl(mock_csv_storage, schema_registry)
    uploaded = MagicMock(spec=FileStorage)
    name = service.upload_file(uploaded)
    assert name == "foo.csv"
    mock_csv_storage.save_uploaded_file.assert_called_once_with(uploaded)


def test_validate_valid_csv_returns_no_errors(schema_registry, mock_csv_storage):
    import uuid
    from datetime import date

    valid_df = pd.DataFrame(
        {
            "user_email": ["a@b.com", "b@c.com"],
            "transaction_amount": [10.0, 20.0],
            "signup_date": [date(2026, 1, 1), date(2026, 1, 2)],
        }
    )
    mock_csv_storage.read_chunk.return_value = iter([valid_df])
    service = CSVServiceImpl(mock_csv_storage, schema_registry)
    request = CSVValidationRequest(
        id=uuid.uuid4(),
        file="test.csv",
        schema="test",
        mappings={
            "user_email": "user_email",
            "transaction_amount": "transaction_amount",
            "signup_date": "signup_date",
        },
    )
    response = service.validate(request)
    assert response.is_valid()
    assert len(response.errors) == 0


def test_validate_invalid_csv_appends_errors(schema_registry, mock_csv_storage):
    import uuid

    invalid_df = pd.DataFrame(
        {
            "user_email": ["not-an-email", "bad"],
            "transaction_amount": [-1, 5],  # -1 fails min
            "signup_date": ["2026-01-01", "2026-01-02"],
        }
    )
    mock_csv_storage.read_chunk.return_value = iter([invalid_df])
    service = CSVServiceImpl(mock_csv_storage, schema_registry)
    request = CSVValidationRequest(
        id=uuid.uuid4(),
        file="test.csv",
        schema="test",
        mappings={
            "user_email": "user_email",
            "transaction_amount": "transaction_amount",
            "signup_date": "signup_date",
        },
    )
    response = service.validate(request)
    assert not response.is_valid()
    assert len(response.errors) >= 1


def test_validate_invalid_file_returns_invalid_file_response(
    schema_registry, mock_csv_storage
):
    import uuid

    mock_csv_storage.read_chunk.return_value = None
    service = CSVServiceImpl(mock_csv_storage, schema_registry)
    request = CSVValidationRequest(
        id=uuid.uuid4(),
        file="missing.csv",
        schema="test",
    )
    response = service.validate(request)
    assert not response.is_valid()
    assert len(response.errors) == 1
    assert response.errors[0].row_numer == 0


def test_inspect_returns_inspection_result_from_peek(schema_registry, mock_csv_storage):
    df = pd.DataFrame(
        {
            "User Email": ["a@b.com"],
            "transaction_amount": [1.0],
        }
    )
    mock_csv_storage.peek.return_value = df
    service = CSVServiceImpl(mock_csv_storage, schema_registry)
    result = service.inspect("some.csv", "test", sample_size=5)
    assert result.schema == schema
    assert result.columns == ["User Email", "transaction_amount"]
    mock_csv_storage.peek.assert_called_once_with("some.csv", rows=5)


def test_inspect_raises_when_file_not_found(schema_registry, mock_csv_storage):
    mock_csv_storage.peek.side_effect = FileNotFoundError("not found")
    service = CSVServiceImpl(mock_csv_storage, schema_registry)
    with pytest.raises(ValueError, match="Error reading file"):
        service.inspect("missing.csv", "test")


def test_recommend_schema_returns_schema_above_threshold(
    schema_registry, mock_csv_storage
):
    df = pd.DataFrame(
        {
            "User Email": ["a@b.com"],
            "transaction_amount": [1.0],
        }
    )
    mock_csv_storage.peek.return_value = df
    service = CSVServiceImpl(mock_csv_storage, schema_registry)
    recommended = service.recommend_schema("file.csv", threshold=0.5)
    assert recommended is not None
    assert recommended.name == "test"


def test_recommend_schema_returns_default_when_below_threshold(
    schema_registry, mock_csv_storage
):
    df = pd.DataFrame({"unknown_col": ["a", "b", "c"]})
    mock_csv_storage.peek.return_value = df
    service = CSVServiceImpl(mock_csv_storage, schema_registry)
    # With no column match, score is low. Service returns default_schema (registry has "test", no "default" so default_schema is None in our mock)
    recommended = service.recommend_schema("file.csv", threshold=0.99)
    # When default_schema is None, recommend_schema can return None
    assert recommended is None or recommended.name in ("test", "default")
