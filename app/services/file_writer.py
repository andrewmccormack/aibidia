from datetime import datetime
from typing import Protocol, Optional, Callable
from pathlib import Path
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from mimetypes import guess_type
from .file_rename import FileRename, PreserveFileName


class FileWriter(Protocol):
    def save_uploaded_file(self, file: FileStorage) -> Path: ...


def is_valid_csv(file: FileStorage) -> bool:
    if not file.filename.endswith(".csv"):
        return False
    mime_type, _ = guess_type(file.filename)
    if mime_type not in ("text/csv", "application/vnd.ms-excel", "text/plain"):
        return False
    return True


class LocalFileWriter(FileWriter):
    def __init__(
        self, upload_folder: str, rename_strategy: Optional[FileRename]
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
