import { CATEGORY_CONFIG } from "../../config/category-config.js";
import { getSubcategoriesByCategory } from "../../config/subcategory-config.js";
import { createPageHeader } from "../../components/page-header.js";
import { createPrimaryButton } from "../../components/primary-button.js";
import { createSelectionCard } from "../../components/selection-card.js";
import { getQuizSession, saveQuizSession } from "../../state/quiz-session.js";
import { qs } from "../../utils/dom.js";
import { validateSubcategorySelection } from "../../utils/validation.js";

const root = qs("#quiz-feature-root");
const session = getQuizSession();
const category = CATEGORY_CONFIG.find((item) => item.id === session.categoryId);
const subcategories = getSubcategoriesByCategory(session.categoryId);
let selectedSubcategoryId = session.subcategoryId;

if (!category) {
  window.location.href = "../category-selection/category-selection.html";
}

function renderPage() {
  root.innerHTML = "";

  const shell = document.createElement("section");
  shell.className = "quiz-shell";
  shell.append(
    createPageHeader({
      title: `فرعيات ${category.name}`,
      subtitle: "اختر الفرعية التي سيتم جلب الأسئلة منها عند بدء المباراة.",
      backHref: "../category-selection/category-selection.html",
    })
  );

  const grid = document.createElement("section");
  grid.className = "selection-grid";

  subcategories.forEach((subcategory) => {
    grid.append(
      createSelectionCard({
        title: subcategory.name,
        description: subcategory.description,
        icon: subcategory.flag || subcategory.icon,
        badge: subcategory.provider,
        selected: selectedSubcategoryId === subcategory.id,
        info: subcategory.info,
        onClick: () => {
          selectedSubcategoryId = subcategory.id;
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
      disabled: !validateSubcategorySelection(selectedSubcategoryId),
      onClick: () => {
        saveQuizSession({
          subcategoryId: selectedSubcategoryId,
          difficulty: null,
          amount: null,
          questions: [],
        });
        window.location.href = "../quiz-options/quiz-options.html";
      },
    })
  );

  shell.append(grid, footer);
  root.append(shell);
}

renderPage();

