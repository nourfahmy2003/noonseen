import { CATEGORY_CONFIG } from "../../config/category-config.js";
import { createPageHeader } from "../../components/page-header.js";
import { createPrimaryButton } from "../../components/primary-button.js";
import { createSelectionCard } from "../../components/selection-card.js";
import { saveQuizSession } from "../../state/quiz-session.js";
import { qs } from "../../utils/dom.js";
import { validateCategorySelection } from "../../utils/validation.js";

const root = qs("#quiz-feature-root");
let selectedCategoryId = null;

function renderPage() {
  root.innerHTML = "";

  const shell = document.createElement("section");
  shell.className = "quiz-shell";

  shell.append(
    createPageHeader({
      title: "اختيار الفئة",
      subtitle: "اختر الفئة الرئيسية أولًا قبل الانتقال إلى الفرعيات.",
    })
  );

  const grid = document.createElement("section");
  grid.className = "selection-grid";

  CATEGORY_CONFIG.forEach((category) => {
    grid.append(
      createSelectionCard({
        title: category.name,
        description: category.description,
        icon: category.icon,
        selected: selectedCategoryId === category.id,
        info: category.description,
        onClick: () => {
          selectedCategoryId = category.id;
          renderPage();
        },
        onInfoClick: (infoText, title) => window.alert(`${title}\n\n${infoText}`),
      })
    );
  });

  const footer = document.createElement("div");
  footer.className = "quiz-page-actions";
  footer.append(
    createPrimaryButton({
      label: "التالي",
      disabled: !validateCategorySelection(selectedCategoryId),
      onClick: () => {
        saveQuizSession({
          categoryId: selectedCategoryId,
          subcategoryId: null,
          difficulty: null,
          amount: null,
          questions: [],
        });
        window.location.href = "../subcategory-selection/subcategory-selection.html";
      },
    })
  );

  shell.append(grid, footer);
  root.append(shell);
}

renderPage();

