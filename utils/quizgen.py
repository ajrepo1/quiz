import random
import re
from collections import Counter
from typing import Dict, List

BASIC_STOPWORDS = {
	"the","and","for","are","but","not","you","with","that","this","have","from","they",
	"was","were","will","would","there","their","what","when","where","which","your","about",
	"can","could","should","into","than","then","them","these","those","over","also","such",
	"has","had","did","does","doing","been","being","its","it's","our","out","any","all",
	"him","her","his","she","himself","herself","ours","yours","mine","theirs","who","whom",
	"to","of","in","on","at","by","as","is","it","a","an","or","if","so","we","i"
}


_word_pattern = re.compile(r"[A-Za-z][A-Za-z\-']+")
_sentence_split = re.compile(r"(?<=[.!?])\s+")


def _tokenize_words(text: str) -> List[str]:
	return [w.lower() for w in _word_pattern.findall(text)]


def _split_sentences(text: str) -> List[str]:
	sentences = _sentence_split.split(text)
	# Normalize spacing
	return [re.sub(r"\s+", " ", s).strip() for s in sentences if s.strip()]


def _choose_keyword(sentence: str, global_freq: Dict[str, int]) -> str:
	words = _tokenize_words(sentence)
	candidates = [w for w in words if len(w) > 3 and w not in BASIC_STOPWORDS and w in global_freq]
	if not candidates:
		return ""
	# Choose the most frequent meaningful word across the whole text that is present in the sentence
	candidates.sort(key=lambda w: (global_freq.get(w, 0), len(w)), reverse=True)
	return candidates[0]


def _make_distractors(correct: str, global_freq: Dict[str, int], k: int) -> List[str]:
	# Choose high-frequency words as distractors that are different from the correct answer
	common = [w for w, _ in Counter(global_freq).most_common(100)
			  if w != correct and len(w) > 3 and w not in BASIC_STOPWORDS]
	random.shuffle(common)
	return common[:k]


def _blank_word_in_sentence(sentence: str, word: str) -> str:
	if not word:
		return sentence
	pattern = re.compile(rf"\b{re.escape(word)}\b", re.IGNORECASE)
	return pattern.sub("_____", sentence, count=1)


def _generate_mcq(sentences: List[str], freq: Dict[str, int], num_questions: int) -> List[Dict]:
	questions = []
	for sentence in sentences:
		keyword = _choose_keyword(sentence, freq)
		if not keyword:
			continue
		question_text = _blank_word_in_sentence(sentence, keyword)
		if question_text == sentence:
			continue
		options = [keyword]
		options.extend(_make_distractors(keyword, freq, 3))
		options = list(dict.fromkeys(options))
		if len(options) < 4:
			continue
		options = options[:4]
		random.shuffle(options)
		answer_index = options.index(keyword)
		questions.append({
			"question": question_text,
			"options": options,
			"answer_index": answer_index,
			"type": "mcq"
		})
		if len(questions) >= num_questions:
			break
	return questions


def _generate_true_false(sentences: List[str], freq: Dict[str, int], num_questions: int) -> List[Dict]:
	questions = []
	for sentence in sentences:
		keyword = _choose_keyword(sentence, freq)
		if not keyword:
			continue
		make_false = random.random() < 0.5
		if make_false:
			distractors = _make_distractors(keyword, freq, 1)
			if not distractors:
				continue
			false_word = distractors[0]
			pattern = re.compile(rf"\b{re.escape(keyword)}\b", re.IGNORECASE)
			mutated = pattern.sub(false_word, sentence, count=1)
			stmt = mutated
			answer_index = 1  # False
		else:
			stmt = sentence
			answer_index = 0  # True
		questions.append({
			"question": stmt,
			"options": ["True", "False"],
			"answer_index": answer_index,
			"type": "true_false"
		})
		if len(questions) >= num_questions:
			break
	return questions


def generate_quiz(text: str, num_questions: int = 5, mode: str = "mcq") -> List[Dict]:
	"""
	Generate quiz questions from raw text.
	mode: "mcq" | "tf" | "mixed"
	Returns a list of {question, options, answer_index, type} dicts.
	"""
	clean_text = re.sub(r"\s+", " ", (text or "").strip())
	if not clean_text:
		return []

	# Build global frequency map
	words = [w for w in _tokenize_words(clean_text) if len(w) > 3 and w not in BASIC_STOPWORDS]
	freq = Counter(words)

	sentences = _split_sentences(clean_text)
	# Filter sentences to be at most 30 words
	sentences = [s for s in sentences if len(_tokenize_words(s)) <= 30]
	# Prefer mid-length sentences that likely form a complete idea
	sentences.sort(key=lambda s: (-len(_tokenize_words(s)), s))

	mode = (mode or "mcq").lower()
	if mode == "mcq":
		return _generate_mcq(sentences, freq, num_questions)
	elif mode == "tf":
		return _generate_true_false(sentences, freq, num_questions)
	elif mode == "mixed":
		mcq_count = num_questions // 2
		tf_count = num_questions - mcq_count
		mcqs = _generate_mcq(sentences, freq, mcq_count)
		tfs = _generate_true_false(sentences, freq, tf_count)
		combined = mcqs + tfs
		random.shuffle(combined)
		return combined
	else:
		# Fallback to mcq
		return _generate_mcq(sentences, freq, num_questions)
