import uuid
import pytest
from app.models.process import (
    CSVValidationRequest,
    CSVValidationResponse,
    CSVValidationError,
)


@pytest.fixture
def request_id():
    return uuid.uuid4()


def test_csv_validation_response_is_valid_when_no_errors(request_id):
    response = CSVValidationResponse(
        request_id=request_id,
        file="test.csv",
        schema="default",
        errors=[],
    )
    assert response.is_valid() is True


def test_csv_validation_response_is_invalid_when_errors_present(request_id):
    response = CSVValidationResponse(
        request_id=request_id,
        file="test.csv",
        schema="default",
        errors=[CSVValidationError(row_numer=1, error="invalid")],
    )
    assert response.is_valid() is False


def test_invalid_file_factory(request_id):
    request = CSVValidationRequest(
        id=request_id,
        file="missing.csv",
        schema="default",
    )
    response = CSVValidationResponse.invalid_file(request)
    assert response.request_id == request_id
    assert response.file == "missing.csv"
    assert response.schema == "default"
    assert len(response.errors) == 1
    assert response.errors[0].row_numer == 0
    assert "Could not read file" in response.errors[0].error


def test_from_request(request_id):
    request = CSVValidationRequest(
        id=request_id,
        file="data.csv",
        schema="test",
        mappings={"Col A": "col_a"},
        error_threshold=50,
    )
    response = CSVValidationResponse.from_request(request)
    assert response.request_id == request_id
    assert response.file == "data.csv"
    assert response.schema == "test"
    assert response.errors == []
