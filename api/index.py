from flask import Flask, jsonify, request, send_from_directory
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
    # Return HTML interface instead of JSON
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Quiz Generator App</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; }
            .form-group { margin: 15px 0; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, select, textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .result { background: white; padding: 15px; border-radius: 4px; margin-top: 20px; }
            .error { color: red; }
            .success { color: green; }
        </style>
    </head>
    <body>
        <h1>Quiz Generator App</h1>
        <p>Generate custom quizzes from PDF, DOCX, or text input.</p>
        
        <div class="container">
            <h3>Upload File</h3>
            <form id="uploadForm">
                <div class="form-group">
                    <label for="file">Choose file (PDF, DOCX, TXT):</label>
                    <input type="file" id="file" name="file" accept=".pdf,.docx,.txt" required>
                </div>
                <button type="submit">Extract Text</button>
            </form>
            <div id="uploadResult"></div>
        </div>
        
        <div class="container">
            <h3>Or Paste Text</h3>
            <div class="form-group">
                <label for="textInput">Text content:</label>
                <textarea id="textInput" rows="6" placeholder="Paste your text here..."></textarea>
            </div>
        </div>
        
        <div class="container">
            <h3>Generate Quiz</h3>
            <form id="quizForm">
                <div class="form-group">
                    <label for="numQuestions">Number of questions (1-100):</label>
                    <input type="number" id="numQuestions" min="1" max="100" value="5">
                </div>
                <div class="form-group">
                    <label for="quizMode">Quiz type:</label>
                    <select id="quizMode">
                        <option value="mcq">Multiple Choice</option>
                        <option value="truefalse">True/False</option>
                        <option value="mixed">Mixed</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>
                        <input type="checkbox" id="useAI"> Use AI (if API keys available)
                    </label>
                </div>
                <button type="submit">Generate Quiz</button>
            </form>
            <div id="quizResult"></div>
        </div>
        
        <script>
            document.getElementById('uploadForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData();
                const fileInput = document.getElementById('file');
                formData.append('file', fileInput.files[0]);
                
                try {
                    const response = await fetch('/upload', {
                        method: 'POST',
                        body: formData
                    });
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        document.getElementById('textInput').value = result.text;
                        document.getElementById('uploadResult').innerHTML = 
                            '<div class="success">Text extracted successfully! Length: ' + result.text.length + ' characters</div>';
                    } else {
                        document.getElementById('uploadResult').innerHTML = 
                            '<div class="error">Error: ' + result.error + '</div>';
                    }
                } catch (error) {
                    document.getElementById('uploadResult').innerHTML = 
                        '<div class="error">Error: ' + error.message + '</div>';
                }
            });
            
            document.getElementById('quizForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const text = document.getElementById('textInput').value.trim();
                if (!text) {
                    alert('Please provide text content first (upload file or paste text)');
                    return;
                }
                
                const data = {
                    text: text,
                    num_questions: parseInt(document.getElementById('numQuestions').value),
                    mode: document.getElementById('quizMode').value,
                    use_ai: document.getElementById('useAI').checked
                };
                
                try {
                    const response = await fetch('/generate-quiz', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(data)
                    });
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        let html = '<div class="success"><h4>Quiz Generated Successfully!</h4>';
                        if (result.used_ai) {
                            html += '<p>Generated using AI (' + result.provider + ')</p>';
                        } else if (result.fallback) {
                            html += '<p>AI failed, used fallback method</p>';
                        } else {
                            html += '<p>Generated using fallback method</p>';
                        }
                        html += '<h5>Questions:</h5>';
                        
                        result.questions.forEach((q, i) => {
                            html += '<div style="margin: 15px 0; padding: 10px; border: 1px solid #ddd; border-radius: 4px;">';
                            html += '<strong>Question ' + (i+1) + ':</strong> ' + q.question + '<br>';
                            if (q.options) {
                                q.options.forEach((opt, j) => {
                                    html += '<input type="radio" name="q' + i + '" value="' + j + '"> ' + opt + '<br>';
                                });
                            }
                            if (q.answer !== undefined) {
                                html += '<strong>Answer:</strong> ' + q.answer + '<br>';
                            }
                            html += '</div>';
                        });
                        html += '</div>';
                        
                        document.getElementById('quizResult').innerHTML = html;
                    } else {
                        document.getElementById('quizResult').innerHTML = 
                            '<div class="error">Error: ' + result.error + '</div>';
                    }
                } catch (error) {
                    document.getElementById('quizResult').innerHTML = 
                        '<div class="error">Error: ' + error.message + '</div>';
                }
            });
        </script>
    </body>
    </html>
    """
    return html_content

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



