from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open
from app.services.file_writer import LocalFileStorage


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
