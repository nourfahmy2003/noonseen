(() => {
  function QuizCardVisual({ title, imageKey, iconKey }) {
    const runtime = window.QuizCategorySectionsRuntime || {};
    const getPlaceholderIcon =
      runtime.getPlaceholderIcon || (() => "✨");
    const getVisualAccent =
      runtime.getVisualAccent || (() => "#A6D0F5");

    const icon = getPlaceholderIcon(imageKey, iconKey);
    const accent = getVisualAccent(`${imageKey || ""}-${iconKey || ""}-${title}`);

    return (
      <div className="quiz-subcategory-card__visual">
        <span
          className="quiz-subcategory-card__visual-glow"
          aria-hidden="true"
          style={{ backgroundColor: accent }}
        />
        <span className="quiz-subcategory-card__visual-ring" aria-hidden="true" />
        <span className="quiz-subcategory-card__visual-icon" aria-hidden="true">
          {icon}
        </span>
      </div>
    );
  }

  window.QuizCategorySectionsRuntime = {
    ...(window.QuizCategorySectionsRuntime || {}),
    CardVisual: QuizCardVisual,
  };
})();
