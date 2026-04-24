(() => {
  function QuizFlagBadge({ flagCode }) {
    const runtime = window.QuizCategorySectionsRuntime || {};
    const flagCodeToEmoji =
      runtime.flagCodeToEmoji || (() => "🏳️");

    return (
      <span className="quiz-subcategory-card__flag" aria-label={`العلم ${flagCode}`}>
        {flagCodeToEmoji(flagCode)}
      </span>
    );
  }

  window.QuizCategorySectionsRuntime = {
    ...(window.QuizCategorySectionsRuntime || {}),
    FlagBadge: QuizFlagBadge,
  };
})();
