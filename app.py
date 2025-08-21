from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from utils.extract import extract_text_from_upload
from utils.quizgen import generate_quiz
import os

app = Flask(__name__)

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}


def is_allowed_file(filename: str) -> bool:
	return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.get("/")
def index():
	return render_template("index.html")


@app.post("/upload")
def upload():
	if "file" not in request.files:
		return jsonify({"error": "No file part"}), 400
	file = request.files["file"]
	if file.filename == "":
		return jsonify({"error": "No selected file"}), 400
	if not is_allowed_file(file.filename):
		return jsonify({"error": "Unsupported file type. Use PDF, DOCX, or TXT."}), 400

	# Process directly from file stream; no need to save to disk
	try:
		text_content = extract_text_from_upload(file)
		return jsonify({"text": text_content})
	except Exception as exc:
		return jsonify({"error": f"Failed to extract text: {exc}"}), 500


@app.post("/generate-quiz")
def generate_quiz_endpoint():
	payload = request.get_json(silent=True) or {}
	text = (payload.get("text") or "").strip()
	num_questions = int(payload.get("num_questions") or 5)
	# Enforce quiz generation limit: 1..100
	num_questions = max(1, min(100, num_questions))
	mode = (payload.get("mode") or "mcq").strip().lower()
	if not text:
		return jsonify({"error": "Text is required"}), 400
	try:
		questions = generate_quiz(text, num_questions=num_questions, mode=mode)
		return jsonify({"questions": questions})
	except Exception as exc:
		return jsonify({"error": f"Quiz generation failed: {exc}"}), 500


if __name__ == "__main__":
	port = int(os.environ.get("PORT", 5000))
	app.run(host="0.0.0.0", port=port, debug=True)
