const textInput = document.getElementById('textInput');
const uploadForm = document.getElementById('uploadForm');
const uploadStatus = document.getElementById('uploadStatus');
const numQuestionsInput = document.getElementById('numQuestions');
const modeSelect = document.getElementById('mode');
const generateBtn = document.getElementById('generateBtn');
const genStatus = document.getElementById('genStatus');
const quizContainer = document.getElementById('quizContainer');
const showAnswersBtn = document.getElementById('showAnswersBtn');

uploadForm.addEventListener('submit', async (e) => {
	e.preventDefault();
	const fileInput = document.getElementById('fileInput');
	if (!fileInput.files.length) {
		uploadStatus.textContent = 'Please select a file';
		return;
	}
	const formData = new FormData();
	formData.append('file', fileInput.files[0]);
	uploadStatus.textContent = 'Extracting...';
	try {
		const res = await fetch('/upload', { method: 'POST', body: formData });
		const data = await res.json();
		if (!res.ok) throw new Error(data.error || 'Upload failed');
		textInput.value = data.text || '';
		uploadStatus.textContent = 'Text extracted successfully.';
	} catch (err) {
		uploadStatus.textContent = 'Error: ' + err.message;
	}
});

function renderQuiz(questions) {
	quizContainer.innerHTML = '';
	questions.forEach((q, idx) => {
		const div = document.createElement('div');
		div.className = 'question';
		const title = document.createElement('h3');
		title.textContent = `Q${idx + 1} (${q.type?.toUpperCase?.() || 'MCQ'}). ${q.question}`;
		div.appendChild(title);
		q.options.forEach((opt, i) => {
			const label = document.createElement('label');
			label.className = 'option';
			const input = document.createElement('input');
			input.type = 'radio';
			input.name = 'q' + idx;
			input.value = i;
			label.appendChild(input);
			label.appendChild(document.createTextNode(' ' + opt));
			div.appendChild(label);
		});
		quizContainer.appendChild(div);
	});
}

generateBtn.addEventListener('click', async () => {
	const text = textInput.value.trim();
	const numQuestions = parseInt(numQuestionsInput.value || '5', 10);
	const mode = modeSelect.value;
	if (!text) {
		genStatus.textContent = 'Please paste text or extract from a file.';
		return;
	}
	genStatus.textContent = 'Generating quiz...';
	try {
		const res = await fetch('/generate-quiz', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ text, num_questions: numQuestions, mode })
		});
		const data = await res.json();
		if (!res.ok) throw new Error(data.error || 'Failed to generate quiz');
		const questions = (data.questions || []).slice(0, Math.min(numQuestions, 100));
		renderQuiz(questions);
		genStatus.textContent = `Generated ${questions.length} question(s).`;
	} catch (err) {
		genStatus.textContent = 'Error: ' + err.message;
	}
});

showAnswersBtn.addEventListener('click', () => {
	const questionDivs = Array.from(document.querySelectorAll('#quizContainer .question'));
	questionDivs.forEach((div, idx) => {
		const inputs = Array.from(div.querySelectorAll('input[type="radio"]'));
		if (!window.currentQuestions || !window.currentQuestions[idx]) return;
		inputs.forEach((input, i) => {
			const label = input.parentElement;
			label.classList.remove('correct', 'incorrect');
			if (i === window.currentQuestions[idx].answer_index) {
				label.classList.add('correct');
			}
		});
	});
});

// Keep a copy of current questions for showing answers
function setCurrentQuestions(questions) {
	window.currentQuestions = questions;
}

// Wrap renderQuiz to also set current questions
const originalRenderQuiz = renderQuiz;
renderQuiz = function(questions) {
	setCurrentQuestions(questions);
	originalRenderQuiz(questions);
}
