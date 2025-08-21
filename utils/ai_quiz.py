import json
import os
from typing import Dict, List

try:
	from openai import OpenAI
except Exception:  # pragma: no cover
	OpenAI = None  # type: ignore

try:
	import google.generativeai as genai
except Exception:
	genai = None  # type: ignore


def _build_prompt(text: str, num_questions: int, mode: str) -> str:
	mode = (mode or "mcq").lower()
	return (
		"You are a helpful assistant that creates high-quality quiz questions from study text.\n"
		"Return ONLY a valid JSON array, no prose, no markdown fences.\n"
		"Each item must be: {\n"
		"  'question': string (<= 30 words),\n"
		"  'options': array of strings,\n"
		"  'answer_index': integer index of the correct option,\n"
		"  'type': 'mcq' or 'true_false'\n"
		"}.\n"
		"Constraints:\n"
		f"- Total questions: {num_questions}.\n"
		"- Prefer conceptually meaningful, unambiguous questions.\n"
		"- No duplicate or near-duplicate questions.\n"
		"- Avoid trivial blanks; test comprehension.\n"
		"- Keep questions concise (<= 30 words).\n"
		+ (
			"- For MCQ, provide exactly 4 plausible options, one correct. Set type='mcq'.\n"
			if mode in ("mcq", "mixed")
			else ""
		)
		+ (
			"- For True/False, options must be [\"True\", \"False\"]. Set type='true_false'.\n"
			if mode in ("tf", "mixed")
			else ""
		)
		+ (
			"- If mixed, include a balanced mix of MCQ and True/False.\n"
			if mode == "mixed"
			else ""
		)
		+ "\nText to use:\n" + text
	)


def _coerce_questions(raw: str) -> List[Dict]:
	# Try to parse raw JSON or extract from fences
	try:
		return json.loads(raw)
	except Exception:
		pass
	# Try extracting the largest JSON array
	start = raw.find("[")
	end = raw.rfind("]")
	if start != -1 and end != -1 and end > start:
		candidate = raw[start : end + 1]
		try:
			return json.loads(candidate)
		except Exception:
			pass
	return []


def generate_quiz_ai(text: str, num_questions: int, mode: str = "mcq", model: str | None = None) -> List[Dict]:
	provider = (os.environ.get("AI_PROVIDER") or "").strip().lower()
	use_google = provider == "google" or bool(os.environ.get("GOOGLE_API_KEY"))

	prompt = _build_prompt(text, num_questions, mode)

	if use_google:
		if not genai:
			raise RuntimeError("Google Generative AI SDK not available. Install 'google-generativeai'.")
		google_key = (os.environ.get("AI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or "").strip()
		if not google_key:
			raise RuntimeError("GOOGLE_API_KEY/AI_API_KEY is not set.")
		genai.configure(api_key=google_key)
		google_model = (model or os.environ.get("AI_MODEL") or "gemini-1.5-flash").strip()
		response = genai.GenerativeModel(google_model).generate_content(prompt)
		content = getattr(response, "text", "") or ""
		items = _coerce_questions(content)
	else:
		if not OpenAI:
			raise RuntimeError("OpenAI SDK not available. Install 'openai'.")
		# Flexible OpenAI-compatible config
		api_key = (
			os.environ.get("AI_API_KEY")
			or os.environ.get("OPENAI_API_KEY")
			or ""
		).strip()
		if not api_key:
			raise RuntimeError("AI_API_KEY/OPENAI_API_KEY is not set.")
		base_url = os.environ.get("AI_BASE_URL", "").strip() or None
		openai_model = (model or os.environ.get("AI_MODEL") or "gpt-4o-mini").strip()
		default_headers = None
		if base_url and "openrouter.ai" in base_url:
			default_headers = {
				"HTTP-Referer": os.environ.get("AI_SITE_URL", "http://localhost:5000"),
				"X-Title": os.environ.get("AI_APP_NAME", "Quiz Generator"),
			}
		client = OpenAI(api_key=api_key, base_url=base_url, default_headers=default_headers)
		resp = client.chat.completions.create(
			model=openai_model,
			messages=[
				{"role": "system", "content": "You produce strict JSON outputs."},
				{"role": "user", "content": prompt},
			],
			temperature=0.5,
			max_tokens=2000,
		)
		content = resp.choices[0].message.content or ""
		items = _coerce_questions(content)

	# Use Chat Completions for broad compatibility
	resp = client.chat.completions.create(
		model=model,
		messages=[
			{"role": "system", "content": "You produce strict JSON outputs."},
			{"role": "user", "content": prompt},
		],
		temperature=0.5,
		max_tokens=2000,
	)
	content = resp.choices[0].message.content or ""
	items = _coerce_questions(content)

	# Normalize and validate
	normalized: List[Dict] = []
	for q in items:
		question = str(q.get("question", "")).strip()
		options = list(map(str, q.get("options", [])))
		answer_index = int(q.get("answer_index", -1))
		qtype = str(q.get("type", "mcq")).strip().lower() or "mcq"
		if not question or not options or answer_index < 0 or answer_index >= len(options):
			continue
		# Enforce shapes
		if qtype == "true_false":
			options = ["True", "False"]
			answer_index = 0 if answer_index == 0 else 1
		elif qtype == "mcq":
			# Trim/pad to 4 options if possible
			options = options[:4] if len(options) >= 4 else options
		if not options:
			continue
		normalized.append({
			"question": question,
			"options": options,
			"answer_index": answer_index,
			"type": qtype,
		})

	return normalized[:num_questions]


