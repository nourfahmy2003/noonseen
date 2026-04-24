import type { MouseEventHandler } from "react";
import type {
  QuizCategorySection,
  QuizSubcategoryCard,
} from "../../config/categoryCatalog";
import type { ApiSourceDefinition } from "../../config/sourceMap";

export type CategorySectionsPageProps = {
  title?: string;
  subtitle?: string;
  onSelectSubcategory: (
    category: QuizCategorySection,
    subcategory: QuizSubcategoryCard
  ) => void;
};

export type CategorySectionProps = {
  category: QuizCategorySection;
  onSelectSubcategory: (
    category: QuizCategorySection,
    subcategory: QuizSubcategoryCard
  ) => void;
  onOpenInfo: (
    category: QuizCategorySection,
    subcategory: QuizSubcategoryCard
  ) => void;
};

export type SubcategoryCardProps = {
  category: QuizCategorySection;
  subcategory: QuizSubcategoryCard;
  onSelect: (
    category: QuizCategorySection,
    subcategory: QuizSubcategoryCard
  ) => void;
  onOpenInfo: (
    category: QuizCategorySection,
    subcategory: QuizSubcategoryCard
  ) => void;
};

export type InfoButtonProps = {
  label?: string;
  onClick: MouseEventHandler<HTMLButtonElement>;
};

export type InfoModalPayload = {
  category: QuizCategorySection;
  subcategory: QuizSubcategoryCard;
  source?: ApiSourceDefinition;
};

export type InfoModalProps = {
  item: InfoModalPayload | null;
  onClose: () => void;
};

export type FlagBadgeProps = {
  flagCode: string;
};

export type CardVisualProps = {
  title: string;
  imageKey?: string;
  iconKey?: string;
};
