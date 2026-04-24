// Purpose: wait until all category-section runtime pieces are loaded, then mount the page.
const runtime = window.QuizCategorySectionsRuntime || {};

runtime.apiSourceLookup = new Map();

window.QuizCategorySectionsRuntime = runtime;

const root = ReactDOM.createRoot(document.getElementById("page-root"));

function mountWhenReady() {
  const currentRuntime = window.QuizCategorySectionsRuntime || {};
  const requiredKeys = [
    "CategorySectionsPage",
    "CategorySection",
    "SubcategoryCard",
    "InfoButton",
    "InfoModal",
    "CardVisual",
    "FlagBadge",
    "getPlaceholderIcon",
    "getVisualAccent",
    "flagCodeToEmoji",
    "loadCatalogRuntime",
    "loadSourceMapRuntime",
    "apiFetch",
    "readSession",
    "writeSession",
  ];

  const isReady = requiredKeys.every((key) => Boolean(currentRuntime[key]));

  if (!isReady) {
    window.requestAnimationFrame(mountWhenReady);
    return;
  }

  root.render(<currentRuntime.CategorySectionsPage />);
}

mountWhenReady();
