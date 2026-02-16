import uuid

from flask import (
    render_template,
    flash,
    Blueprint,
    current_app,
    redirect,
    url_for,
    request,
)
from app.main.forms import UploadForm, MappingForm
from app.models.inspection import InspectionResult
from app.models.process import CSVValidationRequest
from app.models.schema import Schema

main = Blueprint("main", __name__, template_folder="templates")


@main.route("/", methods=["GET", "POST"])
def index():
    form = UploadForm()
    if form.validate_on_submit():
        try:
            saved_file = current_app.csv_service.upload_file(form.csv.data)
            flash(f"File {saved_file} successfully uploaded.", "success")
            return redirect(url_for("main.map_columns", filename=saved_file))
        except Exception as e:
            flash(f"Error uploading file: {e}", "error")

    return render_template("index.html", form=form)


@main.route("/mapping/<filename>")
def map_columns(filename):
    try:
        available_schemas = current_app.csv_service.available_schemas()
        selected_schema = request.args.get("schema")
        if not selected_schema:
            recommended = current_app.csv_service.recommend_schema(filename)
            selected_schema = recommended.name if recommended else "default"
        results = current_app.csv_service.inspect(filename, selected_schema)
        form = building_mapping_form(results)
        return render_template(
            "mapping.html",
            filename=filename,
            selected_schema=selected_schema,
            available_schemas=available_schemas,
            form=form,
            columns=results.columns,
            sample=results.sample,
        )
    except Exception as e:
        flash(f"Error reading file {filename}: {e}")
        return redirect(url_for("main.index"))


def build_schema_fields_choices(form: MappingForm, schema: Schema) -> MappingForm:
    schema_fields = list(schema.definition.keys())
    choices = [("", "-- Ignore Column --")] + [
        (f, f.replace("_", " ").title()) for f in schema_fields
    ]
    for entry in form.mappings:
        entry.schema_field.choices = choices
    return form


def building_mapping_form(inspection: InspectionResult) -> MappingForm:
    schema_fields = list(inspection.schema.definition.keys())
    choices = [("", "-- Ignore Column --")] + [
        (f, f.replace("_", " ").title()) for f in schema_fields
    ]

    form = MappingForm(schema_name=inspection.schema.name, save_template=False)
    for col in inspection.columns:
        form.mappings.append_entry(
            {
                "csv_column": col,
                "schema_field": inspection.suggestions.get(col, ""),
            }
        )
    for entry in form.mappings:
        entry.schema_field.choices = choices
    return form


@main.post("/process/<filename>")
def process_file(filename):
    form = MappingForm(request.form)
    schema = current_app.schema_registry.get_schema(form.schema_name.data)
    form = build_schema_fields_choices(form, schema)
    if form.validate_on_submit():
        mappings = {
            entry.csv_column.data: entry.schema_field.data
            for entry in form.mappings
            if entry.schema_field.data
        }
        validation_request = CSVValidationRequest(
            id=uuid.uuid4(), file=filename, schema=schema.name, mappings=mappings
        )
        result = current_app.csv_service.validate(validation_request)
        return render_template("result.html", result=result)
    print(request.form)
    return redirect(url_for("main.index"))
