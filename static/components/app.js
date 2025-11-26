(() => {
  // Safe query helpers: tolerate null roots
  const $ = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => [...(r || document).querySelectorAll(s)];

  // Outcome/dashboard references
  const outcomeCard = $("#outcomeCard");
  const fields = {
    status: $('[data-role="status"]', outcomeCard),
    accuracy: $('[data-role="accuracy"]', outcomeCard),
    answered: $('[data-role="answered"]', outcomeCard),
    current: $('[data-role="current"]', outcomeCard),
    best: $('[data-role="best"]', outcomeCard),
    pbar: $("#progressBar") || null,
  };

  // Explanation box
  const explBox =
    $("#explanation .explanation") ||
    (() => {
      const host =
        $("#explanation") ||
        document.body.appendChild(
          Object.assign(document.createElement("section"), { id: "explanation" })
        );
      host.innerHTML =
        '<div class="explanation"><h3>Explanation</h3><p>Select an answer and press Check.</p></div>';
      return $(".explanation", host);
    })();

  // State
  const state = {
    answered: new Set(),
    correctMap: new Map(),
    streak: 0,
    best: 0,
  };

  function setStatus(kind) {
    const word =
      kind === "correct"
        ? "CORRECT"
        : kind === "wrong"
          ? "INCORRECT"
          : "PENDING";
    if (outcomeCard) {
      outcomeCard.classList.remove("correct", "wrong", "pending");
      outcomeCard.classList.add(kind);
    }
    if (fields.status) fields.status.textContent = word;
  }

  function renderStats() {
    const vals = [...state.correctMap.values()];
    const answered = vals.length;
    const correct = vals.filter(Boolean).length;
    const acc = answered ? Math.round((100 * correct) / answered) : 0;

    if (fields.accuracy) fields.accuracy.textContent = `${acc}%`;
    if (fields.answered) fields.answered.textContent = String(answered);
    if (fields.current) fields.current.textContent = String(state.streak);
    if (fields.best) fields.best.textContent = String(state.best);
    if (fields.pbar) fields.pbar.style.width = `${acc}%`;
  }

  function showExplanation(isCorrect, correctLetter, chosenLetter, text) {
    const head = isCorrect
      ? `<span class="correct">Correct.</span>`
      : `<span class="wrong">Incorrect.</span> Correct answer: <strong>${correctLetter}</strong>.`;
    const extra = text ? `<p>${text}</p>` : "";
    const html = `<h3>Explanation</h3><p>${head}</p>${extra}`;
    explBox.innerHTML = html;
    if (
      !isCorrect &&
      window.matchMedia("(max-width: 980px)").matches &&
      explBox.scrollIntoView
    ) {
      explBox.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }

  function clearMarkings(form) {
    $$(".option", form).forEach((el) =>
      el.classList.remove("correct", "wrong", "dim")
    );
  }

  function mark(form, correctLetter, chosenLetter, isCorrect) {
    clearMarkings(form);
    const opts = $$(".option", form);
    for (const opt of opts) {
      const radio = $("input[type='radio']", opt);
      const letter = radio?.value;
      if (letter === correctLetter) opt.classList.add("correct");
      if (!isCorrect && letter === chosenLetter) opt.classList.add("wrong");
      if (
        !isCorrect &&
        letter !== correctLetter &&
        letter !== chosenLetter
      )
        opt.classList.add("dim");
    }
  }

  function checkOne(card) {
    const qid = card.dataset.qid;
    const correctLetter = (card.dataset.correct || "").trim();
    const expl = card.dataset.expl || "";
    const form = $("form.q", card);
    const chosen = $("input[type='radio']:checked", form)?.value;

    if (!chosen) {
      setStatus("pending");
      showExplanation(false, correctLetter, "", "Select an option first.");
      return;
    }

    const isCorrect = chosen === correctLetter;
    state.correctMap.set(qid, isCorrect);

    // Update per-card visual state
    card.classList.remove("is-correct", "is-wrong");

    if (isCorrect) {
      state.streak += 1;
      if (state.streak > state.best) state.best = state.streak;
      setStatus("correct");
      card.classList.add("is-correct");
    } else {
      state.streak = 0;
      setStatus("wrong");
      card.classList.add("is-wrong");
    }
    state.answered.add(qid);

    mark(form, correctLetter, chosen, isCorrect);
    showExplanation(isCorrect, correctLetter, chosen, isCorrect ? "" : expl);
    renderStats();
  }

  // Remove check buttons (UX: auto-check on select)
  $$(".card .btn-check").forEach((btn) => btn.remove());

  // Auto-check when a radio option is selected
  $$("form.q").forEach((form) => {
    form.addEventListener("change", (e) => {
      const target = e.target;
      if (target && target.matches("input[type='radio']")) {
        const card = form.closest(".card");
        if (card) checkOne(card);
      }
    });
  });

  // Init
  setStatus("pending");
  renderStats();
})();
