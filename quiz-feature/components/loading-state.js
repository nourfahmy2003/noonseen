import { createElement } from "../utils/dom.js";

export function createLoadingState(message = "جاري تحميل الأسئلة...") {
  return createElement("div", {
    className: "status-panel status-panel--loading",
    html: `<div class="status-panel__spinner"></div><p>${message}</p>`,
  });
}

