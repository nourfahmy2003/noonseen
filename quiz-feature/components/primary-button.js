import { createElement } from "../utils/dom.js";

export function createPrimaryButton({ label, disabled = false, onClick }) {
  const button = createElement("button", {
    className: "primary-button",
    text: label,
    attributes: { type: "button" },
  });

  button.disabled = disabled;
  button.addEventListener("click", () => onClick?.());
  return button;
}

