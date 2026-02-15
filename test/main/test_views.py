"""Tests for main blueprint views."""
import io
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


def test_index_get_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200


def test_index_post_upload_redirects_to_mapping(app, client, tmp_path):
    app.config["UPLOAD_FOLDER"] = str(tmp_path / "uploads")
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    app.config["SCHEMA_FOLDER"] = str(tmp_path / "schemas")
    Path(app.config["SCHEMA_FOLDER"]).mkdir(parents=True, exist_ok=True)
    (Path(app.config["SCHEMA_FOLDER"]) / "default.json").write_text(
        json.dumps({"email": {"type": "string"}})
    )
    from app.services import init_services
    init_services(app)

    data = {"csv": (io.BytesIO(b"col1,col2\n1,2"), "test.csv")}
    response = client.post("/", data=data, content_type="multipart/form-data", follow_redirects=False)
    assert response.status_code == 302
    assert "mapping" in response.location


def test_mapping_get_returns_200_when_file_exists(app, client, tmp_path):
    uploads = tmp_path / "uploads"
    uploads.mkdir(parents=True)
    schemas_dir = tmp_path / "schemas"
    schemas_dir.mkdir(parents=True)
    (schemas_dir / "default.json").write_text(json.dumps({"a": {"type": "string"}}))
    (uploads / "sample.csv").write_text("a,b\n1,2")

    app.config["UPLOAD_FOLDER"] = str(uploads)
    app.config["SCHEMA_FOLDER"] = str(schemas_dir)
    from app.services import init_services
    init_services(app)

    response = client.get("/mapping/sample.csv")
    assert response.status_code == 200


def test_mapping_get_redirects_to_index_when_file_missing(app, client, tmp_path):
    uploads = tmp_path / "uploads"
    uploads.mkdir(parents=True)
    schemas_dir = tmp_path / "schemas"
    schemas_dir.mkdir(parents=True)
    (schemas_dir / "default.json").write_text(json.dumps({"x": {"type": "string"}}))

    app.config["UPLOAD_FOLDER"] = str(uploads)
    app.config["SCHEMA_FOLDER"] = str(schemas_dir)
    from app.services import init_services
    init_services(app)

    response = client.get("/mapping/nonexistent.csv", follow_redirects=True)
    assert response.status_code == 200
    # Should have been redirected to index and flashed error
    assert b"Error reading file" in response.data or response.request.path == "/"


@pytest.mark.parametrize("path", ["/", "/mapping/foo.csv"])
def test_pages_dont_crash_with_500(client, path):
    # Minimal check: no server error. / works; /mapping/foo may redirect when file missing
    response = client.get(path, follow_redirects=True)
    assert response.status_code in (200, 302)
    if response.status_code == 200:
        assert b"500" not in response.data