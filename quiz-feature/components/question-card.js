import { createElement } from "../utils/dom.js";

export function createQuestionCard(question) {
  const card = createElement("section", { className: "question-card" });
  const list = createElement("ol", { className: "question-card__options" });

  question.options.forEach((option) => {
    list.append(createElement("li", { className: "question-card__option", text: option }));
  });

  card.append(
    createElement("span", { className: "question-card__meta", text: `${question.points} نقطة` }),
    createElement("h2", { className: "question-card__text", text: question.text }),
    list
  );

  return card;
}

