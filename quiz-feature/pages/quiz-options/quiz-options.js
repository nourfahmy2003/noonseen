import { createOptionChip } from "../../components/option-chip.js";
import { createPageHeader } from "../../components/page-header.js";
import { createPrimaryButton } from "../../components/primary-button.js";
import { clearQuizQuestions, getQuizSession, saveQuizSession } from "../../state/quiz-session.js";
import { qs } from "../../utils/dom.js";
import { validateQuizOptions } from "../../utils/validation.js";

const root = qs("#quiz-feature-root");
const session = getQuizSession();
const difficultyOptions = [
  { id: "easy", label: "سهل • 200" },
  { id: "medium", label: "متوسط • 400" },
  { id: "hard", label: "صعب • 600" },
];
const amountOptions = [5, 10, 15, 20];

let selectedDifficulty = session.difficulty;
let selectedAmount = session.amount;

if (!session.categoryId || !session.subcategoryId) {
  window.location.href = "../category-selection/category-selection.html";
}

function renderSectionTitle(text) {
  const title = document.createElement("h2");
  title.className = "quiz-section-title";
  title.textContent = text;
  return title;
}

function renderPage() {
  root.innerHTML = "";

  const shell = document.createElement("section");
  shell.className = "quiz-shell";
  shell.append(
    createPageHeader({
      title: "خيارات المباراة",
      subtitle: "لن يتم جلب الأسئلة إلا بعد الضغط على ابدأ.",
      backHref: "../subcategory-selection/subcategory-selection.html",
    })
  );

  const panel = document.createElement("section");
  panel.className = "options-panel";

  const difficultyRow = document.createElement("div");
  difficultyRow.className = "chip-row";
  difficultyOptions.forEach((option) => {
    difficultyRow.append(
      createOptionChip({
        label: option.label,
        selected: selectedDifficulty === option.id,
        onClick: () => {
          selectedDifficulty = option.id;
          renderPage();
        },
      })
    );
  });

  const amountRow = document.createElement("div");
  amountRow.className = "chip-row";
  amountOptions.forEach((amount) => {
    amountRow.append(
      createOptionChip({
        label: `${amount} سؤال`,
        selected: selectedAmount === amount,
        onClick: () => {
          selectedAmount = amount;
          renderPage();
        },
      })
    );
  });

  panel.append(
    renderSectionTitle("اختر مستوى الصعوبة"),
    difficultyRow,
    renderSectionTitle("اختر عدد الأسئلة"),
    amountRow
  );

  const footer = document.createElement("div");
  footer.className = "quiz-page-actions";
  footer.append(
    createPrimaryButton({
      label: "ابدأ",
      disabled: !validateQuizOptions({ difficulty: selectedDifficulty, amount: selectedAmount }),
      onClick: () => {
        clearQuizQuestions();
        saveQuizSession({
          difficulty: selectedDifficulty,
          amount: selectedAmount,
        });
        window.location.href = "../quiz/quiz.html";
      },
    })
  );

  shell.append(panel, footer);
  root.append(shell);
}

renderPage();

