(() => {
  // Purpose: render the live category selection page and route either to
  // backend quiz preparation or the separate Walla Kelma session flow.
  const GAME_STORAGE_KEY = "seen-jeem-jeopardy-state";
  const MAX_SUBCATEGORY_SELECTIONS = 6;

  function mergePreparedPayloads(basePayload, browserPayload) {
    const baseQuestions = Array.isArray(basePayload?.questionBank)
      ? basePayload.questionBank
      : [];
    const browserQuestions = Array.isArray(browserPayload?.questionBank)
      ? browserPayload.questionBank
      : [];
    const mergedById = new Map();

    baseQuestions.forEach((category) => {
      if (category?.id) {
        mergedById.set(category.id, category);
      }
    });
    browserQuestions.forEach((category) => {
      if (category?.id) {
        mergedById.set(category.id, category);
      }
    });

    return {
      questionBank: Array.from(mergedById.values()),
      diagnostics: [
        ...(Array.isArray(basePayload?.diagnostics) ? basePayload.diagnostics : []),
        ...(Array.isArray(browserPayload?.diagnostics) ? browserPayload.diagnostics : []),
      ],
      apiReady: Boolean(basePayload?.apiReady) && Boolean(browserPayload?.apiReady),
    };
  }

  const WALLA_PROMPT_SLOTS = [
    { difficulty: "easy", points: 200 },
    { difficulty: "easy", points: 200 },
    { difficulty: "medium", points: 400 },
    { difficulty: "medium", points: 400 },
    { difficulty: "hard", points: 600 },
    { difficulty: "hard", points: 600 },
  ];

  function resolvePreferredPublicBaseUrl() {
    const runtime = window.QuizCategorySectionsRuntime || {};
    if (typeof runtime.resolvePublicBaseUrl === "function") {
      return runtime.resolvePublicBaseUrl();
    }
    const origin = window.location.origin || "";
    return /\/\/(127\.0\.0\.1|localhost)/.test(origin) ? "" : origin;
  }

  function resolveWallaPromptUrl(prompt) {
    const publicBaseUrl =
      (typeof prompt?.api_base_url === "string" && prompt.api_base_url.trim()) ||
      resolvePreferredPublicBaseUrl();
    if (prompt?.qr_url) {
      return String(prompt.qr_url);
    }
    if (prompt?.qr_path) {
      return `${publicBaseUrl}${prompt.qr_path}`;
    }
    if (prompt?.token) {
      return `${publicBaseUrl}/walla-kelma.html?token=${encodeURIComponent(
        prompt.token
      )}`;
    }
    return "";
  }

  function buildWallaCategoryPayload(item, promptBank) {
    return {
      id: item.subcategoryId,
      name: item.subcategoryTitle,
      backendCategory: item.subcategoryTitle,
      icon: (window.QuizCategorySectionsRuntime?.getPlaceholderIcon || (() => "🤐"))(
        item.imageKey,
        item.iconKey
      ),
      imageKey: item.imageKey || null,
      iconKey: item.iconKey || null,
      flagCode: item.flagCode || null,
      description: "جولات ولا كلمة برمز QR واسم سري يظهر على جهاز الممثل فقط.",
      sourceMode: "api",
      resolvedSource: "ولا كلمة",
      sourceType: "api",
      questions: promptBank.map((prompt, index) => ({
        id: `${item.subcategoryId}-walla-${index + 1}`,
        points: Number(prompt?.points) || WALLA_PROMPT_SLOTS[index]?.points || 200,
        difficulty:
          typeof prompt?.difficulty === "string" ? prompt.difficulty : "easy",
        question:
          "امسح رمز QR بالجوال ليظهر السر على جهاز الممثل فقط، ثم اضغط التالي لبدء المؤقت.",
        answer:
          (typeof prompt?.secret_value_ar === "string" && prompt.secret_value_ar.trim()) ||
          (typeof prompt?.secret_value === "string" && prompt.secret_value.trim()) ||
          "الجواب غير متاح",
        displayMode: "reveal_answer",
        questionType: "walla_kelma",
        visual: {
          type: "qr",
          value: resolveWallaPromptUrl(prompt),
        },
      })),
    };
  }

  function QuizCategorySectionsPage() {
    const runtime = window.QuizCategorySectionsRuntime || {};
    const loadCatalogRuntime = runtime.loadCatalogRuntime;
    const loadSourceMapRuntime = runtime.loadSourceMapRuntime;
    const readSession =
      runtime.readSession ||
      (() => ({
        categoryId: null,
        subcategoryId: null,
        difficulty: null,
        amount: null,
        questions: [],
      }));
    const writeSession = runtime.writeSession || (() => null);
    const RuntimeCategorySection = runtime.CategorySection;
    const RuntimeInfoModal = runtime.InfoModal;
    const apiSourceLookup = runtime.apiSourceLookup;
    const apiFetch = runtime.apiFetch;
    const [catalog, setCatalog] = React.useState([]);
    const [sourceMap, setSourceMap] = React.useState({});
    const [liveReadyIds, setLiveReadyIds] = React.useState([]);
    const [wallaReadyIds, setWallaReadyIds] = React.useState([]);
    const [questionCounts, setQuestionCounts] = React.useState({});
    const [loading, setLoading] = React.useState(true);
    const [preparingMatch, setPreparingMatch] = React.useState(false);
    const [error, setError] = React.useState("");
    const [backendReady, setBackendReady] = React.useState(false);
    const [selectedItems, setSelectedItems] = React.useState(() => {
      const session = readSession();
      if (Array.isArray(session.selectedSubcategories)) {
        return session.selectedSubcategories;
      }

      if (session.subcategoryId) {
        return [
          {
            categoryId: session.categoryId,
            categoryTitle: null,
            subcategoryId: session.subcategoryId,
            subcategoryTitle: null,
            imageKey: null,
            iconKey: null,
            flagCode: null,
          },
        ];
      }

      return [];
    });
    const [infoItem, setInfoItem] = React.useState(null);
    const liveReadyLookup = React.useMemo(
      () => new Set(liveReadyIds),
      [liveReadyIds]
    );
    React.useEffect(() => {
      if (!loadCatalogRuntime || !loadSourceMapRuntime || !apiFetch) {
        setError("مكوّنات التحميل لم تجهز بعد. حدّث الصفحة مرة واحدة.");
        setLoading(false);
        return;
      }

      Promise.all([
        loadCatalogRuntime(),
        loadSourceMapRuntime(),
        apiFetch("/api/quiz/live-subcategories")
          .then((response) => {
            if (!response.ok) {
              throw new Error("Failed to load live subcategories");
            }
            return response.json();
          }),
      ])
        .then(([catalogModule, sourceModule, livePayload]) => {
          const counts = {};
          const liveIds = Array.isArray(livePayload?.subcategoryIds)
            ? livePayload.subcategoryIds
            : [];
          const nextWallaIds = Array.isArray(livePayload?.wallaKelmaSubcategoryIds)
            ? livePayload.wallaKelmaSubcategoryIds
            : [];
          liveIds.forEach((subcategoryId) => {
            counts[subcategoryId] = 6;
          });

          const sourceLookup = Object.fromEntries(
            sourceModule.apiSourceMap.map((source) => [source.key, source])
          );

          setCatalog(catalogModule.categoryCatalog);
          setSourceMap(sourceLookup);
          setBackendReady(true);
          setLiveReadyIds(liveIds);
          setWallaReadyIds(nextWallaIds);
          setQuestionCounts(counts);
          setSelectedItems((currentItems) => {
            const supportedIds = new Set(liveIds);
            const nextItems = currentItems
              .filter((item) =>
                supportedIds.has(item.subcategoryId)
              )
              .slice(0, MAX_SUBCATEGORY_SELECTIONS);
            if (nextItems.length !== currentItems.length) {
              const firstItem = nextItems[0] || null;
              writeSession({
                selectedSubcategories: nextItems,
                categoryId: firstItem ? firstItem.categoryId : null,
                subcategoryId: firstItem ? firstItem.subcategoryId : null,
                difficulty: null,
                amount: null,
                questions: [],
                preparedQuestionBank: [],
              });
            }
            return nextItems;
          });
          setLoading(false);
        })
        .catch((loadError) => {
          setBackendReady(false);
          setCatalog([]);
          setLiveReadyIds([]);
          setWallaReadyIds([]);
          setQuestionCounts({});
          setError(
            "تعذر الوصول إلى الـ backend الحي. شغّل المشروع عبر python3 server.py ثم حدّث الصفحة."
          );
          setLoading(false);
          console.error(loadError);
        });
    }, []);

    const selectedIds = React.useMemo(
      () => selectedItems.map((item) => item.subcategoryId),
      [selectedItems]
    );

    const selectedSummary = React.useMemo(() => {
      if (!selectedItems.length) {
        return "لم يتم اختيار أي فرعية بعد.";
      }

      return `تم اختيار ${selectedItems.length} فرعية.`;
    }, [selectedItems]);
    const isOnlyWallaKelmaSelection =
      selectedItems.length > 0 &&
      selectedItems.every((item) => item.categoryId === "no-word");

    const handleSelectSubcategory = (category, subcategory) => {
      if (!liveReadyLookup.has(subcategory.id)) {
        return;
      }

      setSelectedItems((currentItems) => {
        const exists = currentItems.some(
          (item) => item.subcategoryId === subcategory.id
        );

        if (!exists && currentItems.length >= MAX_SUBCATEGORY_SELECTIONS) {
          setError("يمكن اختيار ٦ فرعيات كحد أقصى.");
          return currentItems;
        }

        const nextItems = exists
          ? currentItems.filter((item) => item.subcategoryId !== subcategory.id)
          : [
              ...currentItems,
              {
                categoryId: category.id,
                categoryTitle: category.title,
                subcategoryId: subcategory.id,
                subcategoryTitle: subcategory.title,
                imageKey: subcategory.imageKey || null,
                iconKey: subcategory.iconKey || null,
                flagCode: subcategory.flagCode || null,
              },
            ];

        const firstItem = nextItems[0] || null;

        writeSession({
          selectedSubcategories: nextItems,
          categoryId: firstItem ? firstItem.categoryId : null,
          subcategoryId: firstItem ? firstItem.subcategoryId : null,
          difficulty: null,
          amount: null,
          questions: [],
          preparedQuestionBank: [],
        });

        if (exists || nextItems.length <= MAX_SUBCATEGORY_SELECTIONS) {
          setError("");
        }

        return nextItems;
      });
    };

    const handleRemoveSelection = (subcategoryId) => {
      setSelectedItems((currentItems) => {
        const nextItems = currentItems.filter(
          (item) => item.subcategoryId !== subcategoryId
        );
        const firstItem = nextItems[0] || null;

        writeSession({
          selectedSubcategories: nextItems,
          categoryId: firstItem ? firstItem.categoryId : null,
          subcategoryId: firstItem ? firstItem.subcategoryId : null,
          difficulty: null,
          amount: null,
          questions: [],
          preparedQuestionBank: [],
        });

        return nextItems;
      });
    };

    const syncSelectionsToGameState = () => {
      try {
        const raw = localStorage.getItem(GAME_STORAGE_KEY);
        const currentGameState = raw ? JSON.parse(raw) : {};
        const selectedIdsForBoard = selectedItems.map((item) => item.subcategoryId);

        localStorage.setItem(
          GAME_STORAGE_KEY,
          JSON.stringify({
            ...currentGameState,
            selectedCategoryIds: selectedIdsForBoard,
            selectedSubcategories: selectedItems,
            usedQuestionIds: [],
            activeQuestionId: null,
            activeQuestionRevealed: false,
            activeQuestionResolved: false,
            lastFeedback: null,
            scores: [0, 0],
            currentTeamIndex: 0,
          })
        );
      } catch (error) {
        console.error("Failed to sync selected subcategories to game state", error);
      }
    };

    const handleOpenInfo = (category, subcategory) => {
      setInfoItem({
        category,
        subcategory,
        source:
          sourceMap[subcategory.apiSource] ||
          apiSourceLookup?.get?.(subcategory.apiSource),
      });
    };

    if (loading) {
      return (
        <div className="quiz-category-page">
          <div className="quiz-category-page__loading">
            جارٍ تحميل الفئات الجديدة...
          </div>
        </div>
      );
    }

    if (error) {
      return (
        <div className="quiz-category-page">
          <div className="quiz-category-page__error">{error}</div>
        </div>
      );
    }

    return (
      <div className="quiz-category-page" dir="rtl">
        <header className="quiz-category-page__header">
          <div className="quiz-category-page__hero">اختر الفئات</div>
          <p className="quiz-category-page__subtitle">
            اختر الفرعية التي تريد اللعب بها. الفروع المدعومة تبدأ من APIs حية عند بدء اللوحة،
            وغير المدعومة تظهر تحت الإنشاء حتى يكتمل ربطها.
          </p>
          <div className="quiz-category-page__rules">
            كل فرعية تحتوي على ٦ أسئلة:
            {" "}
            <strong>٢ سهل</strong>
            {" "}
            +
            {" "}
            <strong>٢ متوسط</strong>
            {" "}
            +
            {" "}
            <strong>٢ صعب</strong>
            {" "}
            • الحد الأقصى للاختيار:
            {" "}
            <strong>٦ فرعيات</strong>
            {" "}
            •
            {" "}
            <strong>ولا كلمة</strong>
            {" "}
            تعمل كجلسة منفصلة ويُفضّل اختيار فرعية واحدة لها فقط.
          </div>
        </header>

        <main className="quiz-category-page__sections">
          {RuntimeCategorySection
            ? catalog.map((category) => (
                <RuntimeCategorySection
                  key={category.id}
                  category={category}
                  selectedSubcategoryIds={selectedIds}
                  questionCounts={questionCounts}
                  isSubcategoryAvailable={(subcategory) =>
                    liveReadyLookup.has(subcategory.id)
                  }
                  onSelectSubcategory={handleSelectSubcategory}
                  onOpenInfo={handleOpenInfo}
                />
              ))
            : null}
        </main>

        <aside className="quiz-selection-rail" aria-live="polite">
          <div className="quiz-selection-rail__header">
            <span className="quiz-selection-rail__title">اختياراتك</span>
            <span className="quiz-selection-rail__count">
              {selectedItems.length || 0}
            </span>
          </div>

          <div className="quiz-selection-rail__body">
            <div className="quiz-selection-rail__list">
              {selectedItems.length ? (
                selectedItems.map((item) => {
                  const icon =
                    (runtime.getPlaceholderIcon || (() => "✨"))(
                      item.imageKey,
                      item.iconKey
                    );
                  const flag =
                    item.flagCode &&
                    (runtime.flagCodeToEmoji || (() => "🏳️"))(item.flagCode);

                  return (
                    <div
                      key={item.subcategoryId}
                      className="quiz-selection-rail__item"
                    >
                      <button
                        type="button"
                        className="quiz-selection-rail__remove"
                        aria-label={`إزالة ${item.subcategoryTitle}`}
                        onClick={() => handleRemoveSelection(item.subcategoryId)}
                      >
                        ×
                      </button>

                      <div className="quiz-selection-rail__thumb">
                        <span className="quiz-selection-rail__thumb-icon">{icon}</span>
                        {flag ? (
                          <span className="quiz-selection-rail__thumb-flag">{flag}</span>
                        ) : null}
                      </div>

                      <div className="quiz-selection-rail__item-footer">
                        <span className="quiz-selection-rail__item-title">
                          {item.subcategoryTitle}
                        </span>
                      </div>
                    </div>
                  );
                })
              ) : (
                <div className="quiz-selection-rail__empty">
                  اختر فرعية وستظهر هنا.
                </div>
              )}
            </div>
          </div>
        </aside>

        <div className="quiz-category-page__footer">
          <div className="quiz-category-page__footer-copy">
            <span className="quiz-category-page__footer-title">الفرعيات المختارة: {selectedItems.length}</span>
            <span className="quiz-category-page__footer-subtitle">
              البطاقات غير المدعومة تظهر تحت الإنشاء، ويمكنك اختيار حتى ٦ فرعيات فقط وإزالة أي عنصر من العمود الجانبي قبل المتابعة.
            </span>
          </div>

          <button
            type="button"
            className="quiz-category-page__footer-button"
            disabled={!selectedItems.length || preparingMatch}
            onClick={async () => {
              if (!selectedItems.length) return;
              setPreparingMatch(true);
              setError("");

              try {
                const noWordItems = selectedItems.filter(
                  (item) => item.categoryId === "no-word"
                );
                const quizItems = selectedItems.filter(
                  (item) => item.categoryId !== "no-word"
                );

                const wallaQuestionBank = await Promise.all(
                  noWordItems.map(async (item) => {
                    const promptBank = await Promise.all(
                      WALLA_PROMPT_SLOTS.map(async (slot, slotIndex) => {
                        if (!backendReady) {
                          throw new Error("ولا كلمة تحتاج backend حي ولا يوجد fallback محلي.");
                        }

                        const wallaResponse = await apiFetch("/api/walla-kelma/create", {
                          method: "POST",
                          headers: {
                            "Content-Type": "application/json",
                          },
                          body: JSON.stringify({
                            selectedSubcategory: item,
                            difficulty: slot.difficulty,
                          }),
                        });

                        const wallaPayload = await wallaResponse.json().catch(() => ({}));
                        if (!wallaResponse.ok) {
                          throw new Error(
                            typeof wallaPayload?.details === "string" && wallaPayload.details.trim()
                              ? wallaPayload.details.trim()
                              : "تعذر بدء جولة ولا كلمة من المصدر الحي."
                          );
                        }

                        let privatePayload = {};
                        if (wallaPayload?.token) {
                          const privateResponse = await apiFetch(
                            `/api/walla-kelma/session/${encodeURIComponent(wallaPayload.token)}`
                          );
                          privatePayload = await privateResponse.json().catch(() => ({}));
                          if (!privateResponse.ok) {
                            throw new Error(
                              typeof privatePayload?.details === "string" &&
                                privatePayload.details.trim()
                                ? privatePayload.details.trim()
                                : "تعذر جلب جواب جولة ولا كلمة."
                            );
                          }
                        }

                        return {
                          ...wallaPayload,
                          ...privatePayload,
                          points: slot.points,
                          slotIndex,
                        };
                      })
                    );
                    return buildWallaCategoryPayload(item, promptBank);
                  })
                );

                let payload = quizItems.length
                  ? await (async () => {
                      if (!backendReady) {
                        throw new Error("هذا الفرع يحتاج backend حي ولا يوجد fallback محلي.");
                      }

                      const response = await apiFetch("/api/quiz/prepare-match", {
                        method: "POST",
                        headers: {
                          "Content-Type": "application/json",
                        },
                        body: JSON.stringify({
                          selectedSubcategories: quizItems,
                        }),
                      });

                      if (!response.ok) {
                        let details = "";
                        try {
                          const errorPayload = await response.json();
                          details =
                            typeof errorPayload?.details === "string" &&
                            errorPayload.details.trim() !== ""
                              ? errorPayload.details.trim()
                              : "";
                        } catch (parseError) {
                          details = "";
                        }

                        throw new Error(
                          details
                            ? `تعذر تجهيز بنك الأسئلة من الـ API: ${details}`
                            : `prepare-match returned ${response.status}`
                        );
                      }

                      return response.json();
                    })()
                  : {
                      questionBank: [],
                      diagnostics: [],
                      apiReady: true,
                    };

                if (wallaQuestionBank.length) {
                  payload = mergePreparedPayloads(payload, {
                    questionBank: wallaQuestionBank,
                    diagnostics: wallaQuestionBank.map((category) => ({
                      id: category.id,
                      name: category.name,
                      backendCategory: category.backendCategory,
                      sourceMode: "api",
                      questionCount: Array.isArray(category.questions)
                        ? category.questions.length
                        : 0,
                      source: "ولا كلمة",
                      sourceType: "api",
                    })),
                    apiReady: true,
                  });
                }

                const preparedQuestionBank = Array.isArray(payload.questionBank)
                  ? payload.questionBank.filter(
                      (category) =>
                        category &&
                        Array.isArray(category.questions) &&
                        category.questions.length &&
                        category.sourceMode === "api"
                    )
                  : [];
                const diagnostics = Array.isArray(payload.diagnostics)
                  ? payload.diagnostics
                  : [];
                const preparedIds = new Set(
                  preparedQuestionBank.map((category) => category.id).filter(Boolean)
                );
                const latestDiagnosticById = new Map();
                diagnostics.forEach((item) => {
                  const diagnosticId = item?.id;
                  if (diagnosticId) {
                    latestDiagnosticById.set(diagnosticId, item);
                  }
                });
                const failedItems = Array.from(latestDiagnosticById.values()).filter(
                  (item) => item.sourceMode !== "api" && !preparedIds.has(item.id)
                );

                if (!preparedQuestionBank.length) {
                  const failureReason = failedItems
                    .map((item) =>
                      item?.reason
                        ? `${item.name || item.id}: ${item.reason}`
                        : item.name || item.id
                    )
                    .filter(Boolean)
                    .join("، ");
                  throw new Error(
                    failureReason
                      ? `لم يتم تجهيز أي أسئلة من المصادر الحية: ${failureReason}`
                      : "لم يتم تجهيز أي أسئلة قبل بدء اللوحة."
                  );
                }

                const fullyPrepared = preparedQuestionBank.length === selectedItems.length;

                if (failedItems.length || !fullyPrepared) {
                  const failedNames = failedItems
                    .map((item) => item.name)
                    .filter(Boolean)
                    .join("، ");
                  throw new Error(
                    failedNames
                      ? `تعذر تجهيز بعض الفرعيات من الـ API: ${failedNames}.`
                      : "لم يكتمل تجهيز بنك الأسئلة من الـ API."
                  );
                }

                writeSession({
                  selectedSubcategories: selectedItems,
                  preparedQuestionBank: preparedQuestionBank,
                  wallaKelmaSession: null,
                });
                syncSelectionsToGameState();
                window.location.href = "./board.html";
              } catch (requestError) {
                console.error(requestError);
                writeSession({
                  selectedSubcategories: selectedItems,
                  preparedQuestionBank: [],
                  wallaKelmaSession: null,
                });
                setError(
                  requestError instanceof Error
                    ? requestError.message
                    : "تعذر تجهيز بنك الأسئلة من الـ API."
                );
              } finally {
                setPreparingMatch(false);
              }
            }}
          >
            {preparingMatch
              ? "جاري التجهيز..."
              : isOnlyWallaKelmaSelection
              ? "ابدأ ولا كلمة"
              : "ابدأ اللوحة"}
          </button>
        </div>

        {RuntimeInfoModal ? (
          <RuntimeInfoModal item={infoItem} onClose={() => setInfoItem(null)} />
        ) : null}
      </div>
    );
  }

  window.QuizCategorySectionsRuntime = {
    ...(window.QuizCategorySectionsRuntime || {}),
    CategorySectionsPage: QuizCategorySectionsPage,
  };
})();
