(() => {
  function handleCardKeyDown(event, onActivate) {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      onActivate();
    }
  }

  function QuizSubcategoryCard({
    category,
    subcategory,
    isSelected,
    isAvailable,
    questionCount,
    onSelect,
    onOpenInfo,
  }) {
    const runtime = window.QuizCategorySectionsRuntime || {};
    const RuntimeCardVisual = runtime.CardVisual;
    const RuntimeFlagBadge = runtime.FlagBadge;
    const RuntimeInfoButton = runtime.InfoButton;

    return (
      <div
        role="button"
        tabIndex={isAvailable ? 0 : -1}
        aria-disabled={!isAvailable}
        className={`quiz-subcategory-card ${isSelected ? "quiz-subcategory-card--selected" : ""} ${!isAvailable ? "quiz-subcategory-card--disabled" : ""}`}
        onClick={() => {
          if (isAvailable) {
            onSelect(category, subcategory);
          }
        }}
        onKeyDown={(event) =>
          handleCardKeyDown(event, () => {
            if (isAvailable) {
              onSelect(category, subcategory);
            }
          })
        }
      >
        {RuntimeInfoButton ? (
          <RuntimeInfoButton
            onClick={(event) => {
              event.stopPropagation();
              onOpenInfo(category, subcategory);
            }}
          />
        ) : null}

        {RuntimeCardVisual ? (
          <RuntimeCardVisual
            title={subcategory.title}
            imageKey={subcategory.imageKey}
            iconKey={subcategory.iconKey}
          />
        ) : null}

        {subcategory.flagCode && RuntimeFlagBadge ? (
          <RuntimeFlagBadge flagCode={subcategory.flagCode} />
        ) : null}

        {!isAvailable ? (
          <span className="quiz-subcategory-card__status">تحت الإنشاء</span>
        ) : null}

        <div className="quiz-subcategory-card__footer">
          <span className="quiz-subcategory-card__title">{subcategory.title}</span>
            <span className="quiz-subcategory-card__meta">
              {!isAvailable
              ? "تحت الإنشاء"
              : category?.id === "no-word"
              ? "٢ سهل • ٢ متوسط • ٢ صعب • QR"
              : "٢ سهل • ٢ متوسط • ٢ صعب"}
            </span>
        </div>
      </div>
    );
  }

  window.QuizCategorySectionsRuntime = {
    ...(window.QuizCategorySectionsRuntime || {}),
    SubcategoryCard: QuizSubcategoryCard,
  };
})();
