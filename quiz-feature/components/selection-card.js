import { createElement } from "../utils/dom.js";

export function createSelectionCard({ title, description, icon, badge = "", selected = false, info = "", onClick, onInfoClick }) {
  const button = createElement("button", {
    className: `selection-card${selected ? " selection-card--selected" : ""}`,
    attributes: { type: "button" },
  });

  const infoButton = createElement("button", {
    className: "selection-card__info",
    text: "i",
    attributes: { type: "button", "aria-label": `معلومات عن ${title}` },
  });

  infoButton.addEventListener("click", (event) => {
    event.stopPropagation();
    onInfoClick?.(info, title);
  });

  const media = createElement("div", { className: "selection-card__media" });
  media.append(createElement("span", { className: "selection-card__icon", text: icon || "❖" }));

  const body = createElement("div", { className: "selection-card__body" });
  body.append(
    createElement("h3", { className: "selection-card__title", text: title }),
    createElement("p", { className: "selection-card__description", text: description })
  );

  if (badge) {
    body.append(createElement("span", { className: "selection-card__badge", text: badge }));
  }

  button.append(infoButton, media, body);
  button.addEventListener("click", () => onClick?.());
  return button;
}

