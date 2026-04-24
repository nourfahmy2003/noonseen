(function () {
  // Purpose: keep the detached browser-only match-prep runtime readable while
  // the active selection flow uses backend preparation instead.
  const OPEN_TRIVIA_API_BASE = "https://opentdb.com/api.php";
  const ALQURAN_CLOUD_API_BASE = "https://api.alquran.cloud/v1";
  const DEFAULT_PUBLIC_BASE_URL = window.location.origin || "";
  const BOARD_SLOT_POINTS = [200, 200, 400, 400, 600, 600];
  const openTriviaCache = new Map();
  const OPEN_TRIVIA_CATEGORY_IDS = {
    "general-technology": 18,
    "general-general-knowledge": 9,
    "general-history": 23,
    "general-animals": 27,
  };
  const WALLA_GENERAL_PROMPTS = {
    easy: [
      { value: "تفاحة", hint: "مثّل شيئًا يؤكل ويكون شائعًا في الفواكه." },
      { value: "سيارة", hint: "مثّل وسيلة نقل يستخدمها الناس يوميًا." },
      { value: "ساعة", hint: "مثّل شيئًا نلبسه أو نحمله لمعرفة الوقت." },
      { value: "مفتاح", hint: "مثّل شيئًا صغيرًا نستخدمه لفتح الأبواب." },
      { value: "مدرسة", hint: "مثّل مكانًا يذهب إليه الطلاب يوميًا." },
      { value: "هاتف", hint: "مثّل جهازًا نتواصل به مع الآخرين." },
      { value: "قهوة", hint: "مثّل مشروبًا ساخنًا مشهورًا عند الكبار." },
      { value: "مطر", hint: "مثّل ظاهرة تنزل من السماء في الشتاء." },
    ],
    medium: [
      { value: "مكتبة", hint: "مثّل مكانًا يرتبط بالكتب والقراءة والهدوء." },
      { value: "حديقة", hint: "مثّل مكانًا مفتوحًا يذهب إليه الناس للتنزه." },
      { value: "قطار", hint: "مثّل وسيلة نقل تسير على سكة طويلة." },
      { value: "مرآة", hint: "مثّل شيئًا ننظر إليه لرؤية أنفسنا." },
      { value: "مصعد", hint: "مثّل شيئًا ينقل الناس بين الطوابق." },
      { value: "خريطة", hint: "مثّل شيئًا يساعد في معرفة الطرق والأماكن." },
      { value: "متحف", hint: "مثّل مكانًا يحفظ أشياء تاريخية أو فنية." },
      { value: "بطولة", hint: "مثّل حدثًا تنافسيًا كبيرًا بين فرق أو لاعبين." },
    ],
    hard: [
      { value: "ضمير", hint: "مثّل شيئًا معنويًا يرتبط بالحق والخطأ داخل الإنسان." },
      { value: "دهشة", hint: "مثّل شعورًا يظهر عند المفاجأة الشديدة." },
      { value: "فوضى", hint: "مثّل حالة لا يوجد فيها ترتيب أو نظام." },
      { value: "حنين", hint: "مثّل شعورًا نحو ماضٍ أو أشخاص أو أماكن." },
      { value: "عدالة", hint: "مثّل قيمة ترتبط بالحق والإنصاف." },
      { value: "إلهام", hint: "مثّل حالة تدفع إلى فكرة أو إبداع جديد." },
      { value: "هيبة", hint: "مثّل شعورًا بالمكانة والوقار والاحترام." },
      { value: "تناقض", hint: "مثّل حالتين أو فكرتين لا تجتمعان بسهولة." },
    ],
  };
  const WALLA_ENTERTAINMENT_PROMPTS = {
    easy: [
      { value: "طاش ما طاش", kind: "مسلسل" },
      { value: "شباب البومب", kind: "مسلسل" },
      { value: "باب الحارة", kind: "مسلسل" },
      { value: "عمر وسلمى", kind: "فيلم" },
      { value: "عسل أسود", kind: "فيلم" },
      { value: "الأطلال", kind: "أغنية" },
      { value: "مدرسة المشاغبين", kind: "مسرحية" },
      { value: "العيال كبرت", kind: "مسرحية" },
    ],
    medium: [
      { value: "المال والبنون", kind: "مسلسل" },
      { value: "لن أعيش في جلباب أبي", kind: "مسلسل" },
      { value: "الزعيم", kind: "فيلم" },
      { value: "الكيف", kind: "فيلم" },
      { value: "سيرة الحب", kind: "أغنية" },
      { value: "جسمي لبّيس", kind: "أغنية" },
      { value: "الواد سيد الشغال", kind: "مسرحية" },
      { value: "بودي جارد", kind: "مسرحية" },
    ],
    hard: [
      { value: "التغريبة الفلسطينية", kind: "مسلسل" },
      { value: "ضمير أبلة حكمت", kind: "مسلسل" },
      { value: "شيء من الخوف", kind: "فيلم" },
      { value: "الكيت كات", kind: "فيلم" },
      { value: "إنت عمري", kind: "أغنية" },
      { value: "على بالي", kind: "أغنية" },
      { value: "وجهة نظر", kind: "مسرحية" },
      { value: "ريا وسكينة", kind: "مسرحية" },
    ],
  };

  function shuffle(items) {
    const copy = [...items];
    for (let index = copy.length - 1; index > 0; index -= 1) {
      const swapIndex = Math.floor(Math.random() * (index + 1));
      [copy[index], copy[swapIndex]] = [copy[swapIndex], copy[index]];
    }
    return copy;
  }

  function sampleDistinct(items, amount, excludeIds = new Set()) {
    const filtered = items.filter((item) => !excludeIds.has(item.cca3 || item.name));
    return shuffle(filtered).slice(0, amount);
  }

  function makeOptions(correct, distractors, minimum = 4) {
    const options = [correct];
    distractors.forEach((item) => {
      if (item && !options.includes(item) && options.length < minimum) {
        options.push(item);
      }
    });

    while (options.length < minimum) {
      options.push(`خيار ${options.length + 1}`);
    }

    const shuffled = shuffle(options);
    return {
      options: shuffled,
      correctIndex: shuffled.indexOf(correct),
    };
  }

  function makeQuestion(id, points, difficulty, text, answer, options, correctIndex) {
    return {
      id,
      points,
      difficulty,
      question: text,
      answer,
      options,
      correctIndex,
    };
  }

  function decodeHtml(value) {
    const parser = document.createElement("textarea");
    parser.innerHTML = String(value || "");
    return parser.value.trim();
  }

  function base64UrlEncode(value) {
    return btoa(unescape(encodeURIComponent(value)))
      .replace(/\+/g, "-")
      .replace(/\//g, "_")
      .replace(/=+$/g, "");
  }

  function delay(ms) {
    return new Promise((resolve) => window.setTimeout(resolve, ms));
  }

  function resolvePublicBaseUrl() {
    const runtime = window.QuizCategorySectionsRuntime || {};
    if (typeof runtime.resolvePublicBaseUrl === "function") {
      return runtime.resolvePublicBaseUrl();
    }
    return DEFAULT_PUBLIC_BASE_URL.replace(/\/$/, "");
  }

  function normalizeCountry(rawCountry) {
    const translations = rawCountry.translations || {};
    const arabic = translations.ara || {};
    const currencies = rawCountry.currencies || {};
    const languages = rawCountry.languages || {};

    return {
      name:
        arabic.common ||
        (rawCountry.name && rawCountry.name.common) ||
        rawCountry.cca2 ||
        "",
      commonName: rawCountry.name?.common || "",
      capital: Array.isArray(rawCountry.capital) ? rawCountry.capital[0] : null,
      currencyCodes: Object.keys(currencies || {}),
      currencyNames: Object.entries(currencies || {}).map(
        ([code, item]) => item?.name || code
      ),
      languages: Object.values(languages || {}),
      flag: rawCountry.flag || "",
      cca2: rawCountry.cca2 || "",
      cca3: rawCountry.cca3 || "",
      region: rawCountry.region || "",
      subregion: rawCountry.subregion || "",
      population: Number(rawCountry.population || 0),
      continents: rawCountry.continents || [],
      borders: rawCountry.borders || [],
      timezones: rawCountry.timezones || [],
      startOfWeek: rawCountry.startOfWeek || "",
      carSide: rawCountry.car?.side || "",
      landlocked: Boolean(rawCountry.landlocked),
      area: Number(rawCountry.area || 0),
    };
  }

  async function fetchCountryContext(cache) {
    if (cache.countries) return cache.countries;

    const primaryResponse = await fetch(
      "https://restcountries.com/v3.1/all?fields=name,translations,capital,currencies,languages,flag,cca2,cca3,region,subregion"
    );
    if (!primaryResponse.ok) {
      throw new Error("REST Countries primary request failed");
    }

    const secondaryResponse = await fetch(
      "https://restcountries.com/v3.1/all?fields=cca3,population,continents,borders,timezones,startOfWeek,car,landlocked,area"
    );
    if (!secondaryResponse.ok) {
      throw new Error("REST Countries secondary request failed");
    }

    const primaryData = await primaryResponse.json();
    const secondaryData = await secondaryResponse.json();
    const secondaryByCode = new Map(
      secondaryData
        .filter((country) => country && country.cca3)
        .map((country) => [country.cca3, country])
    );

    const data = primaryData.map((country) => ({
      ...country,
      ...(secondaryByCode.get(country.cca3) || {}),
    }));

    cache.countries = data
      .map(normalizeCountry)
      .filter((country) => country.name && country.cca2 && country.population > 0)
      .sort((a, b) => b.population - a.population);

    return cache.countries;
  }

  async function fetchOpenTriviaQuestions(categoryId) {
    if (openTriviaCache.has(categoryId)) {
      return openTriviaCache.get(categoryId);
    }

    const url = `${OPEN_TRIVIA_API_BASE}?amount=12&category=${categoryId}&type=multiple&encode=url3986`;
    for (let attempt = 0; attempt < 2; attempt += 1) {
      const response = await fetch(url);
      if (response.ok) {
        const payload = await response.json();
        if (payload?.response_code === 0 && Array.isArray(payload?.results)) {
          openTriviaCache.set(categoryId, payload.results);
          return payload.results;
        }
      }
      if (attempt === 0) {
        await delay(1200);
      }
    }
    throw new Error(`Open Trivia request failed for ${categoryId}`);
  }

  function buildOpenTriviaQuestions(item) {
    const categoryId = OPEN_TRIVIA_CATEGORY_IDS[item.subcategoryId];
    if (!categoryId) {
      throw new Error(`No browser generator configured for ${item.subcategoryId}`);
    }

    const grouped = [
      ["easy", 200],
      ["easy", 200],
      ["medium", 400],
      ["medium", 400],
      ["hard", 600],
      ["hard", 600],
    ];

    return fetchOpenTriviaQuestions(categoryId).then((results) => {
      if (!Array.isArray(results) || results.length < 6) {
        throw new Error(`Open Trivia returned insufficient results for ${categoryId}`);
      }
      const flattened = results.slice(0, 6);
      return grouped.map(([difficulty, points], index) => {
        const question = flattened[index];
        const answer = decodeHtml(decodeURIComponent(question.correct_answer || ""));
        const distractors = (question.incorrect_answers || []).map((item) =>
          decodeHtml(decodeURIComponent(item || ""))
        );
        const built = makeOptions(answer, distractors);
        return makeQuestion(
          `${item.subcategoryId}-${difficulty}-${index + 1}`,
          points,
          difficulty,
          decodeHtml(decodeURIComponent(question.question || "")),
          answer,
          built.options,
          built.correctIndex
        );
      });
    });
  }

  async function fetchQuranSurahs() {
    const response = await fetch(`${ALQURAN_CLOUD_API_BASE}/surah`);
    if (!response.ok) {
      throw new Error("AlQuran Cloud request failed");
    }
    const payload = await response.json();
    const surahs = Array.isArray(payload?.data) ? payload.data : [];
    if (!surahs.length) {
      throw new Error("AlQuran Cloud returned no surahs");
    }
    return surahs;
  }

  function pickWallaPrompt(pool) {
    const options = Array.isArray(pool) ? pool : [];
    if (!options.length) {
      throw new Error("لا توجد عناصر متاحة لهذه الجولة.");
    }
    return options[Math.floor(Math.random() * options.length)];
  }

  async function fetchArabicGeneralPrompt(category, difficulty) {
    const picked = pickWallaPrompt(
      WALLA_GENERAL_PROMPTS[difficulty] || WALLA_GENERAL_PROMPTS.easy
    );
    return {
      category,
      difficulty,
      secret_value_ar: picked.value,
      display_hint_ar: picked.hint || "مثّل الكلمة دون نطقها أو تهجئتها.",
    };
  }

  async function fetchArabicEntertainmentPrompt(difficulty) {
    const picked = pickWallaPrompt(
      WALLA_ENTERTAINMENT_PROMPTS[difficulty] || WALLA_ENTERTAINMENT_PROMPTS.easy
    );
    return {
      category: "ولا كلمة",
      difficulty,
      secret_value_ar: picked.value,
      display_hint_ar:
        "يحتوي الباركود على اسم " +
        `${picked.kind || "عمل"} ` +
        "للممثل فقط. مثّل العمل دون ذكر اسمه أو تهجئته.",
    };
  }

  async function fetchIslamicPrompt(difficulty) {
    const surahs = await fetchQuranSurahs();
    const pools = {
      easy: surahs.slice(0, 20),
      medium: surahs.slice(20, 70),
      hard: surahs.slice(70),
    };
    const pool = pools[difficulty] || pools.easy;
    const picked = pool[Math.floor(Math.random() * pool.length)];
    return {
      category: "ولا كلمة إسلامي",
      difficulty,
      secret_value_ar: String(picked.name || "").trim(),
      display_hint_ar: "مثّل اسمًا إسلاميًا أو قرآنيًا دون قول الاسم.",
    };
  }

  async function createWallaKelmaInBrowser(item, difficulty) {
    const category = item.subcategoryTitle || item.subcategoryId;
    const prompt =
      item.subcategoryId === "no-word-islamic"
        ? await fetchIslamicPrompt(difficulty)
        : item.subcategoryId === "no-word-default"
        ? await fetchArabicEntertainmentPrompt(difficulty)
        : await fetchArabicGeneralPrompt(category, difficulty);
    const token = `browser-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
    const encoded = base64UrlEncode(
      JSON.stringify({
        token,
        category: prompt.category,
        difficulty: prompt.difficulty,
        secret_value_ar: prompt.secret_value_ar,
        display_hint_ar: prompt.display_hint_ar,
      })
    );
    const qrPath = `/walla-kelma.html?client_prompt=${encoded}`;
    const publicBaseUrl = resolvePublicBaseUrl();
    return {
      token,
      category: prompt.category,
      difficulty: prompt.difficulty,
      secret_value_ar: prompt.secret_value_ar,
      display_hint_ar: prompt.display_hint_ar,
      status: "active",
      qr_path: qrPath,
      qr_url: `${publicBaseUrl}${qrPath}`,
      expires_at: null,
    };
  }

  function difficultyPool(countries, difficulty, predicate) {
    const filtered = countries.filter((country) => (predicate ? predicate(country) : true));
    if (!filtered.length) return [];
    if (difficulty === "easy") return filtered.slice(0, Math.min(70, filtered.length));
    if (difficulty === "medium") return filtered.slice(40, Math.min(140, filtered.length));
    return filtered.length > 100 ? filtered.slice(100) : filtered.slice(-60);
  }

  function buildCountryCurrencyQuestions(item, countries) {
    const valid = (country) => country.currencyCodes.length > 0;
    const configs = [
      ["easy", 200, "currency_code_of_country"],
      ["easy", 200, "country_of_currency"],
      ["medium", 400, "currency_code_of_country"],
      ["medium", 400, "country_of_currency"],
      ["hard", 600, "currency_name_of_country"],
      ["hard", 600, "country_of_currency"],
    ];

    return configs.map(([difficulty, points, mode], index) => {
      const pool = difficultyPool(countries, difficulty, valid);
      const correctCountry = pool[Math.floor(Math.random() * pool.length)];
      const currencyCode = correctCountry.currencyCodes[0];
      const currencyName = correctCountry.currencyNames[0] || currencyCode;

      if (mode === "currency_code_of_country") {
        const distractors = sampleDistinct(pool, 8, new Set([correctCountry.cca3]))
          .map((country) => country.currencyCodes[0])
          .filter(Boolean);
        const built = makeOptions(currencyCode, distractors);
        return makeQuestion(
          `${item.subcategoryId}-${difficulty}-${index + 1}`,
          points,
          difficulty,
          `ما رمز العملة الرسمية في ${correctCountry.name}؟`,
          currencyCode,
          built.options,
          built.correctIndex
        );
      }

      if (mode === "currency_name_of_country") {
        const distractors = sampleDistinct(pool, 8, new Set([correctCountry.cca3]))
          .map((country) => country.currencyNames[0])
          .filter(Boolean);
        const built = makeOptions(currencyName, distractors);
        return makeQuestion(
          `${item.subcategoryId}-${difficulty}-${index + 1}`,
          points,
          difficulty,
          `ما اسم العملة الرسمية في ${correctCountry.name}؟`,
          currencyName,
          built.options,
          built.correctIndex
        );
      }

      const distractors = sampleDistinct(pool, 8, new Set([correctCountry.cca3])).map(
        (country) => country.name
      );
      const built = makeOptions(correctCountry.name, distractors);
      return makeQuestion(
        `${item.subcategoryId}-${difficulty}-${index + 1}`,
        points,
        difficulty,
        `أي دولة تستخدم العملة ذات الرمز ${currencyCode}؟`,
        correctCountry.name,
        built.options,
        built.correctIndex
      );
    });
  }

  function buildCountryCapitalsQuestions(item, countries) {
    const valid = (country) => Boolean(country.capital);
    const configs = [
      ["easy", 200, "capital_of_country"],
      ["easy", 200, "country_of_capital"],
      ["medium", 400, "capital_of_country"],
      ["medium", 400, "country_of_capital"],
      ["hard", 600, "capital_of_country"],
      ["hard", 600, "country_of_capital"],
    ];

    return configs.map(([difficulty, points, mode], index) => {
      const pool = difficultyPool(countries, difficulty, valid);
      const correctCountry = pool[Math.floor(Math.random() * pool.length)];

      if (mode === "capital_of_country") {
        const distractors = sampleDistinct(pool, 8, new Set([correctCountry.cca3]))
          .map((country) => country.capital)
          .filter(Boolean);
        const built = makeOptions(correctCountry.capital, distractors);
        return makeQuestion(
          `${item.subcategoryId}-${difficulty}-${index + 1}`,
          points,
          difficulty,
          `ما عاصمة ${correctCountry.name}؟`,
          correctCountry.capital,
          built.options,
          built.correctIndex
        );
      }

      const distractors = sampleDistinct(pool, 8, new Set([correctCountry.cca3])).map(
        (country) => country.name
      );
      const built = makeOptions(correctCountry.name, distractors);
      return makeQuestion(
        `${item.subcategoryId}-${difficulty}-${index + 1}`,
        points,
        difficulty,
        `عاصمة أي دولة هي ${correctCountry.capital}؟`,
        correctCountry.name,
        built.options,
        built.correctIndex
      );
    });
  }

  function buildCountryFlagsQuestions(item, countries) {
    const valid = (country) => Boolean(country.flag);
    return BOARD_SLOT_POINTS.map((points, index) => {
      const difficulty = points === 200 ? "easy" : points === 400 ? "medium" : "hard";
      const pool = difficultyPool(countries, difficulty, valid);
      const correctCountry = pool[Math.floor(Math.random() * pool.length)];
      const distractors = sampleDistinct(pool, 8, new Set([correctCountry.cca3])).map(
        (country) => country.name
      );
      const built = makeOptions(correctCountry.name, distractors);
      return makeQuestion(
        `${item.subcategoryId}-${difficulty}-${index + 1}`,
        points,
        difficulty,
        `لأي دولة يعود هذا العلم ${correctCountry.flag}؟`,
        correctCountry.name,
        built.options,
        built.correctIndex
      );
    });
  }

  function buildCountryLanguageQuestions(item, countries) {
    const valid = (country) => country.languages.length > 0;
    const configs = [
      ["easy", 200, "language_of_country"],
      ["easy", 200, "country_of_language"],
      ["medium", 400, "language_of_country"],
      ["medium", 400, "country_of_language"],
      ["hard", 600, "identify_from_language_and_capital"],
      ["hard", 600, "identify_from_language_and_region"],
    ];

    return configs.map(([difficulty, points, mode], index) => {
      const pool = difficultyPool(countries, difficulty, valid);
      const correctCountry = pool[Math.floor(Math.random() * pool.length)];
      const language = correctCountry.languages[0];

      if (mode === "language_of_country") {
        const distractors = sampleDistinct(pool, 8, new Set([correctCountry.cca3]))
          .map((country) => country.languages[0])
          .filter(Boolean);
        const built = makeOptions(language, distractors);
        return makeQuestion(
          `${item.subcategoryId}-${difficulty}-${index + 1}`,
          points,
          difficulty,
          `ما إحدى اللغات الرسمية في ${correctCountry.name}؟`,
          language,
          built.options,
          built.correctIndex
        );
      }

      if (mode === "country_of_language") {
        const distractors = sampleDistinct(pool, 8, new Set([correctCountry.cca3])).map(
          (country) => country.name
        );
        const built = makeOptions(correctCountry.name, distractors);
        return makeQuestion(
          `${item.subcategoryId}-${difficulty}-${index + 1}`,
          points,
          difficulty,
          `في أي دولة تُعد ${language} لغة رسمية؟`,
          correctCountry.name,
          built.options,
          built.correctIndex
        );
      }

      if (mode === "identify_from_language_and_capital") {
        const distractors = sampleDistinct(pool, 8, new Set([correctCountry.cca3])).map(
          (country) => country.name
        );
        const built = makeOptions(correctCountry.name, distractors);
        return makeQuestion(
          `${item.subcategoryId}-${difficulty}-${index + 1}`,
          points,
          difficulty,
          `ما الدولة التي عاصمتها ${correctCountry.capital} وإحدى لغاتها الرسمية ${language}؟`,
          correctCountry.name,
          built.options,
          built.correctIndex
        );
      }

      const distractors = sampleDistinct(pool, 8, new Set([correctCountry.cca3])).map(
        (country) => country.name
      );
      const built = makeOptions(correctCountry.name, distractors);
      return makeQuestion(
        `${item.subcategoryId}-${difficulty}-${index + 1}`,
        points,
        difficulty,
        `أي دولة تقع في ${correctCountry.region || "هذا الإقليم"} وتُعد ${language} لغة رسمية فيها؟`,
        correctCountry.name,
        built.options,
        built.correctIndex
      );
    });
  }

  function buildCountryGeographyQuestions(item, countries) {
    const configs = [
      ["easy", 200, "continent"],
      ["easy", 200, "region"],
      ["medium", 400, "subregion"],
      ["medium", 400, "borders_count"],
      ["hard", 600, "landlocked"],
      ["hard", 600, "timezone_count"],
    ];

    return configs.map(([difficulty, points, mode], index) => {
      let pool = difficultyPool(countries, difficulty, (country) => country.continents.length > 0);
      let correctCountry = pool[Math.floor(Math.random() * pool.length)];

      if (mode === "continent") {
        const answer = correctCountry.continents[0];
        const built = makeOptions(answer, [
          "آسيا",
          "أفريقيا",
          "أوروبا",
          "أمريكا الشمالية",
          "أمريكا الجنوبية",
          "أوقيانوسيا",
        ]);
        return makeQuestion(
          `${item.subcategoryId}-${difficulty}-${index + 1}`,
          points,
          difficulty,
          `في أي قارة تقع ${correctCountry.name}؟`,
          answer,
          built.options,
          built.correctIndex
        );
      }

      if (mode === "region") {
        const answer = correctCountry.region || "غير محدد";
        const built = makeOptions(answer, ["Africa", "Americas", "Asia", "Europe", "Oceania", "Polar"]);
        return makeQuestion(
          `${item.subcategoryId}-${difficulty}-${index + 1}`,
          points,
          difficulty,
          `إلى أي إقليم رئيسي تنتمي ${correctCountry.name}؟`,
          answer,
          built.options,
          built.correctIndex
        );
      }

      if (mode === "subregion") {
        pool = pool.filter((country) => country.subregion);
        correctCountry = pool[Math.floor(Math.random() * pool.length)];
        const answer = correctCountry.subregion;
        const distractors = sampleDistinct(pool, 8, new Set([correctCountry.cca3]))
          .map((country) => country.subregion)
          .filter(Boolean);
        const built = makeOptions(answer, distractors);
        return makeQuestion(
          `${item.subcategoryId}-${difficulty}-${index + 1}`,
          points,
          difficulty,
          `ما المنطقة الفرعية التي تقع فيها ${correctCountry.name}؟`,
          answer,
          built.options,
          built.correctIndex
        );
      }

      if (mode === "borders_count") {
        const answer = String(correctCountry.borders.length);
        const built = makeOptions(
          answer,
          ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"].filter((item) => item !== answer)
        );
        return makeQuestion(
          `${item.subcategoryId}-${difficulty}-${index + 1}`,
          points,
          difficulty,
          `كم عدد الدول التي تشترك بحدود برية مع ${correctCountry.name}؟`,
          answer,
          built.options,
          built.correctIndex
        );
      }

      if (mode === "landlocked") {
        const landlockedPool = pool.filter((country) => country.landlocked);
        const coastPool = pool.filter((country) => !country.landlocked);
        correctCountry = landlockedPool[Math.floor(Math.random() * landlockedPool.length)];
        const distractors = sampleDistinct(coastPool, 3).map((country) => country.name);
        const built = makeOptions(correctCountry.name, distractors);
        return makeQuestion(
          `${item.subcategoryId}-${difficulty}-${index + 1}`,
          points,
          difficulty,
          "أي دولة من التالية دولة حبيسة لا تطل على بحر؟",
          correctCountry.name,
          built.options,
          built.correctIndex
        );
      }

      const answer = String(correctCountry.timezones.length);
      const built = makeOptions(
        answer,
        ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"].filter((item) => item !== answer)
      );
      return makeQuestion(
        `${item.subcategoryId}-${difficulty}-${index + 1}`,
        points,
        difficulty,
        `كم منطقة زمنية تقريبًا تسجلها بيانات ${correctCountry.name}؟`,
        answer,
        built.options,
        built.correctIndex
      );
    });
  }

  function buildCountryIdentifyQuestions(item, countries) {
    const valid = (country) =>
      Boolean(country.capital && country.currencyCodes.length && country.languages.length);

    return BOARD_SLOT_POINTS.map((points, index) => {
      const difficulty = points === 200 ? "easy" : points === 400 ? "medium" : "hard";
      const pool = difficultyPool(countries, difficulty, valid);
      const correctCountry = pool[Math.floor(Math.random() * pool.length)];
      const language = correctCountry.languages[0];
      const currency = correctCountry.currencyCodes[0];
      const continent = correctCountry.continents[0];
      const text =
        difficulty === "easy"
          ? `ما هي الدولة التي عاصمتها ${correctCountry.capital}، وعملتها ${currency}، وإحدى لغاتها الرسمية ${language}؟`
          : `ما هي الدولة التي عاصمتها ${correctCountry.capital}، وعملتها ${currency}، وإحدى لغاتها الرسمية ${language}، وتقع في ${continent}؟`;
      const distractors = sampleDistinct(pool, 8, new Set([correctCountry.cca3])).map(
        (country) => country.name
      );
      const built = makeOptions(correctCountry.name, distractors);
      return makeQuestion(
        `${item.subcategoryId}-${difficulty}-${index + 1}`,
        points,
        difficulty,
        text,
        correctCountry.name,
        built.options,
        built.correctIndex
      );
    });
  }

  function buildCountryTravelQuestions(item, countries) {
    const valid = (country) => Boolean(country.capital && country.continents.length);
    const configs = [
      ["easy", 200, "destination_by_capital"],
      ["easy", 200, "destination_by_continent"],
      ["medium", 400, "destination_by_drive_side"],
      ["medium", 400, "destination_by_start_of_week"],
      ["hard", 600, "destination_by_timezone_and_capital"],
      ["hard", 600, "destination_by_landlocked_and_capital"],
    ];

    return configs.map(([difficulty, points, mode], index) => {
      const pool = difficultyPool(countries, difficulty, valid);
      const correctCountry = pool[Math.floor(Math.random() * pool.length)];

      if (mode === "destination_by_capital") {
        const distractors = sampleDistinct(pool, 8, new Set([correctCountry.cca3])).map(
          (country) => country.name
        );
        const built = makeOptions(correctCountry.name, distractors);
        return makeQuestion(
          `${item.subcategoryId}-${difficulty}-${index + 1}`,
          points,
          difficulty,
          `إذا كانت رحلتك إلى مدينة ${correctCountry.capital}، فأنت متجه إلى أي دولة؟`,
          correctCountry.name,
          built.options,
          built.correctIndex
        );
      }

      if (mode === "destination_by_continent") {
        const distractors = sampleDistinct(pool, 8, new Set([correctCountry.cca3])).map(
          (country) => country.name
        );
        const built = makeOptions(correctCountry.name, distractors);
        return makeQuestion(
          `${item.subcategoryId}-${difficulty}-${index + 1}`,
          points,
          difficulty,
          `أي دولة من التالية تُعد وجهة سفر في قارة ${correctCountry.continents[0]}؟`,
          correctCountry.name,
          built.options,
          built.correctIndex
        );
      }

      if (mode === "destination_by_drive_side") {
        const answer = correctCountry.carSide === "left" ? "اليسار" : "اليمين";
        const built = makeOptions(answer, ["اليسار", "اليمين"]);
        return makeQuestion(
          `${item.subcategoryId}-${difficulty}-${index + 1}`,
          points,
          difficulty,
          `إذا سافرت إلى ${correctCountry.name}، ففي أي جهة من الطريق تقود السيارات غالبًا؟`,
          answer,
          built.options,
          built.correctIndex
        );
      }

      if (mode === "destination_by_start_of_week") {
        const answer = correctCountry.startOfWeek || "monday";
        const built = makeOptions(answer, ["monday", "sunday", "saturday"]);
        return makeQuestion(
          `${item.subcategoryId}-${difficulty}-${index + 1}`,
          points,
          difficulty,
          `في بيانات ${correctCountry.name} يبدأ الأسبوع عادةً بأي يوم؟`,
          answer,
          built.options,
          built.correctIndex
        );
      }

      if (mode === "destination_by_timezone_and_capital") {
        const distractors = sampleDistinct(pool, 8, new Set([correctCountry.cca3])).map(
          (country) => country.name
        );
        const built = makeOptions(correctCountry.name, distractors);
        return makeQuestion(
          `${item.subcategoryId}-${difficulty}-${index + 1}`,
          points,
          difficulty,
          `أي دولة عاصمتها ${correctCountry.capital} وتسجل ${correctCountry.timezones.length} منطقة زمنية تقريبًا؟`,
          correctCountry.name,
          built.options,
          built.correctIndex
        );
      }

      const landlockedCopy = correctCountry.landlocked ? "دولة حبيسة" : "دولة ساحلية";
      const distractors = sampleDistinct(pool, 8, new Set([correctCountry.cca3])).map(
        (country) => country.name
      );
      const built = makeOptions(correctCountry.name, distractors);
      return makeQuestion(
        `${item.subcategoryId}-${difficulty}-${index + 1}`,
        points,
        difficulty,
        `أي دولة عاصمتها ${correctCountry.capital} وتُعد ${landlockedCopy}؟`,
        correctCountry.name,
        built.options,
        built.correctIndex
      );
    });
  }

  const liveGenerators = {
    "general-technology": async (item) => buildOpenTriviaQuestions(item),
    "general-general-knowledge": async (item) => buildOpenTriviaQuestions(item),
    "general-history": async (item) => buildOpenTriviaQuestions(item),
    "general-animals": async (item) => buildOpenTriviaQuestions(item),
    "countries-currencies": async (item, cache) =>
      buildCountryCurrencyQuestions(item, await fetchCountryContext(cache)),
    "countries-country-capitals": async (item, cache) =>
      buildCountryCapitalsQuestions(item, await fetchCountryContext(cache)),
    "countries-capitals": async (item, cache) =>
      buildCountryCapitalsQuestions(item, await fetchCountryContext(cache)),
    "countries-flags": async (item, cache) =>
      buildCountryFlagsQuestions(item, await fetchCountryContext(cache)),
    "countries-languages": async (item, cache) =>
      buildCountryLanguageQuestions(item, await fetchCountryContext(cache)),
    "countries-geography": async (item, cache) =>
      buildCountryGeographyQuestions(item, await fetchCountryContext(cache)),
    "countries-what-country": async (item, cache) =>
      buildCountryIdentifyQuestions(item, await fetchCountryContext(cache)),
    "countries-travel": async (item, cache) =>
      buildCountryTravelQuestions(item, await fetchCountryContext(cache)),
  };

  async function prepareMatchInBrowser(selectedItems) {
    const cache = {};
    const diagnostics = [];
    const questionBank = [];

    for (const item of selectedItems || []) {
      const generator = liveGenerators[item.subcategoryId];
      if (!generator) {
        diagnostics.push({
          id: item.subcategoryId,
          name: item.subcategoryTitle || item.subcategoryId,
          sourceMode: "fallback",
          questionCount: 0,
          reason: "No live browser API generator configured for this subcategory",
        });
        continue;
      }

      try {
        const questions = await generator(item, cache);
        questionBank.push({
          id: item.subcategoryId,
          name: item.subcategoryTitle || item.subcategoryId,
          icon: item.iconKey || "✨",
          imageKey: item.imageKey || null,
          iconKey: item.iconKey || null,
          flagCode: item.flagCode || null,
          description: "أسئلة مولدة من APIs حية.",
          questions,
          sourceMode: "api",
        });
        diagnostics.push({
          id: item.subcategoryId,
          name: item.subcategoryTitle || item.subcategoryId,
          sourceMode: "api",
          questionCount: questions.length,
        });
      } catch (error) {
        diagnostics.push({
          id: item.subcategoryId,
          name: item.subcategoryTitle || item.subcategoryId,
          sourceMode: "fallback",
          questionCount: 0,
          reason: error instanceof Error ? error.message : String(error),
        });
      }
    }

    return {
      questionBank,
      diagnostics,
      preparedCount: questionBank.length,
      apiReady:
        questionBank.length === (selectedItems || []).length &&
        diagnostics.every((item) => item.sourceMode === "api"),
    };
  }

  window.QuizCategorySectionsRuntime = {
    ...(window.QuizCategorySectionsRuntime || {}),
    prepareMatchInBrowser,
    createWallaKelmaInBrowser,
  };
})();
