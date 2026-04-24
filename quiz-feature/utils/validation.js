export function validateCategorySelection(categoryId) {
  return Boolean(categoryId);
}

export function validateSubcategorySelection(subcategoryId) {
  return Boolean(subcategoryId);
}

export function validateQuizOptions(options) {
  return Boolean(options?.difficulty) && Number(options?.amount) > 0;
}

