from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from utils.extract import extract_text_from_upload
from utils.quizgen import generate_quiz
from utils.ai_quiz import generate_quiz_ai
import os

app = Flask(__name__)

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}


def is_allowed_file(filename: str) -> bool:
	return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.get("/")
def index():
	return render_template("index.html")
@app.get("/about")
def about():
	return render_template("about.html")


@app.get("/contact")
def contact():
	return render_template("contact.html")


@app.get("/policy")
def policy():
	return render_template("policy.html")



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
	use_ai = bool(payload.get("use_ai"))
	# Graceful fallback: if no provider credentials are present, disable AI mode
	if use_ai:
		has_openai_like = bool(os.environ.get("AI_API_KEY") or os.environ.get("OPENAI_API_KEY"))
		has_google = bool(os.environ.get("GOOGLE_API_KEY") or (os.environ.get("AI_PROVIDER", "").lower() == "google"))
		if not (has_openai_like or has_google):
			use_ai = False
	if not text:
		return jsonify({"error": "Text is required"}), 400
	try:
		used_ai = False
		provider = None
		fallback_used = False
		ai_error = None
		questions = []
		if use_ai:
			try:
				provider = "google" if os.environ.get("GOOGLE_API_KEY") or (os.environ.get("AI_PROVIDER", "").lower() == "google") else "openai"
				questions = generate_quiz_ai(text, num_questions=num_questions, mode=mode)
				used_ai = True if questions else False
			except Exception as e:
				used_ai = False
				questions = []
				ai_error = str(e)
		if not questions:
			questions = generate_quiz(text, num_questions=num_questions, mode=mode)
			fallback_used = use_ai
		return jsonify({
			"questions": questions,
			"used_ai": used_ai,
			"provider": provider,
			"fallback": fallback_used,
			"ai_error": ai_error
		})
	except Exception as exc:
		return jsonify({"error": f"Quiz generation failed: {exc}"}), 500


if __name__ == "__main__":
	port = int(os.environ.get("PORT", 5000))
	app.run(host="0.0.0.0", port=port, debug=True)
