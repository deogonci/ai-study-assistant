import os

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from pypdf import PdfReader


app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
ALLOWED_EXTENSIONS = {"pdf", "txt"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def read_text_file(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        return file.read()

def read_pdf_file(filepath):
    reader = PdfReader(filepath)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "No file selected", 400

    file = request.files["file"]

    if file.filename == "":
        return "No file selected", 400

    if not allowed_file(file.filename):
        return "Only PDF and TXT files are allowed", 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    file.save(filepath)

    if filename.lower().endswith(".txt"):
        text = read_text_file(filepath)

    elif filename.lower().endswith(".pdf"):
        text = read_pdf_file(filepath)

    else:
        return "Unsupported file type", 400


    return f"""
    <h1>{filename}</h1>
    <h2>Extracted Notes:</h2>
    <pre>{text}</pre>
    """


if __name__ == "__main__":
    app.run(debug=True)