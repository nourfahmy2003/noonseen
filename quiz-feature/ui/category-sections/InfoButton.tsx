import styles from "./CategorySectionsPage.module.css";
import type { InfoButtonProps } from "./category-sections.types";

export function InfoButton({
  label = "معلومات",
  onClick,
}: InfoButtonProps): JSX.Element {
  return (
    <button
      type="button"
      className={styles.infoButton}
      aria-label={label}
      title={label}
      onClick={onClick}
    >
      i
    </button>
  );
}
