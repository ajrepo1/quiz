# Quiz Generator App

A Flask web application that generates custom quizzes from PDF, DOCX, or pasted text. Supports multiple quiz types including Multiple Choice Questions (MCQ), True/False, and Mixed formats.

## Features

- **File Upload Support**: Upload PDF, DOCX, or TXT files to extract text
- **Text Input**: Paste text directly into the application
- **Multiple Quiz Types**:
  - MCQ (Multiple Choice Questions)
  - True/False questions
  - Mixed (combination of MCQ and True/False)
- **Customizable**: Set the number of questions (1-100)
- **Smart Generation**: Uses heuristics to identify keywords and create meaningful questions

## Project Structure

```
quiz/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── utils/
│   ├── __init__.py       # Package initialization
│   ├── extract.py        # Text extraction from files
│   └── quizgen.py        # Quiz generation logic
├── templates/
│   └── index.html        # Main HTML template
└── static/
    ├── style.css         # CSS styling
    └── script.js         # Frontend JavaScript
```

## Setup Instructions

### Prerequisites
- Python 3.10 or higher
- Windows (tested on Windows 10/11)

### Installation

1. **Clone or download the project**
   ```bash
   cd C:\Users\hp\Documents\quiz
   ```

2. **Create a virtual environment**
   ```bash
   py -m venv .venv
   ```

3. **Activate the virtual environment**
   ```bash
   .\.venv\Scripts\Activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. **Start the Flask server**
   ```bash
   python app.py
   ```

2. **Open your browser**
   Navigate to: http://localhost:5000

## Usage

1. **Upload a File**: Choose a PDF, DOCX, or TXT file and click "Extract Text"
2. **Or Paste Text**: Type or paste text directly into the text area
3. **Configure Quiz**: Set the number of questions and choose quiz type
4. **Generate**: Click "Generate" to create your quiz
5. **Review**: Use "Show Answers" to see correct responses

## Quiz Types

- **MCQ**: Traditional multiple choice with 4 options
- **True/False**: Simple true/false statements
- **Mixed**: Combination of MCQ and True/False questions

## Dependencies

- **Flask**: Web framework
- **PyPDF2**: PDF text extraction
- **python-docx**: DOCX text extraction
- **Werkzeug**: WSGI utilities

## Development

The application runs in debug mode by default, which means:
- Auto-reloads when code changes
- Detailed error messages
- Development server (not for production)

## Notes

- Text extraction quality depends on the source document format
- Quiz generation uses simple heuristics and may not always produce perfect questions
- For production use, consider using a production WSGI server like Gunicorn

## Deploying Publicly

### Quick option: ngrok (share your local server)
1. Install ngrok from `https://ngrok.com/download` and sign in.
2. Start your app locally: `python app.py`.
3. In another terminal: `ngrok http 5000`.
4. Share the HTTPS forwarding URL printed by ngrok.

### Render.com (free tier friendly)
1. Push this repo to GitHub.
2. Create a new Web Service on Render and connect the repo.
3. Environment: Python 3.11 (or your version).
4. Build command:
   ```bash
   pip install -r requirements.txt
   ```
5. Start command:
   ```bash
   gunicorn app:app --bind 0.0.0.0:$PORT --workers 2
   ```
6. Add environment variable `PORT` (Render sets this automatically).
7. Deploy; Render provides a public URL.

### Heroku (alternative)
1. Create a `Procfile` with:
   ```
   web: gunicorn app:app --workers 2
   ```
2. `heroku create`
3. `git push heroku main`
4. `heroku open`

## License

This project is open source and available under the MIT License.

