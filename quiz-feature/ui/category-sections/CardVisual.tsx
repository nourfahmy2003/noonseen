import styles from "./CategorySectionsPage.module.css";
import {
  getPlaceholderIcon,
  getVisualAccent,
} from "./category-sections.helpers";
import type { CardVisualProps } from "./category-sections.types";

export function CardVisual({
  title,
  imageKey,
  iconKey,
}: CardVisualProps): JSX.Element {
  const icon = getPlaceholderIcon(imageKey, iconKey);
  const accent = getVisualAccent(`${imageKey ?? ""}-${iconKey ?? ""}-${title}`);

  return (
    <div className={styles.cardVisual}>
      <span
        className={styles.cardVisualGlow}
        aria-hidden="true"
        style={{ backgroundColor: accent }}
      />
      <span className={styles.cardVisualRing} aria-hidden="true" />
      <span className={styles.cardVisualIcon} aria-hidden="true">
        {icon}
      </span>
      <span className={styles.cardVisualHint} aria-hidden="true">
        {title}
      </span>
    </div>
  );
}
