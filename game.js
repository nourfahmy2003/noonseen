const SeenJeemGame = (() => {
  // Purpose: run the quiz board against the prepared live backend payload.
  const STORAGE_KEY = "seen-jeem-jeopardy-state";
  const FEATURE_STORAGE_KEY = "quiz-feature-session";
  const PUBLIC_BASE_STORAGE_KEY = "seen-jeem-public-base";
  const MIN_CATEGORIES = 4;
  const MAX_CATEGORIES = 6;
  const BRAND_LOGO_PATH = "assets/Noon_seen.png";
  const BOARD_POINT_VALUES = [200, 400, 600];
  const DUPLICATES_PER_VALUE = 2;
  const BOARD_SLOT_POINTS = BOARD_POINT_VALUES.flatMap((value) =>
    Array.from({ length: DUPLICATES_PER_VALUE }, () => value)
  );
  const DEFAULT_TEAMS = ["فريق ١", "فريق ٢"];
  const LIVE_QUESTION_SOURCE_CONFIG = {
    mode: "prepared_api",
    prepareEndpoint: "/api/quiz/prepare-match",
    liveSubcategoriesEndpoint: "/api/quiz/live-subcategories",
  };

  /*
    Game state flows between pages through localStorage.
    - index.html writes team names.
    - categories.html writes selected categories.
    - board.html updates scores, turn, used cells, and the open question state.
    - results.html reads the final result and resets the match when needed.

    Runtime boards now use the live prepared API payload stored in localStorage.
    Legacy local banks have been removed from the active runtime bundle.

    To change the minimum selected categories, edit MIN_CATEGORIES.
  */
  const LOCAL_QUESTION_BANK = [];
  let QUESTION_BANK = [];
  let QUESTION_SOURCE_LABEL = "غير محمل";
  let QUESTION_SOURCE_ERROR = null;
  let questionBankPromise = null;
  let activeQuestionTimerInterval = null;
  let wallaTimerInterval = null;

  function loadFeatureSessionFromStorage() {
    try {
      const raw = localStorage.getItem(FEATURE_STORAGE_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (error) {
      return null;
    }
  }

  function hasFeatureSelections() {
    const featureSession = loadFeatureSessionFromStorage();
    return Boolean(
      featureSession &&
        Array.isArray(featureSession.selectedSubcategories) &&
        featureSession.selectedSubcategories.length
    );
  }

  function cleanPlaceholderQuestionText(text) {
    let value = String(text || "").trim();

    if (value.includes(":")) {
      value = value.split(":").slice(1).join(":").trim();
    }

    value = value.replaceAll("الإجابة التجريبية", "الإجابة");
    value = value.replaceAll("لهذا الفرع", "").replace(/\s{2,}/g, " ").trim();

    return value || "ما الإجابة المناسبة؟";
  }

  function cleanPlaceholderAnswerText(text) {
    const value = String(text || "").trim();
    return value || "إجابة غير متاحة";
  }

  function cleanPlaceholderOptions(options, answer) {
    const cleaned = Array.isArray(options)
      ? options
          .map((option) => String(option || "").trim())
          .filter((option, index, list) => option && list.indexOf(option) === index)
      : [];

    if (!cleaned.includes(answer)) {
      cleaned.unshift(answer);
    }

    return cleaned.length ? cleaned : [answer];
  }

  function normalizePreparedQuestion(question, fallbackId, fallbackPoints) {
    const text =
      typeof question?.text === "string" && question.text.trim() !== ""
        ? question.text.trim()
        : typeof question?.question === "string" && question.question.trim() !== ""
        ? question.question.trim()
        : "سؤال غير متاح.";
    const answer =
      typeof question?.answer === "string" && question.answer.trim() !== ""
        ? question.answer.trim()
        : typeof question?.correctAnswer === "string" && question.correctAnswer.trim() !== ""
        ? question.correctAnswer.trim()
        : "إجابة غير متاحة.";

    return {
      id: question?.id || fallbackId,
      points: Number(question?.points) || fallbackPoints,
      difficulty:
        typeof question?.difficulty === "string" && question.difficulty.trim() !== ""
          ? question.difficulty.trim()
          : null,
      questionType:
        typeof question?.questionType === "string" && question.questionType.trim() !== ""
          ? question.questionType.trim()
          : null,
      displayMode:
        typeof question?.displayMode === "string" && question.displayMode.trim() !== ""
          ? question.displayMode.trim()
          : question?.visual
          ? "reveal_visual"
          : "reveal_answer",
      text,
      answer,
      visual:
        question?.visual &&
        typeof question.visual === "object"
          ? {
              ...question.visual,
              type: String(question.visual.type || ""),
              value: String(question.visual.value || ""),
              fallbackText:
                typeof question.visual.fallbackText === "string"
                  ? question.visual.fallbackText
                  : "",
            }
          : null,
    };
  }

  function normalizePreparedQuestionBank(preparedQuestionBank) {
    return preparedQuestionBank.map((category, categoryIndex) => ({
      ...category,
      questions: Array.isArray(category?.questions)
        ? category.questions.map((question, questionIndex) =>
            normalizePreparedQuestion(
              question,
              `${category?.id || "category"}-${questionIndex + 1}`,
              BOARD_SLOT_POINTS[questionIndex] || 200
            )
          )
        : [],
    }));
  }

  async function loadFeatureQuestionBank() {
    const featureSession = loadFeatureSessionFromStorage();
    const selectedSubcategories = Array.isArray(featureSession?.selectedSubcategories)
      ? featureSession.selectedSubcategories
      : [];
    const preparedQuestionBank = Array.isArray(featureSession?.preparedQuestionBank)
      ? featureSession.preparedQuestionBank
      : [];

    if (!selectedSubcategories.length) {
      throw new Error("No selected subcategories found in feature session");
    }

    if (
      preparedQuestionBank.length &&
      preparedQuestionBank.every(
        (category) =>
          category &&
          category.sourceMode === "api" &&
          Array.isArray(category.questions) &&
          category.questions.length
      )
    ) {
      QUESTION_BANK = normalizePreparedQuestionBank(preparedQuestionBank);
      QUESTION_SOURCE_LABEL = "API";
      QUESTION_SOURCE_ERROR = null;
      return QUESTION_BANK;
    }

    throw new Error("لم يتم تجهيز بنك أسئلة API قبل فتح اللوحة.");
  }

  function createInitialState() {
    return {
      teamNames: [...DEFAULT_TEAMS],
      selectedCategoryIds: [],
      selectedSubcategories: [],
      scores: [0, 0],
      currentTeamIndex: 0,
      usedQuestionIds: [],
      activeQuestionId: null,
      activeQuestionOpenedAt: null,
      activeQuestionView: "prompt",
      activeQuestionRevealed: false,
      activeQuestionResolved: false,
      lastFeedback: null,
    };
  }

  function renderBrandLogo(className, alt = "نون جيم") {
    return `<img src="${BRAND_LOGO_PATH}" alt="${escapeHtml(alt)}" class="${className}" />`;
  }

  function getQueryParam(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name);
  }

  function decodeBase64UrlJson(value) {
    try {
      const normalized = String(value || "")
        .replace(/-/g, "+")
        .replace(/_/g, "/");
      const padded = normalized + "=".repeat((4 - (normalized.length % 4 || 4)) % 4);
      return JSON.parse(decodeURIComponent(escape(atob(padded))));
    } catch (error) {
      return null;
    }
  }

  function buildQrImageUrl(value) {
    return `https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=${encodeURIComponent(
      value
    )}`;
  }

  function normalizeBaseUrl(value) {
    return String(value || "").trim().replace(/\/$/, "");
  }

  function getPublicBaseUrl() {
    try {
      const cached = normalizeBaseUrl(sessionStorage.getItem(PUBLIC_BASE_STORAGE_KEY));
      if (cached) {
        return cached;
      }
    } catch (error) {
      // Ignore storage failures.
    }

    const origin = normalizeBaseUrl(window.location.origin);
    if (origin && origin !== "null" && !isLocalhostUrl(origin)) {
      return origin;
    }
    return "";
  }

  function buildApiUrl(path, baseUrl = "") {
    const normalizedPath = path.startsWith("/") ? path : `/${path}`;
    const normalizedBaseUrl = normalizeBaseUrl(baseUrl);
    return normalizedBaseUrl ? `${normalizedBaseUrl}${normalizedPath}` : normalizedPath;
  }

  function resolveWallaApiBaseUrl() {
    const explicitBaseUrl = normalizeBaseUrl(getQueryParam("base"));
    if (explicitBaseUrl) {
      return explicitBaseUrl;
    }

    const publicBaseUrl = getPublicBaseUrl();
    if (publicBaseUrl) {
      return publicBaseUrl;
    }

    const origin = normalizeBaseUrl(window.location.origin);
    return origin && origin !== "null" ? origin : "";
  }

  function isLocalhostUrl(value) {
    try {
      const url = new URL(value, window.location.origin);
      return ["127.0.0.1", "localhost"].includes(url.hostname);
    } catch (error) {
      return false;
    }
  }

  function formatWallaSeconds(totalSeconds) {
    const safeSeconds = Math.max(0, Number(totalSeconds || 0));
    return String(safeSeconds);
  }

  function getWallaRemainingSeconds(openedAt, points) {
    const durationSeconds = getWallaDuration(points);
    if (!openedAt) {
      return durationSeconds;
    }

    const elapsedSeconds = Math.max(0, Math.floor((Date.now() - Number(openedAt)) / 1000));
    return Math.max(0, durationSeconds - elapsedSeconds);
  }

  function loadStateFromStorage() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) {
        return createInitialState();
      }

      const parsed = JSON.parse(raw);
      return {
        ...createInitialState(),
        ...parsed,
        teamNames:
          Array.isArray(parsed.teamNames) && parsed.teamNames.length === 2
            ? parsed.teamNames
            : [...DEFAULT_TEAMS],
        selectedCategoryIds: Array.isArray(parsed.selectedCategoryIds)
          ? parsed.selectedCategoryIds
          : [],
        selectedSubcategories: Array.isArray(parsed.selectedSubcategories)
          ? parsed.selectedSubcategories
          : [],
        scores:
          Array.isArray(parsed.scores) && parsed.scores.length === 2
            ? parsed.scores
            : [0, 0],
        usedQuestionIds: Array.isArray(parsed.usedQuestionIds) ? parsed.usedQuestionIds : [],
        activeQuestionOpenedAt:
          typeof parsed.activeQuestionOpenedAt === "number"
            ? parsed.activeQuestionOpenedAt
            : null,
        activeQuestionView:
          parsed.activeQuestionView === "timer" ||
          parsed.activeQuestionView === "prompt" ||
          parsed.activeQuestionView === "answer"
            ? parsed.activeQuestionView
            : "prompt",
      };
    } catch (error) {
      return createInitialState();
    }
  }

  function saveStateToStorage(state) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }

  function clearActiveQuestionState(state) {
    return {
      ...state,
      activeQuestionId: null,
      activeQuestionOpenedAt: null,
      activeQuestionView: "prompt",
      activeQuestionRevealed: false,
      activeQuestionResolved: false,
      lastFeedback: null,
    };
  }

  function resetBoardProgress(state, preserveCategories = true) {
    return clearActiveQuestionState({
      ...state,
      selectedCategoryIds: preserveCategories ? state.selectedCategoryIds : [],
      selectedSubcategories: preserveCategories ? state.selectedSubcategories : [],
      scores: [0, 0],
      currentTeamIndex: 0,
      usedQuestionIds: [],
    });
  }

  function resetEverything() {
    saveStateToStorage(createInitialState());
  }

  function goTo(page) {
    window.location.href = page;
  }

  function clearActiveQuestionTimer() {
    if (activeQuestionTimerInterval) {
      window.clearInterval(activeQuestionTimerInterval);
      activeQuestionTimerInterval = null;
    }
  }

  function clearWallaTimer() {
    if (wallaTimerInterval) {
      window.clearInterval(wallaTimerInterval);
      wallaTimerInterval = null;
    }
  }

  function getRoot() {
    return document.getElementById("page-root");
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function getCategoryById(categoryId) {
    return QUESTION_BANK.find((category) => category.id === categoryId);
  }

  function getQuestionById(questionId) {
    for (const category of QUESTION_BANK) {
      const question = category.questions.find((item) => item.id === questionId);
      if (question) {
        return {
          ...question,
          categoryId: category.id,
          categoryName: category.name,
        };
      }
    }

    return null;
  }

  function getSelectedCategories(state) {
    return state.selectedCategoryIds
      .map((categoryId) => getCategoryById(categoryId))
      .filter(Boolean)
      .slice(0, MAX_CATEGORIES);
  }

  function chunkIntoRows(items, size) {
    const rows = [];
    for (let index = 0; index < items.length; index += size) {
      rows.push(items.slice(index, index + size));
    }
    return rows;
  }

  function getTotalQuestionsCount(state) {
    return getSelectedCategories(state).reduce(
      (total, category) => total + category.questions.length,
      0
    );
  }

  function checkGameEnd(state) {
    const totalQuestions = getTotalQuestionsCount(state);
    if (!totalQuestions) {
      return false;
    }

    return state.usedQuestionIds.length >= totalQuestions;
  }

  function getCorrectAnswerText(question) {
    if (typeof question?.answer === "string" && question.answer.trim() !== "") {
      return question.answer;
    }

    if (
      typeof question?.correctAnswer === "string" &&
      question.correctAnswer.trim() !== ""
    ) {
      return question.correctAnswer;
    }

    return "إجابة غير متاحة.";
  }

  function flagCodeToEmoji(flagCode) {
    const normalized = String(flagCode || "").trim().toUpperCase();
    if (!/^[A-Z]{2}$/.test(normalized)) {
      return "";
    }

    return String.fromCodePoint(
      ...normalized.split("").map((char) => 127397 + char.charCodeAt(0))
    );
  }

  function formatElapsedTime(openedAt) {
    if (!openedAt) {
      return "00:00";
    }

    const elapsedSeconds = Math.max(0, Math.floor((Date.now() - openedAt) / 1000));
    const minutes = String(Math.floor(elapsedSeconds / 60)).padStart(2, "0");
    const seconds = String(elapsedSeconds % 60).padStart(2, "0");
    return `${minutes}:${seconds}`;
  }

  function formatCountdown(totalSeconds) {
    const safeSeconds = Math.max(0, Number(totalSeconds || 0));
    const minutes = String(Math.floor(safeSeconds / 60)).padStart(2, "0");
    const seconds = String(safeSeconds % 60).padStart(2, "0");
    return `${minutes}:${seconds}`;
  }

  function getWallaDuration(points) {
    if (Number(points) === 600) return 30;
    if (Number(points) === 400) return 60;
    return 90;
  }

  function startActiveQuestionTimer(openedAt, question = null) {
    clearActiveQuestionTimer();

    if (!openedAt) {
      return;
    }

    const updateTimer = () => {
      const timerElement = document.getElementById("question-timer-value");
      if (!timerElement) {
        clearActiveQuestionTimer();
        return;
      }

      if (question?.questionType === "walla_kelma") {
        const remainingSeconds = getWallaRemainingSeconds(openedAt, question.points);
        timerElement.textContent = formatWallaSeconds(remainingSeconds);
        if (remainingSeconds <= 0) {
          clearActiveQuestionTimer();
        }
        return;
      }

      timerElement.textContent = formatElapsedTime(openedAt);
    };

    updateTimer();
    activeQuestionTimerInterval = window.setInterval(updateTimer, 1000);
  }

  async function ensureQuestionBankLoaded() {
    if (!questionBankPromise) {
      questionBankPromise = loadQuestionBank();
    }

    return questionBankPromise;
  }

  async function loadQuestionBank() {
    if (hasFeatureSelections()) {
      return loadFeatureQuestionBank();
    }

    throw new Error("ابدأ الجولة من صفحة اختيار الفئات حتى يتم تجهيز الأسئلة الحية أولًا.");
  }

  function getBoardSlotsForCategory(category) {
    const slots = [];
    const questions = [...category.questions];

    BOARD_SLOT_POINTS.forEach((points) => {
      const matchingIndex = questions.findIndex((question) => question.points === points);

      if (matchingIndex === -1) {
        slots.push({ points, question: null });
        return;
      }

      const [question] = questions.splice(matchingIndex, 1);
      slots.push({ points, question });
    });

    return slots;
  }

  function initStartPage() {
    const root = getRoot();
    const state = loadStateFromStorage();
    const visibleNames = state.teamNames.map((name, index) =>
      name === DEFAULT_TEAMS[index] ? "" : name
    );

    root.innerHTML = `
      <section class="page page--center">
        <div class="glass-card">
          <span class="hero-kicker">لوحة معلومات على طريقة المسابقات</span>
          <div class="hero-brand">${renderBrandLogo("brand-logo brand-logo--hero")}</div>
          <p class="page-subtitle">
            لعبة عربية بين فريقين فقط، مع لوحة نقاط على أسلوب Jeopardy وتجربة عرض حديثة.
          </p>

          <form id="start-form" class="stack" novalidate>
            <div class="field">
              <label class="label" for="team-one">اسم الفريق الأول</label>
              <input
                id="team-one"
                class="input"
                type="text"
                maxlength="30"
                placeholder="أدخل اسم الفريق الأول"
                value="${escapeHtml(visibleNames[0])}"
              />
            </div>

            <div class="field">
              <label class="label" for="team-two">اسم الفريق الثاني</label>
              <input
                id="team-two"
                class="input"
                type="text"
                maxlength="30"
                placeholder="أدخل اسم الفريق الثاني"
                value="${escapeHtml(visibleNames[1])}"
              />
            </div>

            <div class="button-row">
              <button class="button button--wide" type="submit">التالي</button>
            </div>
          </form>
        </div>
      </section>
    `;

    root.querySelector("#start-form").addEventListener("submit", (event) => {
      event.preventDefault();

      const teamOne = root.querySelector("#team-one").value.trim() || DEFAULT_TEAMS[0];
      const teamTwo = root.querySelector("#team-two").value.trim() || DEFAULT_TEAMS[1];

      saveStateToStorage({
        ...createInitialState(),
        teamNames: [teamOne, teamTwo],
      });

      goTo("categories.html");
    });
  }

  async function initWallaKelmaPage() {
    clearWallaTimer();
    const root = getRoot();
    const token = getQueryParam("token");
    const clientPrompt = decodeBase64UrlJson(getQueryParam("client_prompt"));

    if (clientPrompt && !token) {
      root.innerHTML = `
        <section class="page page--center">
          <div class="glass-card walla-card">
            <span class="hero-kicker">ولا كلمة | جهاز الممثل</span>
            <h1 class="page-title walla-title">${escapeHtml(clientPrompt.category || "ولا كلمة")}</h1>
            <p class="page-subtitle">لا تُظهر هذه الشاشة لبقية اللاعبين.</p>
            <div class="walla-secret-card">
              <div class="walla-secret-label">السر</div>
              <div class="walla-secret-value">${escapeHtml(
                clientPrompt.secret_value_ar || "غير متاح"
              )}</div>
              <div class="walla-secret-hint">${escapeHtml(
                clientPrompt.display_hint_ar || "مثّل السر دون نطقه."
              )}</div>
            </div>
          </div>
        </section>
      `;
      return;
    }

    if (token) {
      root.innerHTML = `
        <section class="page page--center">
          <div class="glass-card walla-card">
            <span class="hero-kicker">ولا كلمة | جهاز الممثل</span>
            <h1 class="page-title walla-title">جاري فتح السر...</h1>
          </div>
        </section>
      `;

      try {
        const response = await fetch(
          buildApiUrl(
            `/api/walla-kelma/session/${encodeURIComponent(token)}`,
            resolveWallaApiBaseUrl()
          ),
          {
            mode: "cors",
          }
        );
        const payload = await response.json();
        if (!response.ok) {
          throw new Error(payload?.details || "تعذر فتح جلسة ولا كلمة.");
        }

        root.innerHTML = `
          <section class="page page--center">
            <div class="glass-card walla-card">
              <span class="hero-kicker">ولا كلمة | جهاز الممثل</span>
              <h1 class="page-title walla-title">${escapeHtml(payload.category || "ولا كلمة")}</h1>
              <p class="page-subtitle">لا تُظهر هذه الشاشة لبقية اللاعبين.</p>
              <div class="walla-secret-card">
                <div class="walla-secret-label">السر</div>
                <div class="walla-secret-value">${escapeHtml(
                  payload.secret_value_ar || payload.secret_value || "غير متاح"
                )}</div>
                <div class="walla-secret-hint">${escapeHtml(
                  payload.display_hint_ar || "مثّل السر دون نطقه."
                )}</div>
              </div>
            </div>
          </section>
        `;
      } catch (error) {
        root.innerHTML = `
          <section class="page page--center">
            <div class="glass-card walla-card">
              <span class="hero-kicker">ولا كلمة</span>
              <h1 class="page-title walla-title">تعذر فتح السر</h1>
              <p class="page-subtitle">${escapeHtml(
                error instanceof Error ? error.message : "تعذر تحميل الجلسة الخاصة."
              )}</p>
            </div>
          </section>
        `;
      }
      return;
    }

    const featureSession = loadFeatureSessionFromStorage();
    const wallaSession = featureSession?.wallaKelmaSession || null;
    const promptBank = Array.isArray(wallaSession?.promptBank)
      ? wallaSession.promptBank
      : wallaSession?.token
      ? [wallaSession]
      : [];
    if (!promptBank.length) {
      goTo("categories.html");
      return;
    }

    const resolvePromptUrl = (prompt) =>
      prompt.qr_url ||
      (prompt.qr_path
        ? `${normalizeBaseUrl(prompt.api_base_url || getPublicBaseUrl())}${prompt.qr_path}`
        : `${normalizeBaseUrl(prompt.api_base_url || getPublicBaseUrl())}/walla-kelma.html?token=${encodeURIComponent(
            prompt.token
          )}`);

    function renderWallaPublic(activeIndex) {
      const activePrompt = promptBank[activeIndex] || promptBank[0];
      const secretUrl = resolvePromptUrl(activePrompt);
      const timeSeconds = getWallaDuration(activePrompt.points);
      const missingLanBaseWarning = !/^https?:\/\//.test(secretUrl)
        ? `<p class="page-subtitle" style="margin-top: 0.75rem;">تعذر تحديد رابط شبكة محلية صالح لرمز QR. افتح اللعبة بعنوان LAN أو اضبط المتغير <code>SEENJEEM_PUBLIC_BASE_URL</code>.</p>`
        : "";
      const localhostWarning = isLocalhostUrl(secretUrl)
        ? `<p class="page-subtitle" style="margin-top: 0.75rem;">إذا كنت ستستخدم جوالًا آخر للمسح، افتح اللعبة أولًا بعنوان الشبكة المحلية بدل 127.0.0.1 أو localhost.</p>`
        : "";

      root.innerHTML = `
        <section class="page page--center">
          <div class="glass-card walla-card">
            <span class="hero-kicker">ولا كلمة</span>
            <h1 class="page-title walla-title">${escapeHtml(
              wallaSession.category || activePrompt.category || "ولا كلمة"
            )}</h1>
            <p class="page-subtitle">
              امسح رمز QR بالجوال أو افتح الرابط الخاص على جهاز الممثل فقط، ثم استخدم التالي للانتقال إلى الجولة التالية.
            </p>

            <div class="sheet-topline walla-topline">
              <span class="sheet-chip">${escapeHtml(String(activePrompt.points || 200))} نقطة</span>
              <span class="sheet-chip sheet-chip--timer">
                <span>المدة</span>
                <strong id="walla-timer-value">${formatWallaSeconds(timeSeconds)}</strong>
              </span>
            </div>

            <div class="walla-public-card">
              <img src="${escapeHtml(buildQrImageUrl(secretUrl))}" alt="QR" class="walla-qr-image" />
            </div>
            ${missingLanBaseWarning}
            ${localhostWarning}

            <div class="button-row walla-controls">
              <button id="walla-next-button" class="button" type="button">
                ${activeIndex < promptBank.length - 1 ? "التالي" : "إنهاء ولا كلمة"}
              </button>
              <button id="walla-reset-timer-button" class="button-secondary" type="button">إعادة المؤقت</button>
            </div>
          </div>
        </section>
      `;

      const timerElement = root.querySelector("#walla-timer-value");
      let remaining = timeSeconds;
      const restartTimer = () => {
        clearWallaTimer();
        remaining = timeSeconds;
        if (timerElement) {
          timerElement.textContent = formatWallaSeconds(remaining);
        }
        wallaTimerInterval = window.setInterval(() => {
          remaining = Math.max(0, remaining - 1);
          if (timerElement) {
            timerElement.textContent = formatWallaSeconds(remaining);
          }
          if (remaining <= 0) {
            clearWallaTimer();
          }
        }, 1000);
      };
      restartTimer();

      root.querySelector("#walla-reset-timer-button").addEventListener("click", () => {
        restartTimer();
      });

      root.querySelector("#walla-next-button").addEventListener("click", async () => {
        clearWallaTimer();
        const nextIndex = activeIndex + 1;
        if (nextIndex < promptBank.length) {
          try {
            localStorage.setItem(
              FEATURE_STORAGE_KEY,
              JSON.stringify({
                ...(featureSession || {}),
                wallaKelmaSession: {
                  ...(wallaSession || {}),
                  promptBank,
                  activePromptIndex: nextIndex,
                },
              })
            );
          } catch (error) {
            // Ignore storage failures.
          }
          renderWallaPublic(nextIndex);
          return;
        }

        for (const prompt of promptBank) {
          if (!prompt?.token || String(prompt.token).startsWith("browser-")) {
            continue;
          }
          try {
            await fetch(
              buildApiUrl(
                "/api/walla-kelma/complete",
                prompt.api_base_url || getPublicBaseUrl()
              ),
              {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                mode: "cors",
                body: JSON.stringify({ token: prompt.token }),
              }
            );
          } catch (error) {
            // Completion is best-effort.
          }
        }

        try {
          localStorage.setItem(
            FEATURE_STORAGE_KEY,
            JSON.stringify({
              ...(featureSession || {}),
              wallaKelmaSession: null,
              selectedSubcategories: [],
              preparedQuestionBank: [],
            })
          );
        } catch (error) {
          // Ignore storage cleanup failures.
        }

        goTo("categories.html");
      });
    }

    renderWallaPublic(Number(wallaSession.activePromptIndex || 0));
  }

  async function initCategoriesPage() {
    await ensureQuestionBankLoaded();
    const root = getRoot();
    const state = loadStateFromStorage();

    root.innerHTML = renderCategoriesPage(state);

    root.querySelectorAll("[data-category-id]").forEach((button) => {
      button.addEventListener("click", () => {
        const latestState = loadStateFromStorage();
        const categoryId = button.dataset.categoryId;
        const selected = latestState.selectedCategoryIds.includes(categoryId)
          ? latestState.selectedCategoryIds.filter((id) => id !== categoryId)
          : [...latestState.selectedCategoryIds, categoryId];

        saveStateToStorage({
          ...latestState,
          selectedCategoryIds: selected,
        });

        initCategoriesPage();
      });
    });

    root.querySelector("#start-game-button").addEventListener("click", () => {
      const latestState = loadStateFromStorage();
      if (latestState.selectedCategoryIds.length < MIN_CATEGORIES) {
        return;
      }

      saveStateToStorage(resetBoardProgress(latestState, true));
      goTo("board.html");
    });

    root.querySelector("#back-home-button").addEventListener("click", () => {
      goTo("index.html");
    });
  }

  function renderCategoriesPage(state) {
    const selectedCount = state.selectedCategoryIds.length;
    const errorMessage =
      selectedCount < MIN_CATEGORIES
        ? `يجب اختيار ${MIN_CATEGORIES} فئات على الأقل لبدء اللعبة.`
        : `تم اختيار ${selectedCount} فئات. يمكنك بدء اللعبة الآن.`;

    return `
      <section class="page">
        <div class="page-topbar">
          <div>
            <div class="topbar-title">نون جيم</div>
            <div class="topbar-copy">اختيار الفئات</div>
          </div>
          <div class="status-inline">
            <span class="status-chip">${escapeHtml(state.teamNames[0])}</span>
            <span class="status-chip">${escapeHtml(state.teamNames[1])}</span>
          </div>
        </div>

        <div>
          <h1 class="page-title" style="font-size: clamp(1.9rem, 3vw, 3rem); margin-top: 0;">اختر الفئات</h1>
          <p class="page-subtitle" style="color: rgba(241, 245, 249, 0.84);">
            اختر أربع فئات على الأقل. كل فئة تحتوي على 6 خانات: 200، 200، 400، 400، 600، 600.
          </p>
        </div>

        <div class="panel">
          <div class="category-grid">
            ${QUESTION_BANK.map((category) => renderCategoryCard(category, state)).join("")}
          </div>
        </div>

        <div class="error-text" style="color: ${
          selectedCount < MIN_CATEGORIES ? "#fecaca" : "#bbf7d0"
        };">${escapeHtml(errorMessage)}</div>

        <div class="status-inline">
          <span class="status-chip">مصدر الأسئلة: ${escapeHtml(QUESTION_SOURCE_LABEL)}</span>
          ${
            QUESTION_SOURCE_ERROR
              ? `<span class="status-chip">سبب التعذر: ${escapeHtml(QUESTION_SOURCE_ERROR)}</span>`
              : ""
          }
        </div>

        <div class="button-row">
          <button
            id="start-game-button"
            class="button button--wide"
            type="button"
            ${selectedCount < MIN_CATEGORIES ? "disabled" : ""}
          >
            ابدأ اللعبة
          </button>
          <button id="back-home-button" class="button-ghost" type="button">العودة إلى البداية</button>
        </div>
      </section>
    `;
  }

  function renderCategoryCard(category, state) {
    const isSelected = state.selectedCategoryIds.includes(category.id);
    const categorySlots = category.questions.length;

    return `
      <button
        type="button"
        class="category-card ${isSelected ? "is-selected" : ""}"
        data-category-id="${category.id}"
        aria-pressed="${isSelected}"
      >
        <span class="category-text">
          <span class="category-head">
            <span class="category-name">${escapeHtml(category.name)}</span>
            ${isSelected ? '<span class="tick">✓</span>' : ""}
          </span>
          <p>${escapeHtml(category.description)}</p>
          <span class="category-meta">${categorySlots} خانات نقاط جاهزة</span>
        </span>
        <span class="category-icon" aria-hidden="true">${category.icon}</span>
      </button>
    `;
  }

  async function initBoardPage() {
    try {
      await ensureQuestionBankLoaded();
    } catch (error) {
      QUESTION_SOURCE_ERROR = error instanceof Error ? error.message : String(error);
      window.alert("تعذر تجهيز أسئلة الـ API لهذه اللوحة. اختر الفرعيات مرة أخرى.");
      goTo("categories.html");
      return;
    }
    clearActiveQuestionTimer();
    const state = loadStateFromStorage();
    const activeQuestion = state.activeQuestionId ? getQuestionById(state.activeQuestionId) : null;
    if (!state.selectedCategoryIds.length) {
      goTo("categories.html");
      return;
    }

    const selectedCategories = getSelectedCategories(state);
    if (!selectedCategories.length) {
      goTo("categories.html");
      return;
    }

    if (checkGameEnd(state) && !state.activeQuestionId) {
      goTo("results.html");
      return;
    }

    const root = getRoot();
    root.innerHTML = renderBoardPage(state);

    root.querySelectorAll("[data-question-id]").forEach((button) => {
      button.addEventListener("click", () => {
        const latestState = loadStateFromStorage();
        const questionId = button.dataset.questionId;

        if (
          latestState.usedQuestionIds.includes(questionId) ||
          latestState.activeQuestionId
        ) {
          return;
        }

        const question = getQuestionById(questionId);
        const isWallaQuestion = question?.questionType === "walla_kelma";

        saveStateToStorage({
          ...latestState,
          activeQuestionId: questionId,
          activeQuestionOpenedAt: isWallaQuestion ? null : Date.now(),
          activeQuestionView: "prompt",
          activeQuestionRevealed: false,
          activeQuestionResolved: false,
          lastFeedback: null,
        });

        initBoardPage();
      });
    });

    const revealButton = root.querySelector("#reveal-answer-button");
    if (revealButton) {
      revealButton.addEventListener("click", revealAnswer);
    }

    const resetQuestionTimerButton = root.querySelector("#reset-question-timer-button");
    if (resetQuestionTimerButton) {
      resetQuestionTimerButton.addEventListener("click", () => {
        const latestState = loadStateFromStorage();
        if (!latestState.activeQuestionId) {
          return;
        }
        saveStateToStorage({
          ...latestState,
          activeQuestionOpenedAt: Date.now(),
          activeQuestionView: "timer",
        });
        initBoardPage();
      });
    }

    root.querySelectorAll("[data-question-view]").forEach((button) => {
      button.addEventListener("click", () => {
        const nextView = button.dataset.questionView;
        if (!["prompt", "timer", "answer"].includes(nextView)) {
          return;
        }

        const latestState = loadStateFromStorage();
        if (!latestState.activeQuestionId) {
          return;
        }

        saveStateToStorage({
          ...latestState,
          activeQuestionView: nextView,
        });
        initBoardPage();
      });
    });

    root.querySelectorAll("[data-award-team]").forEach((button) => {
      button.addEventListener("click", () => {
        const teamValue = button.dataset.awardTeam;
        awardPoints(teamValue === "none" ? null : Number(teamValue));
      });
    });

    root.querySelectorAll("[data-score-adjust-team]").forEach((button) => {
      button.addEventListener("click", () => {
        adjustTeamScore(
          Number(button.dataset.scoreAdjustTeam),
          Number(button.dataset.scoreAdjustDelta)
        );
      });
    });

    const backButton = root.querySelector("#back-to-board-button");
    if (backButton) {
      backButton.addEventListener("click", closeQuestionAndContinue);
    }

    if (activeQuestion && state.activeQuestionOpenedAt && !state.activeQuestionRevealed) {
      startActiveQuestionTimer(state.activeQuestionOpenedAt, activeQuestion);
    }
  }

  function renderBoardPage(state) {
    const selectedCategories = getSelectedCategories(state);
    const categoryRows = chunkIntoRows(selectedCategories, 3);
    const activeQuestion = state.activeQuestionId ? getQuestionById(state.activeQuestionId) : null;

    return `
      <section class="page">
        <header class="board-header">
          <div class="board-title">${renderBrandLogo("brand-logo brand-logo--board")}</div>

          <div class="scoreline">
            ${state.teamNames
              .map(
                (teamName, index) => `
                  <div class="team-score ${index === state.currentTeamIndex ? "is-active" : ""}">
                    <div class="team-score__main">
                      <div class="team-name">${escapeHtml(teamName)}</div>
                      <div class="team-points">${state.scores[index]} نقطة</div>
                    </div>
                    <div class="team-score__controls">
                      <button
                        class="team-score__adjust team-score__adjust--plus"
                        type="button"
                        data-score-adjust-team="${index}"
                        data-score-adjust-delta="100"
                        aria-label="زيادة 100 نقطة لـ ${escapeHtml(teamName)}"
                      >
                        +
                      </button>
                      <button
                        class="team-score__adjust team-score__adjust--minus"
                        type="button"
                        data-score-adjust-team="${index}"
                        data-score-adjust-delta="-100"
                        aria-label="خصم 100 نقطة من ${escapeHtml(teamName)}"
                      >
                        −
                      </button>
                    </div>
                  </div>
                `
              )
              .join("")}
          </div>

          <div class="turn-box">
            <div class="turn-label">صاحب الدور في اختيار الخانة</div>
            <div class="turn-team">${escapeHtml(state.teamNames[state.currentTeamIndex])}</div>
          </div>
        </header>

        <div class="board-stage">
          <div class="board-frame">
            <div class="board-scroll">
              <div class="board-grid">
                ${categoryRows
                  .map(
                    (row) => `
                      <div class="board-columns board-columns--compact board-columns--row" style="grid-template-columns: repeat(${row.length}, minmax(180px, 1fr));">
                        ${row.map((category) => renderBoardColumn(category, state)).join("")}
                      </div>
                    `
                  )
                  .join("")}
              </div>
            </div>
          </div>
        </div>

        ${activeQuestion ? renderQuestionOverlay(activeQuestion, state) : ""}
      </section>
    `;
  }

  function renderBoardColumn(category, state) {
    const slots = getBoardSlotsForCategory(category);
    const leftSlots = [slots[0], slots[2], slots[4]];
    const rightSlots = [slots[1], slots[3], slots[5]];
    const categoryFlag = category.flagCode ? flagCodeToEmoji(category.flagCode) : "";

    return `
      <div class="board-column board-column--poster">
        <div class="board-column-title">${escapeHtml(category.name)}</div>
        <div class="board-poster-card">
          <div class="board-poster-side">
            ${leftSlots.map((slot) => renderBoardCell(slot, state)).join("")}
          </div>
          <div class="board-poster-visual">
            <span class="board-poster-visual__glow"></span>
            <span class="board-poster-visual__icon" aria-hidden="true">${escapeHtml(
              category.icon || "✨"
            )}</span>
            ${
              categoryFlag
                ? `<span class="board-poster-visual__flag" aria-hidden="true">${categoryFlag}</span>`
                : ""
            }
          </div>
          <div class="board-poster-side">
            ${rightSlots.map((slot) => renderBoardCell(slot, state)).join("")}
          </div>
        </div>
      </div>
    `;
  }

  function renderBoardCell(slot, state) {
    if (!slot.question) {
      return `
        <button type="button" class="board-cell is-used" disabled>
          ${slot.points}
        </button>
      `;
    }

    const question = slot.question;
    const isUsed = state.usedQuestionIds.includes(question.id);
    const isActiveQuestion = state.activeQuestionId === question.id;

    return `
      <button
        type="button"
        class="board-cell ${isUsed ? "is-used" : ""} ${isActiveQuestion ? "is-active-question" : ""}"
        data-question-id="${question.id}"
        ${isUsed ? "disabled" : ""}
      >
        ${isUsed ? "✓" : question.points}
      </button>
    `;
  }

  function renderQuestionOverlay(question, state) {
    const isWallaQuestion = question?.questionType === "walla_kelma";
    const isVisualRevealQuestion = !isWallaQuestion && question?.displayMode === "reveal_visual";
    const hasWallaTimerStarted = isWallaQuestion && Boolean(state.activeQuestionOpenedAt);
    const activeWallaView =
      isWallaQuestion && state.activeQuestionView === "timer" ? "timer" : "prompt";
    const isRevealed = state.activeQuestionRevealed;
    const isResolved = state.activeQuestionResolved;
    const buttonLabel = checkGameEnd(state) ? "عرض النتائج" : "رجوع إلى اللوحة";
    const nextTurnTeam = state.teamNames[state.currentTeamIndex];
    const questionText =
      typeof question?.text === "string" && question.text.trim() !== ""
        ? question.text
        : typeof question?.question === "string" && question.question.trim() !== ""
        ? question.question
        : "سؤال غير متاح.";
    const questionVisual =
      question?.visual &&
      question.visual.type === "qr" &&
      typeof question.visual.value === "string" &&
      question.visual.value.trim() !== ""
        ? `
          <div class="question-visual question-visual--image" aria-label="QR">
            <img src="${escapeHtml(buildQrImageUrl(question.visual.value))}" alt="QR" class="question-visual__image" />
          </div>
        `
        :
      question?.visual &&
      question.visual.type === "logo-image" &&
      (typeof question.visual.value === "string" || typeof question.visual.fallbackText === "string")
        ? `
          <div class="question-visual question-visual--logo" aria-label="الشعار أو العلامة">
            ${
              question.visual.value.trim() !== ""
                ? `<img src="${escapeHtml(question.visual.value)}" alt="${escapeHtml(
                    question.visual.fallbackText || "شعار علامة تجارية"
                  )}" class="question-visual__logo-image" />`
                : `<div class="question-visual__brand-text">${escapeHtml(
                    question.visual.fallbackText || "Brand"
                  )}</div>`
            }
          </div>
        `
        :
      question?.visual &&
      question.visual.type === "brand-text" &&
      typeof question.visual.value === "string" &&
      question.visual.value.trim() !== ""
        ? `
          <div class="question-visual question-visual--logo" aria-label="اسم العلامة">
            <div class="question-visual__brand-text">${escapeHtml(question.visual.value)}</div>
          </div>
        `
        :
      question?.visual &&
      (question.visual.type === "flag" || question.visual.type === "flag-image") &&
      typeof question.visual.value === "string" &&
      question.visual.value.trim() !== ""
        ? `
          <div class="question-visual ${question.visual.type === "flag-image" ? "question-visual--image" : "question-visual--flag"}" aria-label="العلم">
            ${
              question.visual.type === "flag-image"
                ? `<img src="${escapeHtml(question.visual.value)}" alt="العلم" class="question-visual__image" />`
                : escapeHtml(question.visual.value)
            }
          </div>
        `
        : "";
    const showWallaPrompt =
      isWallaQuestion && (!isRevealed ? activeWallaView === "prompt" : state.activeQuestionView === "prompt");
    const showWallaTimer =
      isWallaQuestion && (!isRevealed ? activeWallaView === "timer" : state.activeQuestionView === "timer");
    const showWallaAnswer = isWallaQuestion && isRevealed && state.activeQuestionView !== "prompt" && state.activeQuestionView !== "timer";
    const wallaTimerStage = showWallaTimer
      ? `
          <div class="walla-timer-stage" aria-live="polite">
            <div class="walla-timer-stage__label">الوقت المتبقي</div>
            <div class="walla-timer-stage__value" id="question-timer-value">${
              hasWallaTimerStarted
                ? formatWallaSeconds(
                    getWallaRemainingSeconds(state.activeQuestionOpenedAt, question.points)
                  )
                : formatWallaSeconds(getWallaDuration(question.points))
            }</div>
            <div class="walla-timer-stage__hint">
              ${hasWallaTimerStarted
                ? "يمكنك إعادة المؤقت أو الرجوع لمشاهدة رمز QR والسؤال في أي وقت."
                : "ابدأ المؤقت من هذه الشاشة ثم تابع الجولة."}
            </div>
          </div>
        `
      : "";
    const wallaAnswerCard = showWallaAnswer
      ? `
          <div class="reveal-card">
            <div class="reveal-label">جواب ولا كلمة</div>
            <div class="reveal-answer">${escapeHtml(getCorrectAnswerText(question))}</div>
          </div>
        `
      : "";

    return `
      <div class="overlay">
        <section class="question-sheet" aria-live="polite">
          <div class="sheet-topline">
            ${
              showWallaTimer
                ? `<span class="sheet-chip">${hasWallaTimerStarted ? "عرض المؤقت" : "تجهيز المؤقت"}</span>`
                : `
                  <span class="sheet-chip sheet-chip--timer">
                    <span>${isWallaQuestion ? (hasWallaTimerStarted ? "الوقت" : "المدة") : "الوقت"}</span>
                    <strong id="question-timer-value">${
                      isWallaQuestion
                        ? hasWallaTimerStarted
                          ? formatWallaSeconds(
                              getWallaRemainingSeconds(state.activeQuestionOpenedAt, question.points)
                            )
                          : formatWallaSeconds(getWallaDuration(question.points))
                        : formatElapsedTime(state.activeQuestionOpenedAt)
                    }</strong>
                  </span>
                `
            }
            <span class="sheet-chip">${question.points} نقطة</span>
          </div>

          ${showWallaTimer ? wallaTimerStage : showWallaAnswer ? wallaAnswerCard : questionVisual}
          ${showWallaTimer || showWallaAnswer || isVisualRevealQuestion ? "" : `<h2 class="question-title">${escapeHtml(questionText)}</h2>`}
          <p class="question-hint">
            ${
              !isRevealed
                ? isWallaQuestion
                  ? showWallaTimer
                    ? hasWallaTimerStarted
                      ? `المؤقت يعمل الآن. يمكنك إعادة المؤقت أو الرجوع إلى عرض رمز QR والسؤال، ثم اضغط على زر التالي لعرض الجواب عند انتهاء المحاولة.`
                      : `جاري بدء المؤقت...`
                    : hasWallaTimerStarted
                    ? `يمكنك عرض رمز QR والسؤال مرة أخرى بينما المؤقت مستمر، أو الانتقال إلى شاشة المؤقت من جديد.`
                    : `امسح رمز QR على جهاز الممثل فقط، ثم اضغط على زر التالي للانتقال إلى شاشة المؤقت.`
                  : isVisualRevealQuestion
                  ? `اعرض العنصر البصري فقط الآن، ثم اضغط على زر إظهار الإجابة بعد انتهاء المحاولة.`
                  : `اطرح السؤال الآن، ثم اضغط على زر إظهار الإجابة بعد انتهاء المحاولة.`
                : !isResolved
                ? isWallaQuestion
                  ? showWallaAnswer
                    ? `هذا هو الجواب الذي كان الممثل يمثّله. يمكنك الرجوع إلى رمز QR أو شاشة المؤقت قبل احتساب النقاط إذا احتجت ذلك.`
                    : showWallaPrompt
                    ? `الجواب ظاهر ويمكنك الرجوع إليه في أي وقت.`
                    : `يمكنك الرجوع إلى الجواب أو رمز QR أو المؤقت قبل احتساب النقاط.`
                  : `ظهرت الإجابة. اختر الفريق الذي سيحصل على النقطة، أو حدّد أن لا أحد حصل عليها.`
                : `تم إنهاء هذا السؤال. الدور التالي في اختيار الخانة هو ${escapeHtml(nextTurnTeam)}.`
            }
          </p>

          ${
            !isRevealed
              ? `
                <div class="button-row">
                  ${
                    isWallaQuestion
                      ? showWallaTimer
                        ? `
                          <button id="reveal-answer-button" class="button" type="button">التالي</button>
                          <button id="reset-question-timer-button" class="button-secondary" type="button">إعادة المؤقت</button>
                          <button class="button-secondary" type="button" data-question-view="prompt">الرجوع إلى QR</button>
                        `
                        : `
                          <button id="reveal-answer-button" class="button" type="button">التالي</button>
                          ${
                            hasWallaTimerStarted
                              ? '<button class="button-secondary" type="button" data-question-view="timer">عرض المؤقت</button>'
                              : ""
                          }
                        `
                      : '<button id="reveal-answer-button" class="button" type="button">إظهار الإجابة</button>'
                  }
                </div>
              `
              : `
                ${
                  isWallaQuestion
                    ? `
                      ${showWallaAnswer ? "" : wallaAnswerCard}
                      <div class="button-row">
                        <button class="button-secondary" type="button" data-question-view="answer">عرض الجواب</button>
                        <button class="button-secondary" type="button" data-question-view="prompt">الرجوع إلى QR</button>
                        <button class="button-secondary" type="button" data-question-view="timer">الرجوع إلى المؤقت</button>
                      </div>
                    `
                    : `
                      <div class="reveal-card">
                        <div class="reveal-label">الإجابة الصحيحة</div>
                        <div class="reveal-answer">${escapeHtml(getCorrectAnswerText(question))}</div>
                      </div>
                    `
                }
              `
          }

          ${
            isRevealed && !isResolved
              ? `
                <div class="award-grid">
                  <button class="award-button" type="button" data-award-team="0">
                    احتساب ${question.points} لـ ${escapeHtml(state.teamNames[0])}
                  </button>
                  <button class="award-button" type="button" data-award-team="1">
                    احتساب ${question.points} لـ ${escapeHtml(state.teamNames[1])}
                  </button>
                  <button class="award-button award-button--muted" type="button" data-award-team="none">
                    لا أحد يحصل على النقاط
                  </button>
                </div>
              `
              : ""
          }

          ${
            state.lastFeedback
              ? `
                <div class="feedback ${state.lastFeedback.type === "warning" ? "is-warning" : "is-success"}">
                  <strong>${state.lastFeedback.type === "warning" ? "تم تسجيل السؤال بدون نقاط" : "تم احتساب النقاط"}</strong>
                  <p>${escapeHtml(state.lastFeedback.message)}</p>
                  <div class="button-row" style="margin-top: 0;">
                    <button id="back-to-board-button" class="button" type="button">${buttonLabel}</button>
                  </div>
                </div>
              `
              : ""
          }
        </section>
      </div>
    `;
  }

  function revealAnswer() {
    const state = loadStateFromStorage();
    if (!state.activeQuestionId || state.activeQuestionRevealed) {
      return;
    }

    const question = getQuestionById(state.activeQuestionId);
    if (question?.questionType === "walla_kelma" && state.activeQuestionView !== "timer") {
      saveStateToStorage({
        ...state,
        activeQuestionOpenedAt: state.activeQuestionOpenedAt || Date.now(),
        activeQuestionView: "timer",
      });
      initBoardPage();
      return;
    }

    if (question?.questionType === "walla_kelma") {
      clearActiveQuestionTimer();
      saveStateToStorage({
        ...state,
        activeQuestionRevealed: true,
        activeQuestionView: "answer",
      });
      initBoardPage();
      return;
    }

    saveStateToStorage({
      ...state,
      activeQuestionRevealed: true,
    });

    initBoardPage();
  }

  function awardPoints(teamIndex) {
    const state = loadStateFromStorage();
    if (!state.activeQuestionId || !state.activeQuestionRevealed || state.activeQuestionResolved) {
      return;
    }

    const question = getQuestionById(state.activeQuestionId);
    if (!question) {
      return;
    }

    const nextScores = [...state.scores];
    let feedbackMessage = "";
    let feedbackType = "success";

    if (teamIndex === 0 || teamIndex === 1) {
      nextScores[teamIndex] += question.points;
      feedbackMessage = `تم احتساب ${question.points} نقطة لصالح ${state.teamNames[teamIndex]}. الدور القادم في اختيار الخانة سيكون على ${state.teamNames[(state.currentTeamIndex + 1) % 2]}.`;
    } else {
      feedbackType = "warning";
      feedbackMessage = `لم يحصل أي فريق على نقاط في هذا السؤال. الدور القادم في اختيار الخانة سيكون على ${state.teamNames[(state.currentTeamIndex + 1) % 2]}.`;
    }

    saveStateToStorage({
      ...state,
      scores: nextScores,
      usedQuestionIds: [...new Set([...state.usedQuestionIds, question.id])],
      activeQuestionResolved: true,
      lastFeedback: {
        type: feedbackType,
        message: feedbackMessage,
      },
      currentTeamIndex: (state.currentTeamIndex + 1) % 2,
    });

    initBoardPage();
  }

  function adjustTeamScore(teamIndex, delta) {
    if (teamIndex !== 0 && teamIndex !== 1) {
      return;
    }

    if (![100, -100].includes(delta)) {
      return;
    }

    const state = loadStateFromStorage();
    const nextScores = [...state.scores];
    nextScores[teamIndex] += delta;

    saveStateToStorage({
      ...state,
      scores: nextScores,
      lastFeedback: {
        type: delta > 0 ? "success" : "warning",
        message:
          delta > 0
            ? `تمت إضافة 100 نقطة إلى ${state.teamNames[teamIndex]}.`
            : `تم خصم 100 نقطة من ${state.teamNames[teamIndex]}.`,
      },
    });

    initBoardPage();
  }

  function closeQuestionAndContinue() {
    const state = clearActiveQuestionState(loadStateFromStorage());
    saveStateToStorage(state);

    if (checkGameEnd(state)) {
      goTo("results.html");
      return;
    }

    initBoardPage();
  }

  async function initResultsPage() {
    try {
      await ensureQuestionBankLoaded();
    } catch (error) {
      goTo("categories.html");
      return;
    }
    const state = loadStateFromStorage();
    if (!state.selectedCategoryIds.length) {
      goTo("categories.html");
      return;
    }

    const selectedCategories = getSelectedCategories(state);
    if (!selectedCategories.length) {
      goTo("categories.html");
      return;
    }

    if (!checkGameEnd(state)) {
      goTo("board.html");
      return;
    }

    const root = getRoot();
    const [teamOneScore, teamTwoScore] = state.scores;
    const winnerIndex =
      teamOneScore === teamTwoScore ? null : teamOneScore > teamTwoScore ? 0 : 1;
    const margin = Math.abs(teamOneScore - teamTwoScore);
    const title =
      winnerIndex === null
        ? "تعادل مثير!"
        : `فاز ${escapeHtml(state.teamNames[winnerIndex])}!`;

    root.innerHTML = `
      <section class="page page--center">
        <div class="result-card">
          <div class="result-content">
            <div>
              <span class="hero-kicker">نهاية المباراة</span>
              <h1 class="result-title">${title}</h1>
              <p class="result-copy">${escapeHtml(getResultsMessage(winnerIndex, margin))}</p>
            </div>

            <div class="result-grid">
              ${state.teamNames
                .map(
                  (teamName, index) => `
                    <div class="result-team-card ${winnerIndex === index ? "is-winner" : ""}">
                      ${winnerIndex === index ? '<span class="winner-label">الفائز</span>' : ""}
                      <div class="result-team-name">${escapeHtml(teamName)}</div>
                      <div class="result-team-score">${state.scores[index]}</div>
                      <div class="page-subtitle" style="margin-top: 0.15rem;">نقطة</div>
                    </div>
                  `
                )
                .join("")}
            </div>

            <div class="button-row">
              <button id="play-again-button" class="button" type="button">لعب مباراة جديدة</button>
              <button id="reset-button" class="button-secondary" type="button">العودة إلى البداية</button>
            </div>
          </div>
        </div>
      </section>
    `;

    root.querySelector("#play-again-button").addEventListener("click", () => {
      const latestState = loadStateFromStorage();
      saveStateToStorage(resetBoardProgress(latestState, true));
      goTo("categories.html");
    });

    root.querySelector("#reset-button").addEventListener("click", () => {
      resetEverything();
      goTo("index.html");
    });
  }

  function getResultsMessage(winnerIndex, margin) {
    if (winnerIndex === null) {
      return "تعادل! يبدو أنكم تحتاجون إلى جولة فاصلة إضافية لحسم المباراة.";
    }

    if (margin >= 1200) {
      return "فوز ساحق! الفريق الفائز سيطر على اللوحة وحسم أغلب الأسئلة الكبيرة.";
    }

    if (margin >= 400) {
      return "أفضلية واضحة في اللحظات الحاسمة، خصوصاً في الأسئلة ذات النقاط الأعلى.";
    }

    return "مباراة متقاربة جداً، والحسم جاء بفارق صغير حتى آخر الخانات.";
  }

  function cloneQuestionBank() {
    return QUESTION_BANK.map((category) => ({
      ...category,
      questions: category.questions.map((question) => ({ ...question })),
    }));
  }

  function listCategories() {
    return QUESTION_BANK.map((category) => ({
      id: category.id,
      name: category.name,
      questionCount: category.questions.length,
      pointValues: category.questions.map((question) => question.points),
      source: QUESTION_SOURCE_LABEL,
    }));
  }

  function listQuestions(categoryId) {
    const category = getCategoryById(categoryId);
    if (!category) {
      return [];
    }

    return category.questions.map((question) => ({
      id: question.id,
      points: question.points,
      text: question.text,
      answer: question.answer,
      displayMode: question.displayMode,
    }));
  }

  async function reloadPreparedQuestions() {
    questionBankPromise = null;
    return ensureQuestionBankLoaded();
  }

  function getImeSupport() {
    const probe = document.createElement("input");
    const standardContext = "inputMethodContext" in probe;
    const webkitContext = "webkitInputMethodContext" in probe;

    return {
      imeApiSpecAvailable: standardContext || webkitContext,
      inputMethodContext: standardContext,
      webkitInputMethodContext: webkitContext,
      compositionEvents: {
        compositionstart: "oncompositionstart" in probe,
        compositionupdate: "oncompositionupdate" in probe,
        compositionend: "oncompositionend" in probe,
      },
      inputEvents: {
        beforeinput: "onbeforeinput" in probe,
        input: "oninput" in probe,
      },
    };
  }

  function attachImeLogger(selector = "input, textarea, [contenteditable='true']") {
    const nodes = Array.from(document.querySelectorAll(selector));
    const eventNames = [
      "compositionstart",
      "compositionupdate",
      "compositionend",
      "beforeinput",
      "input",
    ];

    nodes.forEach((node, nodeIndex) => {
      eventNames.forEach((eventName) => {
        node.addEventListener(eventName, (event) => {
          console.log("[IME DEBUG]", {
            nodeIndex,
            selector,
            event: eventName,
            value: "value" in node ? node.value : node.textContent,
            data: event.data ?? null,
            inputType: event.inputType ?? null,
            isComposing: event.isComposing ?? null,
          });
        });
      });

      const context = node.inputMethodContext || node.webkitInputMethodContext || null;
      if (context) {
        ["candidatewindowshow", "candidatewindowupdate", "candidatewindowhide"].forEach(
          (eventName) => {
            context.addEventListener(eventName, () => {
              console.log("[INPUT METHOD DEBUG]", {
                nodeIndex,
                event: eventName,
                rect:
                  typeof context.getCandidateWindowRect === "function"
                    ? context.getCandidateWindowRect()
                    : null,
                alternatives:
                  typeof context.getCompositionAlternatives === "function"
                    ? context.getCompositionAlternatives()
                    : null,
              });
            });
          }
        );
      }
    });

    return {
      attachedCount: nodes.length,
      selector,
      support: getImeSupport(),
    };
  }

  return {
    initStartPage,
    initWallaKelmaPage,
    initCategoriesPage,
    initBoardPage,
    initResultsPage,
    loadStateFromStorage,
    saveStateToStorage,
    debug: {
      getQuestionBank: cloneQuestionBank,
      listCategories,
      listQuestions,
      getState: loadStateFromStorage,
      getQuestionSource: () => ({
        label: QUESTION_SOURCE_LABEL,
        error: QUESTION_SOURCE_ERROR,
        mode: LIVE_QUESTION_SOURCE_CONFIG.mode,
        endpoints: { ...LIVE_QUESTION_SOURCE_CONFIG },
      }),
      reloadPreparedQuestions,
      imeSupport: getImeSupport,
      attachImeLogger,
    },
  };
})();

window.SeenJeemGame = SeenJeemGame;
window.SeenJeemDebug = SeenJeemGame.debug;
