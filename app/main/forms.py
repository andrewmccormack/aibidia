from flask import current_app
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileSize, FileAllowed
from mimetypes import guess_type

MAX_FILE_SIZE = current_app.config["MAX_FILE_SIZE"]


class UploadForm(FlaskForm):
    csv = FileField(
        "CSV File",
        validators=[FileRequired(), FileSize(MAX_FILE_SIZE), FileAllowed(["csv"])],
    )
