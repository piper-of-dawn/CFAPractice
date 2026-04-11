(function () {
  function isTypingTarget(el) {
    if (!el) return false;
    const tag = String(el.tagName || '').toLowerCase();
    if (tag === 'input') {
      const type = String(el.type || '').toLowerCase();
      return type !== 'radio' && type !== 'checkbox';
    }
    return tag === 'textarea' || tag === 'select' || el.isContentEditable;
  }

  function isModalOpen() {
    return !!document.querySelector('.katas-modal.show');
  }

  function visibleTop(el) {
    const rect = el.getBoundingClientRect();
    return Math.abs(rect.top - 88);
  }

  function dispatchSelectionEvents(input) {
    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.dispatchEvent(new Event('change', { bubbles: true }));
  }

  function optionNumberFromKey(event) {
    const code = String(event.code || '');
    if (code === 'KeyA' || code === 'KeyQ') return 1;
    if (code === 'KeyW') return 2;
    if (code === 'KeyC' || code === 'KeyE') return 3;
    return null;
  }

  function initQuestionKeyboardNav(options) {
    const settings = Object.assign({
      questionSelector: 'section.question',
      selectedClass: 'is-selected',
      scrollBlock: 'center'
    }, options || {});

    const questions = Array.from(document.querySelectorAll(settings.questionSelector));
    if (!questions.length) return null;

    let selectedIndex = 0;

    function setSelectedQuestion(index, shouldScroll) {
      selectedIndex = Math.max(0, Math.min(questions.length - 1, index));
      questions.forEach((question, i) => {
        const selected = i === selectedIndex;
        question.classList.toggle(settings.selectedClass, selected);
        question.setAttribute('data-is-selected', selected ? 'true' : 'false');
        if (selected) {
          question.setAttribute('tabindex', '-1');
          question.style.animation = 'none';
          void question.offsetWidth;
          question.style.animation = '';
        }
      });
      if (shouldScroll) {
        questions[selectedIndex].scrollIntoView({
          behavior: 'smooth',
          block: settings.scrollBlock
        });
      }
    }

    function syncSelectedFromViewport() {
      const best = questions
        .map((question, index) => ({ index, distance: visibleTop(question) }))
        .sort((a, b) => a.distance - b.distance)[0];
      if (best) setSelectedQuestion(best.index, false);
    }

    function selectOption(number) {
      const question = questions[selectedIndex];
      if (!question) return;
      if (question.dataset.answerLocked === 'true') return;
      const options = Array.from(question.querySelectorAll('input[type="radio"]'));
      const target = options[number - 1];
      if (!target || target.disabled) return;
      if (typeof target.click === 'function') {
        target.click();
        target.focus({ preventScroll: true });
        return;
      }
      target.checked = true;
      dispatchSelectionEvents(target);
      target.focus({ preventScroll: true });
    }

    questions.forEach((question, index) => {
      question.addEventListener('click', () => setSelectedQuestion(index, false));
      question.addEventListener('focusin', () => setSelectedQuestion(index, false));
    });

    function handleKeydown(event) {
      const typingTarget = isTypingTarget(event.target);
      const modalOpen = isModalOpen();

      if (event.defaultPrevented || typingTarget || modalOpen) return;

      if (event.key === 'ArrowDown' || event.key === 'ArrowRight') {
        event.preventDefault();
        event.stopPropagation();
        setSelectedQuestion(selectedIndex + 1, true);
        return;
      }

      if (event.key === 'ArrowUp' || event.key === 'ArrowLeft') {
        event.preventDefault();
        event.stopPropagation();
        setSelectedQuestion(selectedIndex - 1, true);
        return;
      }

      const optionNumber = optionNumberFromKey(event);
      if (optionNumber) {
        event.preventDefault();
        event.stopPropagation();
        selectOption(optionNumber);
      }
    }

    window.addEventListener('keydown', handleKeydown, { capture: true });

    let scrollTimer = null;
    window.addEventListener('scroll', () => {
      window.clearTimeout(scrollTimer);
      scrollTimer = window.setTimeout(syncSelectedFromViewport, 120);
    }, { passive: true });

    setSelectedQuestion(0, false);
    return { setSelectedQuestion, syncSelectedFromViewport };
  }

  window.initQuestionKeyboardNav = initQuestionKeyboardNav;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => initQuestionKeyboardNav());
  } else {
    initQuestionKeyboardNav();
  }
})();
