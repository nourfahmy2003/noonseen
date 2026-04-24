import styles from "./CategorySectionsPage.module.css";
import { SubcategoryCard } from "./SubcategoryCard";
import type { CategorySectionProps } from "./category-sections.types";

export function CategorySection({
  category,
  onSelectSubcategory,
  onOpenInfo,
}: CategorySectionProps): JSX.Element {
  return (
    <section className={styles.sectionCard} aria-labelledby={`section-${category.id}`}>
      <div className={styles.sectionTitleWrap}>
        <h2 id={`section-${category.id}`} className={styles.sectionTitlePill}>
          {category.title}
        </h2>
      </div>

      <div className={styles.cardsGrid}>
        {category.subcategories.map((subcategory) => (
          <SubcategoryCard
            key={subcategory.id}
            category={category}
            subcategory={subcategory}
            onSelect={onSelectSubcategory}
            onOpenInfo={onOpenInfo}
          />
        ))}
      </div>
    </section>
  );
}
