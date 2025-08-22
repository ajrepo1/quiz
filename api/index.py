import sys
from pathlib import Path

# Ensure project root is importable when running in Vercel serverless
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import app as flask_app  # noqa: E402

# Point Flask to the correct static and templates directories in serverless env
flask_app.static_folder = str(ROOT / "static")
flask_app.static_url_path = "/static"
flask_app.template_folder = str(ROOT / "templates")

# Vercel expects a module-level WSGI entry named "app"
app = flask_app

# Ensure debug mode is disabled for production
flask_app.debug = False



