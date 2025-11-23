/* File: components/app.js
Drop this at the end of

<body>:
	<script src="components/app.js"></script>
	Expects each question as:
	<article class="card" data-qid="..." data-correct="C" data-expl="...">
		<form> <input type="radio" name="..." value="A"> ... </form>
	</article>

	Outcome hooks (plain spans are enough; JS will create a minimal card if missing):
	<section id="outcome">
		<div class="result-card">
			<h3 data-role="status">PENDING</h3>
			<div class="stats">
				<div class="stat">
					<div class="val" data-role="accuracy">0%</div>
					<div>Accuracy</div>
				</div>
				<div class="stat">
					<div class="val" data-role="answered">0</div>
					<div>Answered</div>
				</div>
				<div class="stat">
					<div class="val" data-role="current">0</div>
					<div>Current Streak</div>
				</div>
				<div class="stat">
					<div class="val" data-role="best">0</div>
					<div>Best Streak</div>
				</div>
			</div>
		</div>
	</section>

	Explanation hook:
	<section id="explanation">
		<div class="explanation"></div>
	</section>
	*/

(() => {
	const $ = (sel, root = document) => root.querySelector(sel);
	const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

	// Ensure minimal outcome/explanation exist
	const outcome = $('#outcome') || document.body.appendChild(Object.assign(document.createElement('section'), {
		id: 'outcome'
	}));
	if (!$('[data-role="status"]', outcome)) {
		outcome.innerHTML = `
	<div class="result-card">
		<h3 data-role="status">PENDING</h3>
		<div class="stats">
			<div class="stat">
				<div class="val" data-role="accuracy">0%</div>
				<div>Accuracy</div>
			</div>
			<div class="stat">
				<div class="val" data-role="answered">0</div>
				<div>Answered</div>
			</div>
			<div class="stat">
				<div class="val" data-role="current">0</div>
				<div>Current Streak</div>
			</div>
			<div class="stat">
				<div class="val" data-role="best">0</div>
				<div>Best Streak</div>
			</div>
		</div>
	</div>`;
	}
	const explSection = $('#explanation') ||
		document.body.appendChild(Object.assign(document.createElement('section'), { id: 'explanation' }));
	if (!$('.explanation', explSection)) explSection.innerHTML = `<div class="explanation">
		<h3>Explanation</h3>
		<p>Select an answer to see feedback.</p>
	</div>`;

	// Outcome fields
	const fields = {
		status: $('[data-role="status"]', outcome),
		accuracy: $('[data-role="accuracy"]', outcome),
		answered: $('[data-role="answered"]', outcome),
		current: $('[data-role="current"]', outcome),
		best: $('[data-role="best"]', outcome),
		explBox: $('.explanation', explSection),
	};

	const state = {
		streak: 0,
		best: 0,
		answers: new Map(), // qid -> true/false
		chosen: new Map(), // qid -> letter
	};

	function setStatus(kind) {
		// kind: 'correct' | 'wrong' | 'pending'
		const word = kind === 'correct' ? 'CORRECT' : kind === 'wrong' ? 'INCORRECT' : 'PENDING';
		fields.status.textContent = word;
		const card = fields.status.closest('.result-card');
		card?.classList.remove('correct', 'wrong', 'pending');
		card?.classList.add(kind);
	}

	function renderStats() {
		const vals = [...state.answers.values()];
		const answered = vals.filter(v => v !== undefined).length;
		const correct = vals.filter(Boolean).length;
		const acc = answered ? Math.round((100 * correct) / answered) : 0;

		fields.accuracy.textContent = `${acc}%`;
		fields.answered.textContent = String(answered);
		fields.current.textContent = String(state.streak);
		fields.best.textContent = String(state.best);
	}

	function renderExplanation({ qid, isCorrect, correctLetter, chosenLetter, text }) {
		if (!fields.explBox) return;
		const head = isCorrect ? `<span class="correct">Correct</span>` : `<span class="wrong">Incorrect</span>`;
		const detail = text ? `<p>${text}</p>` : '';
		const chosen = chosenLetter ? `Your answer: <strong>${chosenLetter}</strong>. ` : '';
		fields.explBox.innerHTML = `
	<h3>Explanation</h3>
	<p>${head}. ${chosen}Correct answer: <strong>${correctLetter || '\u2014'}</strong>.</p>
	${detail}
	`;
	}

	function onPick(form, value) {
		const qel = form.closest('[data-qid]');
		if (!qel) return;
		const qid = qel.dataset.qid;
		const correctLetter = (qel.dataset.correct || '').trim();
		const expl = qel.dataset.expl || '';

		state.chosen.set(qid, value);
		const isCorrect = value === correctLetter;
		state.answers.set(qid, isCorrect);

		if (isCorrect) {
			state.streak += 1;
			if (state.streak > state.best) state.best = state.streak;
			setStatus('correct');
		} else {
			state.streak = 0;
			setStatus('wrong');
		}

		renderStats();
		renderExplanation({ qid, isCorrect, correctLetter, chosenLetter: value, text: expl });
	}

	// Wire radios
	$$('#questions article.card form').forEach(form => {
		form.addEventListener('change', (e) => {
			const t = e.target;
			if (!t || t.type !== 'radio') return;
			onPick(form, t.value);
		}, { passive: true });
	});

	// Initial paint
	setStatus('pending');
	renderStats();
})();
