import { createErrorState } from "../../components/error-state.js";
import { createLoadingState } from "../../components/loading-state.js";
import { createPageHeader } from "../../components/page-header.js";
import { createQuestionCard } from "../../components/question-card.js";
import { getSubcategoriesByCategory } from "../../config/subcategory-config.js";
import { fetchQuizQuestions } from "../../services/quiz-api.js";
import { getQuizSession, saveQuizSession } from "../../state/quiz-session.js";
import { qs } from "../../utils/dom.js";

const root = qs("#quiz-feature-root");
const session = getQuizSession();

if (!session.categoryId || !session.subcategoryId || !session.difficulty || !session.amount) {
  window.location.href = "../category-selection/category-selection.html";
}

const subcategory = getSubcategoriesByCategory(session.categoryId).find(
  (item) => item.id === session.subcategoryId
);

if (!subcategory) {
  window.location.href = "../subcategory-selection/subcategory-selection.html";
}

function renderShell() {
  root.innerHTML = "";
  const shell = document.createElement("section");
  shell.className = "quiz-shell";
  shell.append(
    createPageHeader({
      title: subcategory.name,
      subtitle: "تم جلب الأسئلة بعد ضغط Start فقط.",
      backHref: "../quiz-options/quiz-options.html",
    })
  );
  root.append(shell);
  return shell;
}

async function renderQuizPage() {
  const shell = renderShell();
  shell.append(createLoadingState());

  try {
    const questions =
      session.questions?.length > 0
        ? session.questions
        : await fetchQuizQuestions({
            provider: subcategory.provider,
            categoryId: session.categoryId,
            subcategoryId: session.subcategoryId,
            difficulty: session.difficulty,
            amount: session.amount,
          });

    saveQuizSession({ questions });
    shell.innerHTML = "";
    shell.append(
      createPageHeader({
        title: subcategory.name,
        subtitle: `عدد الأسئلة: ${questions.length} • الصعوبة: ${session.difficulty}`,
        backHref: "../quiz-options/quiz-options.html",
      })
    );

    const list = document.createElement("section");
    list.className = "question-list";
    questions.forEach((question) => list.append(createQuestionCard(question)));
    shell.append(list);
  } catch (error) {
    shell.innerHTML = "";
    shell.append(
      createPageHeader({
        title: subcategory.name,
        subtitle: "تعذر تحميل الأسئلة",
        backHref: "../quiz-options/quiz-options.html",
      }),
      createErrorState(error.message)
    );
  }
}

renderQuizPage();

