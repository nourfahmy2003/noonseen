import styles from "./CategorySectionsPage.module.css";
import { flagCodeToEmoji } from "./category-sections.helpers";
import type { FlagBadgeProps } from "./category-sections.types";

export function FlagBadge({ flagCode }: FlagBadgeProps): JSX.Element {
  return (
    <span className={styles.flagBadge} aria-label={`العلم ${flagCode}`}>
      {flagCodeToEmoji(flagCode)}
    </span>
  );
}
