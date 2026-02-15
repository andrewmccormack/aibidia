from .csv_service import CSVServiceImpl
from .csv_storage import LocalFileStorage, AppendDateToFileName
from .schema_registry import SchemaRegistry, SchemaRepository, LocalSchemaRepository


def init_services(app):
    app.file_storage = LocalFileStorage(
        app.config["UPLOAD_FOLDER"], AppendDateToFileName()
    )
    app.schema_registry = SchemaRegistry(
        LocalSchemaRepository(app.config["SCHEMA_FOLDER"])
    )
    app.csv_service = CSVServiceImpl(app.file_storage, app.schema_registry)
