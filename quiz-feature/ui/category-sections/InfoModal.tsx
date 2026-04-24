import styles from "./CategorySectionsPage.module.css";
import type { InfoModalProps } from "./category-sections.types";

export function InfoModal({
  item,
  onClose,
}: InfoModalProps): JSX.Element | null {
  if (!item) {
    return null;
  }

  const { category, subcategory, source } = item;

  return (
    <div
      className={styles.modalBackdrop}
      role="presentation"
      onClick={onClose}
    >
      <div
        className={styles.modalCard}
        role="dialog"
        aria-modal="true"
        aria-labelledby={`info-title-${subcategory.id}`}
        onClick={(event) => event.stopPropagation()}
      >
        <div className={styles.modalHeader}>
          <div>
            <span className={styles.modalSectionBadge}>{category.title}</span>
            <h3 id={`info-title-${subcategory.id}`} className={styles.modalTitle}>
              {subcategory.infoTitle || subcategory.title}
            </h3>
          </div>

          <button
            type="button"
            className={styles.modalCloseButton}
            onClick={onClose}
            aria-label="إغلاق"
          >
            ×
          </button>
        </div>

        <p className={styles.modalBody}>
          {subcategory.infoBody || subcategory.description}
        </p>

        {source ? (
          <div className={styles.modalSourceBlock}>
            <span className={styles.modalSourceLabel}>مصدر البيانات</span>
            <strong className={styles.modalSourceName}>{source.label}</strong>
            <p className={styles.modalSourceText}>{source.recommendedUsage}</p>
          </div>
        ) : null}
      </div>
    </div>
  );
}
