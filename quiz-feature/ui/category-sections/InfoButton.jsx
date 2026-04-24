(() => {
  function QuizInfoButton({ label = "معلومات", onClick }) {
    return (
      <button
        type="button"
        className="quiz-subcategory-card__info"
        aria-label={label}
        title={label}
        onClick={onClick}
      >
        i
      </button>
    );
  }

  window.QuizCategorySectionsRuntime = {
    ...(window.QuizCategorySectionsRuntime || {}),
    InfoButton: QuizInfoButton,
  };
})();
