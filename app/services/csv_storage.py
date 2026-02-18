import csv
from datetime import datetime
import charset_normalizer
from typing import Protocol, Optional, Callable
from pathlib import Path
import pandas as pd
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from mimetypes import guess_type


class CSVStorage(Protocol):
    def save_uploaded_file(self, file: FileStorage) -> Path: ...
    def resolve_path(self, file_name: str) -> Path: ...
    def peek(self, file_name: str, rows: int = 5) -> pd.DataFrame: ...
    def read_chunk(self, file_name: str, size=10000) -> pd.DataFrame: ...
    def read_all(self, file_name: str) -> pd.DataFrame: ...


class FileRename(Protocol):
    def rename(self, file_path: str) -> Path: ...


class AppendDateToFileName(FileRename):
    def __init__(self, provider: Optional[Callable[[], datetime]] = None) -> None:
        self.provider = provider or datetime.now

    def rename(self, file_path: str) -> Path:
        file_path = Path(file_path)
        timestamp = self.provider().strftime("%Y%m%d_%H%M%S")
        return file_path.with_name(f"{file_path.stem}_{timestamp}{file_path.suffix}")


class PreserveFileName(FileRename):
    def rename(self, file_path: str) -> Path:
        return Path(file_path)


def is_valid_csv(file: CSVStorage) -> bool:
    if not file.filename.endswith(".csv"):
        return False
    mime_type, _ = guess_type(file.filename)
    if mime_type not in ("text/csv", "application/vnd.ms-excel", "text/plain"):
        return False
    return True


def get_encoding(file) -> str:
    with open(file, "rb") as f:
        sample = f.read(50000)
        results = charset_normalizer.from_bytes(sample)
        return str(results.best().encoding) if results.best() else "utf-8"

def has_header(file, encoding='utf-8', sample_size=1024) -> bool:
        """Detect if CSV has a header row using csv.Sniffer"""
        with open(file, 'r', encoding=encoding) as f:
            sample = f.read(sample_size)
            sniffer = csv.Sniffer()
            return sniffer.has_header(sample)


class LocalFileStorage(CSVStorage):
    def __init__(
        self, upload_folder: str, rename_strategy: Optional[FileRename] = None
    ) -> None:
        self.upload_folder = upload_folder
        self.path = Path(upload_folder)
        self.rename_strategy = rename_strategy or PreserveFileName()
        if self.path.exists():
            self.path.mkdir(parents=True, exist_ok=True)

    def save_uploaded_file(self, file: FileStorage) -> Path:
        file_name = self.rename_strategy.rename(secure_filename(file.filename))
        with open(self.path / file_name, "wb") as f:
            data = file.read()
            f.write(data)
            return Path(f.name)

    def peek(self, file_name: str, rows: int = 5) -> pd.DataFrame:
        return self._read_csv(file_name, nrows=rows)

    def read_chunk(self, file_name: str, size=10000) -> pd.DataFrame:
        return self._read_csv(file_name, chunksize=size)

    def read_all(self, file_name: str) -> pd.DataFrame:
        return self._read_csv(file_name)

    def resolve_path(self, file_name: str) -> Path:
        full_path = self.path / file_name
        if full_path.exists():
            return full_path
        raise FileNotFoundError(f"File {file_name} not found")

    def _read_csv(self, file_name: str, **kwargs) -> pd.DataFrame:
        resolved_path = self.resolve_path(file_name)
        encoding = get_encoding(resolved_path)
        header = 'infer' if has_header(resolved_path, encoding=encoding) else None
        return pd.read_csv(resolved_path, encoding=encoding, header=header, **kwargs)
