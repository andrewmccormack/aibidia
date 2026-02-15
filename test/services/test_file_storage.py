from pathlib import Path
from datetime import datetime
from unittest.mock import MagicMock, patch, mock_open

import pandas as pd
import pytest

from app.services.csv_storage import (
    LocalFileStorage,
    AppendDateToFileName,
    PreserveFileName,
    is_valid_csv,
)


def test_can_append_timestamp_to_file_name():
    current_time = datetime(2022, 3, 1, 12, 30, 22)
    file_rename = AppendDateToFileName(provider=lambda: current_time)
    assert str(file_rename.rename("test.csv")) == "test_20220301_123022.csv"


def test_preserve_file_name_returns_path_unchanged():
    renamer = PreserveFileName()
    assert renamer.rename("data/myfile.csv") == Path("data/myfile.csv")
    assert renamer.rename("report.xlsx") == Path("report.xlsx")


def test_is_valid_csv_accepts_csv_extension_and_mime():
    f = MagicMock()
    f.filename = "data.csv"
    with patch("app.services.csv_storage.guess_type", return_value=("text/csv", None)):
        assert is_valid_csv(f) is True


def test_is_valid_csv_rejects_non_csv_extension():
    f = MagicMock()
    f.filename = "data.txt"
    assert is_valid_csv(f) is False


def test_is_valid_csv_rejects_wrong_mime():
    f = MagicMock()
    f.filename = "data.csv"
    with patch(
        "app.services.csv_storage.guess_type", return_value=("application/json", None)
    ):
        assert is_valid_csv(f) is False


def test_when_writing_a_valid_file():
    data = b"col1,col2\n1,2"
    file_writer = LocalFileStorage(upload_folder="test/tmp", rename_strategy=None)
    uploaded_file = MagicMock(filename="test.csv", mimetype="text/csv")
    uploaded_file.read.return_value = data
    mock_write = mock_open()
    with patch("builtins.open", mock_write):
        file_writer.save_uploaded_file(uploaded_file)
        mock_write.assert_called_once_with(Path("test/tmp/test.csv"), "wb")
        mock_write().write.assert_called_once_with(data)


def test_save_uploaded_file_with_rename_strategy():
    data = b"x,y\n1,2"
    current_time = datetime(2022, 4, 15, 9, 0, 0)
    renamer = AppendDateToFileName(provider=lambda: current_time)
    file_writer = LocalFileStorage(upload_folder="test/tmp", rename_strategy=renamer)
    uploaded_file = MagicMock(filename="input.csv", mimetype="text/csv")
    uploaded_file.read.return_value = data
    mock_write = mock_open()
    with patch("builtins.open", mock_write):
        file_writer.save_uploaded_file(uploaded_file)
        mock_write.assert_called_once_with(
            Path("test/tmp/input_20220415_090000.csv"), "wb"
        )


def test_resolve_path_returns_path_when_file_exists(tmp_path):
    (tmp_path / "existing.csv").write_text("a,b\n1,2")
    storage = LocalFileStorage(upload_folder=str(tmp_path))
    resolved = storage.resolve_path("existing.csv")
    assert resolved == tmp_path / "existing.csv"


def test_resolve_path_raises_when_file_missing(tmp_path):
    storage = LocalFileStorage(upload_folder=str(tmp_path))
    with pytest.raises(FileNotFoundError, match="File missing.csv not found"):
        storage.resolve_path("missing.csv")


def test_peek_reads_first_n_rows(tmp_path):
    csv_path = tmp_path / "sample.csv"
    csv_path.write_text("col1,col2\n1,2\n3,4\n5,6\n7,8")
    storage = LocalFileStorage(upload_folder=str(tmp_path))
    df = storage.peek("sample.csv", rows=2)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df.columns) == ["col1", "col2"]


def test_read_all_returns_full_dataframe(tmp_path):
    csv_path = tmp_path / "full.csv"
    csv_path.write_text("a,b\n1,2\n3,4")
    storage = LocalFileStorage(upload_folder=str(tmp_path))
    df = storage.read_all("full.csv")
    assert len(df) == 2
    assert list(df["a"]) == [1, 3]
    assert list(df["b"]) == [2, 4]


def test_read_chunk_returns_iterator_of_chunks(tmp_path):
    csv_path = tmp_path / "chunked.csv"
    lines = "x,y\n" + "\n".join(f"{i},{i * 2}" for i in range(5))
    csv_path.write_text(lines)
    storage = LocalFileStorage(upload_folder=str(tmp_path))
    chunks = storage.read_chunk("chunked.csv", size=2)
    chunk_list = list(chunks)
    assert len(chunk_list) >= 1
    total_rows = sum(len(c) for c in chunk_list)
    assert total_rows == 5
