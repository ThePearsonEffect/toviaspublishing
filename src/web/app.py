from __future__ import annotations

from flask import Flask, render_template, request, send_file, redirect, url_for, send_from_directory
from io import BytesIO
from pathlib import Path
import tempfile

from src.config import config, ensure_output_dir
from src.cover.generate import generate_cover, generate_tshirt_design
from src.marketing.details import generate_book_cover_details, generate_tshirt_details


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024

    @app.get("/")
    def index():
        return render_template("grammarly_editor.html", grammarly_client_id=config.grammarly_client_id or "")

    @app.get("/designer")
    def designer():
        return render_template("designer.html")

    @app.get("/files/<path:filename>")
    def serve_file(filename: str):
        return send_from_directory(ensure_output_dir(), filename)

    @app.post("/export")
    def export_text():
        text = request.form.get("text", "")
        buf = BytesIO(text.encode("utf-8"))
        buf.seek(0)
        return send_file(buf, as_attachment=True, download_name="edited.txt", mimetype="text/plain")

    @app.post("/make/cover")
    def make_cover():
        title = request.form.get("title", "")
        author = request.form.get("author", "")
        quote = request.form.get("quote", "")
        out_dir = Path(ensure_output_dir())
        out_path = out_dir / "web_cover.png"
        generate_cover(title, author, quote, out_path)
        details = generate_book_cover_details(title, author, quote)
        cover_url = url_for("serve_file", filename=out_path.name)
        return render_template("designer.html", cover_url=cover_url, details=details)

    @app.post("/make/tshirt")
    def make_tshirt():
        title = request.form.get("title", "")
        text = request.form.get("text", "")
        author = request.form.get("author", "")
        out_dir = Path(ensure_output_dir())
        out_path = out_dir / "web_tshirt.png"
        generate_tshirt_design(text=text, out_path=out_path, title=title or None)
        details = generate_tshirt_details(title, author, text)
        tshirt_url = url_for("serve_file", filename=out_path.name)
        return render_template("designer.html", tshirt_url=tshirt_url, details=details)

    @app.post("/upload")
    def upload():
        f = request.files.get("file")
        if not f:
            return redirect(url_for("designer"))
        out_dir = Path(ensure_output_dir())
        dest = out_dir / f.filename
        f.save(dest)
        uploaded_url = url_for("serve_file", filename=dest.name)
        return render_template("designer.html", upload_url=uploaded_url)

    return app
