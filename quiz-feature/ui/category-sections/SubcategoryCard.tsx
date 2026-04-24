import styles from "./CategorySectionsPage.module.css";
import { CardVisual } from "./CardVisual";
import { FlagBadge } from "./FlagBadge";
import { InfoButton } from "./InfoButton";
import type { SubcategoryCardProps } from "./category-sections.types";

export function SubcategoryCard({
  category,
  subcategory,
  onSelect,
  onOpenInfo,
}: SubcategoryCardProps): JSX.Element {
  return (
    <button
      type="button"
      className={styles.subcategoryCard}
      onClick={() => onSelect(category, subcategory)}
    >
      <InfoButton
        onClick={(event) => {
          event.stopPropagation();
          onOpenInfo(category, subcategory);
        }}
      />

      <CardVisual
        title={subcategory.title}
        imageKey={subcategory.imageKey}
        iconKey={subcategory.iconKey}
      />

      {subcategory.flagCode ? <FlagBadge flagCode={subcategory.flagCode} /> : null}

      <div className={styles.subcategoryFooter}>
        <span className={styles.subcategoryTitle}>{subcategory.title}</span>
      </div>
    </button>
  );
}
