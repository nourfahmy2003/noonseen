import { useMemo, useState } from "react";

import {
  categoryCatalog,
  type QuizCategorySection,
  type QuizSubcategoryCard,
} from "../../config/categoryCatalog";
import { apiSourceLookup } from "./category-sections.helpers";
import { CategorySection } from "./CategorySection";
import { InfoModal } from "./InfoModal";
import styles from "./CategorySectionsPage.module.css";
import type {
  CategorySectionsPageProps,
  InfoModalPayload,
} from "./category-sections.types";

export function CategorySectionsPage({
  title = "أحدد الفئات",
  subtitle = "اختر الفرع الذي تريد اللعب به من الأقسام المتاحة.",
  onSelectSubcategory,
}: CategorySectionsPageProps): JSX.Element {
  const [infoItem, setInfoItem] = useState<InfoModalPayload | null>(null);

  const sections = useMemo(() => categoryCatalog, []);

  const handleOpenInfo = (
    category: QuizCategorySection,
    subcategory: QuizSubcategoryCard
  ) => {
    setInfoItem({
      category,
      subcategory,
      source: apiSourceLookup.get(subcategory.apiSource),
    });
  };

  return (
    <div className={styles.page} dir="rtl">
      <header className={styles.pageHeader}>
        <div className={styles.heroPill}>{title}</div>
        <p className={styles.pageSubtitle}>{subtitle}</p>
      </header>

      <main className={styles.sectionsStack}>
        {sections.map((category) => (
          <CategorySection
            key={category.id}
            category={category}
            onSelectSubcategory={onSelectSubcategory}
            onOpenInfo={handleOpenInfo}
          />
        ))}
      </main>

      <InfoModal item={infoItem} onClose={() => setInfoItem(null)} />
    </div>
  );
}
