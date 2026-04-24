(() => {
  function QuizCategorySection({
    category,
    selectedSubcategoryIds,
    questionCounts,
    isSubcategoryAvailable,
    onSelectSubcategory,
    onOpenInfo,
  }) {
    const runtime = window.QuizCategorySectionsRuntime || {};
    const RuntimeSubcategoryCard = runtime.SubcategoryCard;

    return (
      <section
        className="quiz-category-section"
        aria-labelledby={`section-${category.id}`}
      >
        <div className="quiz-category-section__title-wrap">
          <h2 id={`section-${category.id}`} className="quiz-category-section__title">
            {category.title}
          </h2>
        </div>

        <div className="quiz-category-section__grid">
          {RuntimeSubcategoryCard
            ? category.subcategories.map((subcategory) => (
                <RuntimeSubcategoryCard
                  key={subcategory.id}
                  category={category}
                  subcategory={subcategory}
                  isSelected={selectedSubcategoryIds.includes(subcategory.id)}
                  isAvailable={isSubcategoryAvailable ? isSubcategoryAvailable(subcategory) : true}
                  questionCount={questionCounts[subcategory.id] || 0}
                  onSelect={onSelectSubcategory}
                  onOpenInfo={onOpenInfo}
                />
              ))
            : null}
        </div>
      </section>
    );
  }

  window.QuizCategorySectionsRuntime = {
    ...(window.QuizCategorySectionsRuntime || {}),
    CategorySection: QuizCategorySection,
  };
})();
