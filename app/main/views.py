from flask import render_template, flash, Blueprint, current_app, redirect, url_for

import app.services.file_storage
from app.main.forms import UploadForm
from app.services import FileStorage, LocalFileStorage, AppendDateToFileName
from datetime import datetime

main = Blueprint("main", __name__, template_folder="templates")


@main.route("/", methods=["GET", "POST"])
def index():
    form = UploadForm()
    if form.validate_on_submit():
        try:
            save_file = current_app.file_storage.save_uploaded_file(form.csv.data)
            flash(f"File {save_file.name} successfully uploaded.")
            return redirect(url_for("main.map_columns", filename=save_file.name))
        except Exception as e:
            flash(f"Error uploading file: {e}", "error")

    return render_template("index.html", form=form)

@main.route("/mapping/<filename>")
def map_columns(filename):

    try:
        results = current_app.csv_inspector.inspect(filename)

        return render_template("mapping.html",
                               filename=filename,
                               columns=results.columns,
                               sample=results.sample,
                               suggestions=results.suggestions,
                               schema_fields=results.schema.definition.keys())
    except Exception as e:
        flash(f"Error reading file {filename}: {e}")
        return redirect(url_for("main.index"))

@main.route("/process/<filename>")
def process_file(filename):

    try:
        results = current_app.csv_inspector.inspect(filename)

        return render_template("mapping.html",
                               filename=filename,
                               columns=results.columns,
                               sample=results.sample,
                               suggestions=results.suggestions,
                               schema_fields=results.schema.definition.keys())
    except Exception as e:
        flash(f"Error reading file {filename}: {e}")
        return redirect(url_for("main.index"))
