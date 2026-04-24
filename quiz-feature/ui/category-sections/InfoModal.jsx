(() => {
  function QuizInfoModal({ item, onClose }) {
    if (!item) {
      return null;
    }

    const { category, subcategory, source } = item;

    return (
      <div className="quiz-info-modal__backdrop" role="presentation" onClick={onClose}>
        <div
          className="quiz-info-modal__card"
          role="dialog"
          aria-modal="true"
          aria-labelledby={`modal-${subcategory.id}`}
          onClick={(event) => event.stopPropagation()}
        >
          <div className="quiz-info-modal__header">
            <div>
              <span className="quiz-info-modal__badge">{category.title}</span>
              <h3 id={`modal-${subcategory.id}`} className="quiz-info-modal__title">
                {subcategory.infoTitle || subcategory.title}
              </h3>
            </div>

            <button
              type="button"
              className="quiz-info-modal__close"
              onClick={onClose}
              aria-label="إغلاق"
            >
              ×
            </button>
          </div>

          <p className="quiz-info-modal__body">
            {subcategory.infoBody || subcategory.description}
          </p>

          {source ? (
            <div className="quiz-info-modal__source">
              <span className="quiz-info-modal__source-label">مصدر البيانات</span>
              <strong className="quiz-info-modal__source-name">{source.label}</strong>
              <p className="quiz-info-modal__source-text">{source.recommendedUsage}</p>
            </div>
          ) : null}
        </div>
      </div>
    );
  }

  window.QuizCategorySectionsRuntime = {
    ...(window.QuizCategorySectionsRuntime || {}),
    InfoModal: QuizInfoModal,
  };
})();
