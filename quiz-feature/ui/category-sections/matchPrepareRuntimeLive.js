(function () {
  // Purpose: expose the browser-side list of backend live-ready subcategory ids.
  // The selection page now requires the live backend and does not prepare fake browser questions.
  const apiReadySubcategoryIds = [
    "countries-capitals",
    "countries-country-capitals",
    "countries-currencies",
    "countries-flags",
    "countries-geography",
    "countries-travel",
    "countries-what-country",
    "general-animals",
    "general-general-knowledge",
    "general-history",
    "general-global-logos",
    "general-logos",
    "general-technology",
  ];

  const wallaKelmaReadySubcategoryIds = [
    "no-word-default",
    "no-word-general",
    "no-word-islamic",
  ];

  const liveReadySubcategoryIds = [
    ...new Set([...apiReadySubcategoryIds, ...wallaKelmaReadySubcategoryIds]),
  ];

  window.QuizCategorySectionsRuntime = {
    ...(window.QuizCategorySectionsRuntime || {}),
    apiReadySubcategoryIds,
    wallaKelmaReadySubcategoryIds,
    liveReadySubcategoryIds,
    isSubcategoryApiReady: (subcategoryId) =>
      apiReadySubcategoryIds.includes(subcategoryId),
    isSubcategoryLiveReady: (subcategoryId) =>
      liveReadySubcategoryIds.includes(subcategoryId),
  };
})();
