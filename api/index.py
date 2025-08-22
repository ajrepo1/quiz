from flask import Flask, jsonify

# Create Flask app
app = Flask(__name__)

@app.route("/")
def index():
    return jsonify({
        "message": "Quiz Generator App is running!",
        "status": "success",
        "endpoints": [
            "/test",
            "/upload (POST)",
            "/generate-quiz (POST)"
        ]
    })

@app.route("/test")
def test():
    return jsonify({
        "message": "Flask app is working on Vercel!",
        "status": "success"
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
    return jsonify({
        "message": "File upload endpoint working",
        "status": "success"
    })

@app.route("/generate-quiz", methods=["POST"])
def generate_quiz_endpoint():
    return jsonify({
        "message": "Quiz generation endpoint working",
        "status": "success"
    })

# Health check endpoint
@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "quiz-generator"
    })

if __name__ == "__main__":
    app.run(debug=False)



