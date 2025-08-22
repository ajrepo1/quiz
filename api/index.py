from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os

# Create Flask app directly in this file to avoid import issues
app = Flask(__name__)

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}

def is_allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/policy")
def policy():
    return render_template("policy.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    if not is_allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type. Use PDF, DOCX, or TXT."}), 400

    try:
        # For now, return a simple response to test if the route works
        return jsonify({"message": "File upload endpoint working"})
    except Exception as exc:
        return jsonify({"error": f"Failed to process file: {exc}"}), 500

@app.route("/generate-quiz", methods=["POST"])
def generate_quiz_endpoint():
    payload = request.get_json(silent=True) or {}
    text = (payload.get("text") or "").strip()
    if not text:
        return jsonify({"error": "Text is required"}), 400
    
    # For now, return a simple response to test if the route works
    return jsonify({"message": "Quiz generation endpoint working", "text_length": len(text)})

# Test route to verify deployment
@app.route("/test")
def test():
    return {"message": "Flask app is working on Vercel!", "status": "success"}

if __name__ == "__main__":
    app.run(debug=False)



