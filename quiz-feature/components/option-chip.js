import { createElement } from "../utils/dom.js";

export function createOptionChip({ label, selected = false, onClick }) {
  const button = createElement("button", {
    className: `option-chip${selected ? " option-chip--selected" : ""}`,
    text: label,
    attributes: { type: "button" },
  });

  button.addEventListener("click", () => onClick?.());
  return button;
}

