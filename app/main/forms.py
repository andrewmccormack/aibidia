from flask import current_app
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileSize, FileAllowed
from mimetypes import guess_type

from wtforms import HiddenField, SelectField, FieldList, BooleanField, FormField, SubmitField

MAX_FILE_SIZE = current_app.config["MAX_FILE_SIZE"]


class UploadForm(FlaskForm):
    csv = FileField(
        "CSV File",
        validators=[FileRequired(), FileSize(MAX_FILE_SIZE), FileAllowed(["csv"])],
    )

class MappingEntryForm(FlaskForm):
    class Meta:
        csrf = False
    csv_column = HiddenField("CSV Column")
    schema_field = SelectField("Target", choices=[])  # set at runtime in the view


class MappingForm(FlaskForm):
    schema_name = HiddenField("Schema")
    save_template = BooleanField("Save these mappings for future files", default=False, id="save-template")
    mappings = FieldList(FormField(MappingEntryForm))
    submit = SubmitField("Process CSV")

