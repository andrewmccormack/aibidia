from .csv_inspector import CSVInspector
from .file_rename import AppendDateToFileName
from .file_storage import LocalFileStorage, FileStorage
from .schema_registry import SchemaRegistry, SchemaRepository, LocalSchemaRepository


def init_services(app):
    app.file_storage = LocalFileStorage(app.config["UPLOAD_FOLDER"], AppendDateToFileName())
    app.schema_registry =  SchemaRegistry(LocalSchemaRepository(app.config["SCHEMA_FOLDER"]))
    app.csv_inspector = CSVInspector(app.file_storage, app.schema_registry)