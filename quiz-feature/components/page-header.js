import { createElement } from "../utils/dom.js";

export function createPageHeader({ title, subtitle = "", backHref = null }) {
  const wrapper = createElement("header", { className: "quiz-page-header" });
  const titleRow = createElement("div", { className: "quiz-page-header__row" });

  if (backHref) {
    const backLink = createElement("a", {
      className: "quiz-back-link",
      text: "رجوع",
      attributes: { href: backHref },
    });
    titleRow.append(backLink);
  }

  const titleBlock = createElement("div", { className: "quiz-page-header__copy" });
  titleBlock.append(
    createElement("h1", { className: "quiz-page-title", text: title }),
    createElement("p", { className: "quiz-page-subtitle", text: subtitle })
  );

  titleRow.append(titleBlock);
  wrapper.append(titleRow);
  return wrapper;
}

