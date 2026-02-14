from datetime import datetime
from app.services.file_rename import AppendDateToFileName


def test_can_append_timestamp_to_file_name():
    current_time = datetime(2022, 3, 1, 12, 30, 22)
    file_rename = AppendDateToFileName(provider=lambda: current_time)
    assert str(file_rename.rename("test.csv")) == "test_20220301_123022.csv"
