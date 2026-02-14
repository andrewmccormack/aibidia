from pathlib import Path
from typing import Protocol, Optional, Callable
from datetime import datetime


class FileRename(Protocol):
    def rename(self, file_path: str) -> Path: ...


class AppendDateToFileName(FileRename):
    def __init__(self, provider: Optional[Callable[[], datetime]]) -> None:
        self.provider = provider or datetime.now

    def rename(self, file_path: str) -> Path:
        file_path = Path(file_path)
        timestamp = self.provider().strftime("%Y%m%d_%H%M%S")
        return file_path.with_name(f"{file_path.stem}_{timestamp}{file_path.suffix}")


class PreserveFileName(FileRename):
    def rename(self, file_path: str) -> Path:
        return Path(file_path)
