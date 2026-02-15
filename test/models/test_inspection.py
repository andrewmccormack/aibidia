import pytest
from app.models.schema import Schema
from app.models.inspection import InspectionResult


@pytest.fixture
def schema():
    return Schema("test", {"user_email": {}, "amount": {}, "date": {}})


def test_score_full_match(schema):
    result = InspectionResult(
        schema=schema,
        columns=["User Email", "Amount", "Date"],
        sample=[],
        suggestions={"User Email": "user_email", "Amount": "amount", "Date": "date"},
    )
    assert result.score == 1.0


def test_score_partial_match(schema):
    result = InspectionResult(
        schema=schema,
        columns=["col1", "col2"],
        sample=[],
        suggestions={"col1": "user_email", "col2": "amount"},
    )
    assert result.score == 2 / 3


def test_score_no_match(schema):
    result = InspectionResult(
        schema=schema,
        columns=["x", "y"],
        sample=[],
        suggestions={"x": None, "y": None},
    )
    assert result.score == 0.0


def test_score_ignores_none_in_suggestions(schema):
    result = InspectionResult(
        schema=schema,
        columns=["a", "b", "c"],
        sample=[],
        suggestions={"a": "user_email", "b": None, "c": "amount"},
    )
    assert result.score == 2 / 3
