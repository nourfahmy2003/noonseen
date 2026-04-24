(function () {
  // Purpose: load typed catalog/source-map files into the browser runtime
  // while leaving live question preparation to the backend only.
  const STORAGE_KEY = "quiz-feature-session";
  const BACKEND_BASE_STORAGE_KEY = "seen-jeem-backend-base";
  const PUBLIC_BASE_STORAGE_KEY = "seen-jeem-public-base";
  const iconMap = {
    "image-search": "🖼️",
    focus: "🎯",
    riddle: "🧩",
    lightbulb: "💡",
    "quote-puzzle": "🗨️",
    draw: "✏️",
    palette: "🎨",
    "reverse-word": "🔁",
    "foreign-guess": "🎬",
    "football-guess": "⚽",
    "proverb-guess": "📜",
    "general-guess": "❓",
    "no-word": "🤐",
    "anime-guess": "🌀",
    "wrestling-guess": "🥊",
    "football-letter": "⚽",
    "music-letter": "🎵",
    "islamic-letter": "🕌",
    letters: "🔤",
    "moving-letters": "🔡",
    "anime-letter": "🗾",
    currency: "💰",
    aviation: "✈️",
    travel: "🧳",
    "country-capital": "🌍",
    geography: "🗺️",
    "old-flag": "🏴",
    flag: "🚩",
    leaders: "👑",
    "identify-country": "📍",
    uk: "🇬🇧",
    languages: "🗣️",
    anthem: "🎼",
    "world-war": "⚔️",
    maps: "🧭",
    capitals: "🏙️",
    companions: "🕌",
    prophets: "🌙",
    seerah: "🕋",
    quran: "📖",
    "islamic-general": "☪️",
    nasheed: "🎤",
    reciter: "🔊",
    "juz-tabarak": "📘",
    "juz-amma": "📗",
    "quran-meanings": "📜",
    hadith: "🪶",
    technology: "💻",
    "general-knowledge": "🧠",
    history: "🏛️",
    poetry: "✒️",
    "language-literature": "📚",
    shopping: "🛒",
    products: "🥤",
    "global-logos": "🌐",
    logos: "🏷️",
    animals: "🦁",
    medicine: "🩺",
    dentistry: "🦷",
    "arabic-perfumes": "🪔",
    "global-perfumes": "🧴",
  };

  function stripTypeBlocks(source) {
    let text = source;
    text = text.replace(/^import\s+type\s+.*$/gm, "");
    text = text.replace(/export\s+type\s+\w+\s*=\s*\{[\s\S]*?\n};/gm, "");
    text = text.replace(/export\s+type\s+\w+\s*=\s*[\s\S]*?;/gm, "");
    return text;
  }

  function transpileCatalogSource(source) {
    let text = stripTypeBlocks(source);

    text = text.replace(
      /const createCard = \(card:[^)]+\):[^=]+=> card;/,
      "const createCard = (card) => card;"
    );
    text = text.replace(
      /const createSection = \(section:[^)]+\):[^=]+=> section;/,
      "const createSection = (section) => section;"
    );
    text = text.replace(
      /export const categoryCatalog:\s*[^=]+=/,
      "const categoryCatalog ="
    );
    text = text.replace(/ as Record<string,[^;]+;/g, ";");
    text = text.replace(/export const /g, "const ");

    return `${text}\nreturn { categoryCatalog, categoryCatalogById, subcategoryCatalogById };`;
  }

  function transpileSourceMap(source) {
    let text = stripTypeBlocks(source);
    text = text.replace(
      /export const apiSourceMap:\s*[^=]+=/,
      "const apiSourceMap ="
    );
    text = text.replace(/export const /g, "const ");
    return `${text}\nreturn { apiSourceMap };`;
  }

  async function loadTypeScriptValue(filePath, transpile) {
    const response = await fetch(filePath);
    if (!response.ok) {
      throw new Error(`Failed to load ${filePath}`);
    }

    const source = await response.text();
    const executable = transpile(source);
    return new Function(executable)();
  }

  async function loadCatalogRuntime() {
    return loadTypeScriptValue(
      "./quiz-feature/config/categoryCatalog.ts?v=20260419h",
      transpileCatalogSource
    );
  }

  async function loadSourceMapRuntime() {
    return loadTypeScriptValue(
      "./quiz-feature/config/sourceMap.ts?v=20260419h",
      transpileSourceMap
    );
  }

  function readSession() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || "null") || {
        categoryId: null,
        subcategoryId: null,
        difficulty: null,
        amount: null,
        questions: [],
      };
    } catch (error) {
      return {
        categoryId: null,
        subcategoryId: null,
        difficulty: null,
        amount: null,
        questions: [],
      };
    }
  }

  function writeSession(partialState) {
    const nextState = {
      ...readSession(),
      ...partialState,
    };

    localStorage.setItem(STORAGE_KEY, JSON.stringify(nextState));
    return nextState;
  }

  function getPlaceholderIcon(imageKey, iconKey) {
    if (iconKey && iconMap[iconKey]) return iconMap[iconKey];
    if ((imageKey || "").includes("quran")) return "📖";
    if ((imageKey || "").includes("flag")) return "🚩";
    if ((imageKey || "").includes("football")) return "⚽";
    return "✨";
  }

  function getVisualAccent(seed = "") {
    const palette = ["#7FB7FF", "#8FD0F6", "#A6C7FF", "#9ED7D3", "#A6D0F5", "#B3C2FF"];
    let hash = 0;
    for (let index = 0; index < seed.length; index += 1) {
      hash = (hash + seed.charCodeAt(index) * (index + 1)) % palette.length;
    }
    return palette[hash];
  }

  function flagCodeToEmoji(flagCode) {
    const normalized = (flagCode || "").trim().toUpperCase();
    if (!/^[A-Z]{2}$/.test(normalized)) return "🏳️";
    return String.fromCodePoint(
      ...normalized.split("").map((char) => 127397 + char.charCodeAt(0))
    );
  }

  function getBackendBaseCandidates() {
    const candidates = [];
    const origin = window.location.origin;
    if (origin && origin !== "null" && !candidates.includes(origin)) {
      candidates.push(origin);
    }

    const hostname = window.location.hostname;
    const protocol = window.location.protocol || "http:";
    if (hostname) {
      const port8000Origin = `${protocol}//${hostname}:8000`;
      if (!candidates.includes(port8000Origin)) {
        candidates.push(port8000Origin);
      }
    }

    return candidates;
  }

  function normalizeBaseUrl(value) {
    return String(value || "").trim().replace(/\/$/, "");
  }

  function isLoopbackBaseUrl(value) {
    try {
      const url = new URL(value, window.location.origin);
      return ["127.0.0.1", "localhost"].includes(url.hostname);
    } catch (error) {
      return false;
    }
  }

  function rememberPublicBaseUrl(value) {
    const normalized = normalizeBaseUrl(value);
    if (!normalized) return;
    try {
      sessionStorage.setItem(PUBLIC_BASE_STORAGE_KEY, normalized);
    } catch (error) {
      // Ignore storage access failures.
    }
  }

  function resolvePublicBaseUrl() {
    try {
      const cached = normalizeBaseUrl(sessionStorage.getItem(PUBLIC_BASE_STORAGE_KEY));
      if (cached) {
        return cached;
      }
    } catch (error) {
      // Ignore storage access failures.
    }

    const origin = normalizeBaseUrl(window.location.origin);
    if (origin && origin !== "null" && !isLoopbackBaseUrl(origin)) {
      return origin;
    }

    try {
      const cachedBackend = normalizeBaseUrl(sessionStorage.getItem(BACKEND_BASE_STORAGE_KEY));
      if (cachedBackend && !isLoopbackBaseUrl(cachedBackend)) {
        return cachedBackend;
      }
    } catch (error) {
      // Ignore storage access failures.
    }

    return "";
  }

  async function probeBackendBase(baseUrl) {
    const response = await fetch(`${baseUrl}/api/quiz/live-subcategories`, {
      method: "GET",
      mode: "cors",
    });
    if (!response.ok) {
      throw new Error(`Backend probe failed: ${baseUrl}`);
    }
    const payload = await response.json();
    if (!Array.isArray(payload?.subcategoryIds)) {
      throw new Error(`Backend probe returned invalid payload: ${baseUrl}`);
    }
    return {
      backendBaseUrl: normalizeBaseUrl(baseUrl),
      publicBaseUrl: normalizeBaseUrl(payload?.publicBaseUrl),
    };
  }

  async function resolveBackendBase() {
    try {
      const cached = sessionStorage.getItem(BACKEND_BASE_STORAGE_KEY);
      if (cached) {
        try {
          const resolved = await probeBackendBase(cached);
          if (resolved.publicBaseUrl) {
            rememberPublicBaseUrl(resolved.publicBaseUrl);
          }
          return resolved.backendBaseUrl;
        } catch (error) {
          try {
            sessionStorage.removeItem(BACKEND_BASE_STORAGE_KEY);
          } catch (storageError) {
            // Ignore storage failures.
          }
        }
      }
    } catch (error) {
      // Ignore storage access failures and continue probing.
    }

    const candidates = getBackendBaseCandidates();
    for (const candidate of candidates) {
      try {
        const resolved = await probeBackendBase(candidate);
        try {
          sessionStorage.setItem(BACKEND_BASE_STORAGE_KEY, resolved.backendBaseUrl);
        } catch (error) {
          // Ignore storage access failures.
        }
        if (resolved.publicBaseUrl) {
          rememberPublicBaseUrl(resolved.publicBaseUrl);
        }
        return resolved.backendBaseUrl;
      } catch (error) {
        // Try the next candidate.
      }
    }

    throw new Error("No live backend could be reached.");
  }

  async function apiFetch(path, options = {}) {
    const baseUrl = await resolveBackendBase();
    const normalizedPath = path.startsWith("/") ? path : `/${path}`;
    const nextOptions = { ...options, mode: "cors" };
    return fetch(`${baseUrl}${normalizedPath}`, nextOptions);
  }

  window.QuizCategorySectionsRuntime = {
    ...(window.QuizCategorySectionsRuntime || {}),
    loadCatalogRuntime,
    loadSourceMapRuntime,
    resolveBackendBase,
    apiFetch,
    resolvePublicBaseUrl,
    readSession,
    writeSession,
    getPlaceholderIcon,
    getVisualAccent,
    flagCodeToEmoji,
  };
})();
