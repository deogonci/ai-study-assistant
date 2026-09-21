import os
import uuid

from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from pypdf import PdfReader

from summariser import summarise_notes
from quiz_generator import generate_quiz

from database import (
    initialise_database,
    save_document,
    get_all_documents,
    get_document,
    delete_document,
    save_quiz_result,
    get_quiz_results,
    get_dashboard_stats
)

app = Flask(__name__)
app.secret_key = "dev-secret-key"

initialise_database()

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
    documents = get_all_documents()
    quiz_results = get_quiz_results()
    stats = get_dashboard_stats()

    return render_template(
        "index.html",
        documents=documents,
        quiz_results=quiz_results,
        stats=stats
    )

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

    document_id = str(uuid.uuid4())

    stored_filename = f"{document_id}_{filename}"

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        stored_filename
    )

    file.save(filepath)

    if filename.lower().endswith(".txt"):
        text = read_text_file(filepath)

    elif filename.lower().endswith(".pdf"):
        text = read_pdf_file(filepath)

    else:
        return "Unsupported file type", 400

    save_document(
        document_id,
        filename,
        filepath
    )

    session["document_id"] = document_id
    session["filename"] = filename
    session["filepath"] = filepath

    return render_template(
        "workspace.html",
        filename=filename,
        text=text
    )

@app.route("/summarise", methods=["POST"])
def summarise():
    filepath = session.get("filepath")

    if not filepath or not os.path.exists(filepath):
        return redirect(url_for("home"))

    if filepath.lower().endswith(".txt"):
        text = read_text_file(filepath)

    elif filepath.lower().endswith(".pdf"):
        text = read_pdf_file(filepath)

    else:
        return "Unsupported file type", 400

    summary = summarise_notes(text)

    return render_template(
        "summary.html",
        filename=session.get("filename"),
        summary=summary
    )

@app.route("/quiz", methods=["POST"])
def quiz():
    filepath = session.get("filepath")

    if not filepath or not os.path.exists(filepath):
        return redirect(url_for("home"))

    if filepath.lower().endswith(".txt"):
        text = read_text_file(filepath)

    elif filepath.lower().endswith(".pdf"):
        text = read_pdf_file(filepath)

    else:
        return "Unsupported file type", 400

    questions = generate_quiz(text)

    session["quiz_answers"] = [
        question["answer"]
        for question in questions
    ]

    return render_template(
        "quiz.html",
        filename=session.get("filename"),
        questions=questions
    )

@app.route("/submit-quiz", methods=["POST"])
def submit_quiz():
    correct_answers = session.get("quiz_answers", [])

    score = 0
    results = []

    for index, correct_answer in enumerate(correct_answers):
        user_answer = request.form.get(
            f"answer_{index}",
            ""
        ).strip().lower()

        correct_answer = correct_answer.strip().lower()

        is_correct = user_answer == correct_answer

        if is_correct:
            score += 1

        results.append({
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct
        })

    total = len(results)

    percentage = round((score / total) * 100) if total > 0 else 0

    document_id = session.get("document_id")

    if document_id and total > 0:
        save_quiz_result(
            document_id,
            score,
            total,
            percentage
        )

    return render_template(
        "quiz_results.html",
        score=score,
        total=total,
        percentage=percentage,
        results=results
    )

@app.route("/document/<document_id>")
def open_document(document_id):
    document = get_document(document_id)

    if document is None:
        return "Document not found", 404

    filepath = document["filepath"]

    if not os.path.exists(filepath):
        return "Document file no longer exists", 404

    if filepath.lower().endswith(".txt"):
        text = read_text_file(filepath)

    elif filepath.lower().endswith(".pdf"):
        text = read_pdf_file(filepath)

    else:
        return "Unsupported file type", 400

    session["document_id"] = document["document_id"]
    session["filename"] = document["filename"]
    session["filepath"] = filepath

    return render_template(
        "workspace.html",
        filename=document["filename"],
        text=text
    )

@app.route("/document/<document_id>/delete", methods=["POST"])
def remove_document(document_id):
    document = get_document(document_id)

    if document is None:
        return "Document not found", 404

    filepath = document["filepath"]

    delete_document(document_id)

    if os.path.exists(filepath):
        os.remove(filepath)

    if session.get("document_id") == document_id:
        session.pop("document_id", None)
        session.pop("filename", None)
        session.pop("filepath", None)
        session.pop("quiz_answers", None)

    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
    