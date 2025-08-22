from flask import Flask, jsonify, request
import os

# Create Flask app
app = Flask(__name__)

# Import quiz generation utilities
try:
    import sys
    from pathlib import Path
    
    # Add project root to path
    ROOT = Path(__file__).resolve().parent.parent
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    
    from utils.extract import extract_text_from_upload
    from utils.quizgen import generate_quiz
    from utils.ai_quiz import generate_quiz_ai
    
    UTILS_AVAILABLE = True
except ImportError:
    UTILS_AVAILABLE = False

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}

def is_allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return jsonify({
        "message": "Quiz Generator App is running!",
        "status": "success",
        "utils_available": UTILS_AVAILABLE,
        "endpoints": [
            "/test",
            "/upload (POST)",
            "/generate-quiz (POST)",
            "/health"
        ]
    })

@app.route("/test")
def test():
    return jsonify({
        "message": "Flask app is working on Vercel!",
        "status": "success",
        "utils_available": UTILS_AVAILABLE
    })

@app.route("/about")
def about():
    return jsonify({
        "message": "About page",
        "status": "success"
    })

@app.route("/contact")
def contact():
    return jsonify({
        "message": "Contact page",
        "status": "success"
    })

@app.route("/policy")
def policy():
    return jsonify({
        "message": "Policy page",
        "status": "success"
    })

@app.route("/upload", methods=["POST"])
def upload():
    if not UTILS_AVAILABLE:
        return jsonify({
            "error": "Text extraction utilities not available",
            "status": "error"
        }), 500
    
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    
    if not is_allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type. Use PDF, DOCX, or TXT."}), 400

    try:
        text_content = extract_text_from_upload(file)
        return jsonify({
            "text": text_content,
            "status": "success",
            "filename": file.filename
        })
    except Exception as exc:
        return jsonify({"error": f"Failed to extract text: {exc}"}), 500

@app.route("/generate-quiz", methods=["POST"])
def generate_quiz_endpoint():
    if not UTILS_AVAILABLE:
        return jsonify({
            "error": "Quiz generation utilities not available",
            "status": "error"
        }), 500
    
    payload = request.get_json(silent=True) or {}
    text = (payload.get("text") or "").strip()
    num_questions = int(payload.get("num_questions") or 5)
    num_questions = max(1, min(100, num_questions))
    mode = (payload.get("mode") or "mcq").strip().lower()
    use_ai = bool(payload.get("use_ai"))
    
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
            "ai_error": ai_error,
            "status": "success"
        })
    except Exception as exc:
        return jsonify({"error": f"Quiz generation failed: {exc}"}), 500

# Health check endpoint
@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "quiz-generator",
        "utils_available": UTILS_AVAILABLE
    })

if __name__ == "__main__":
    app.run(debug=False)



