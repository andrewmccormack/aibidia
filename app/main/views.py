from flask import render_template, flash, Blueprint, current_app, redirect, url_for
from app.main.forms import UploadForm
from app.services import FileWriter, LocalFileWriter, AppendDateToFileName
from datetime import datetime

main = Blueprint("main", __name__, template_folder="templates")


def create_file_writer(app) -> FileWriter:
    return LocalFileWriter(
        app.config["UPLOAD_FOLDER"],
        rename_strategy=AppendDateToFileName(datetime.now),
    )

@main.route("/", methods=["GET", "POST"])
def index():
    form = UploadForm()
    if form.validate_on_submit():
        file_writer = create_file_writer(current_app)
        save_file = file_writer.save_uploaded_file(form.csv.data)
        flash(f"File {save_file.name} successfully uploaded.")
        return redirect(url_for("main.map_columns", file_name=save_file.name))

    return render_template("index.html", form=form)

@main.route("/map/<file_name>")
def map_columns(file_name):
    return render_template("map.html", file_name=file_name.replace("_", ""))
