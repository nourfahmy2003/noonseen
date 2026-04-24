import { createElement } from "../utils/dom.js";

export function createErrorState(message = "حدث خطأ غير متوقع.") {
  return createElement("div", {
    className: "status-panel status-panel--error",
    html: `<strong>تعذر إكمال العملية</strong><p>${message}</p>`,
  });
}

