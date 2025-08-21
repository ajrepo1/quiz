import io
from typing import Text

from PyPDF2 import PdfReader
from docx import Document


def _extract_pdf(file_like: io.BytesIO) -> Text:
	reader = PdfReader(file_like)
	pages_text = []
	for page in reader.pages:
		page_text = page.extract_text() or ""
		pages_text.append(page_text)
	return "\n".join(pages_text).strip()


def _extract_docx(file_like: io.BytesIO) -> Text:
	doc = Document(file_like)
	paragraphs = [p.text for p in doc.paragraphs if p.text]
	return "\n".join(paragraphs).strip()


def _extract_txt(file_like: io.BytesIO) -> Text:
	data = file_like.read()
	try:
		return data.decode("utf-8", errors="replace").strip()
	except Exception:
		return data.decode(errors="replace").strip()


def extract_text_from_upload(file_storage) -> Text:
	"""Extract text content from a Werkzeug FileStorage (PDF, DOCX, or TXT)."""
	filename = file_storage.filename or ""
	ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

	# Ensure we have a fresh BytesIO for libraries that read from start
	memory_file = io.BytesIO(file_storage.read())
	memory_file.seek(0)

	if ext == "pdf":
		return _extract_pdf(memory_file)
	elif ext == "docx":
		return _extract_docx(memory_file)
	elif ext == "txt":
		return _extract_txt(memory_file)
	else:
		raise ValueError(f"Unsupported extension: {ext}")
