// Purpose: describe the live sources surfaced to the quiz category UI.
export type QuizApiSourceKey =
  | "api_ninjas_logo"
  | "kalimalab"
  | "open_trivia_db"
  | "rest_countries"
  | "islamic_quiz_api"
  | "quran_foundation"
  | "mumin_hadith"
  | "fallback_required"
  | "hybrid_general"
  | "hybrid_countries"
  | "internal_letters_api";

export type ApiSourceDefinition = {
  key: QuizApiSourceKey;
  label: string;
  useFor: string[];
  strengths: string[];
  limits: string[];
  requiresAuth: boolean;
  supportsArabicDirectly: boolean;
  recommendedUsage: string;
};

export const apiSourceMap: ApiSourceDefinition[] = [
  {
    key: "api_ninjas_logo",
    label: "API Ninjas Logo API",
    useFor: ["شعارات وعلامات تجارية"],
    strengths: [
      "يعطي أسماء الشركات مع رابط الشعار من سجل حي واحد",
      "مناسب تمامًا لوضع reveal_visual بدل MCQ",
      "يسمح بعرض الشعار أولًا ثم كشف الاسم العربي لاحقًا",
    ],
    limits: [
      "يتطلب API key صالحًا",
      "ليس trivia API نصيًا عامًا بل مصدر شعارات مباشر",
      "ترجمة الاسم العربي وتحديد الصعوبة تحصل في backend",
    ],
    requiresAuth: true,
    supportsArabicDirectly: false,
    recommendedUsage:
      "استخدمه لفئة الشعارات والعلامات التجارية فقط، مع تعريب الاسم في backend وإرسال السؤال كـ reveal_visual.",
  },
  {
    key: "kalimalab",
    label: "KalimaLab",
    useFor: ["لغة وأدب", "حروف"],
    strengths: [
      "يعطي مفردات عربية مباشرة",
      "مناسب لأسئلة الكلمات والمعاني والتلميحات العربية",
      "يتكامل جيدًا مع أسلوب reveal العربي",
    ],
    limits: [
      "يعتمد على توفر token صالح",
      "ليس trivia API عامًا للفروع غير اللغوية",
      "بعض الفروع تحتاج ضبط templates في backend",
    ],
    requiresAuth: true,
    supportsArabicDirectly: true,
    recommendedUsage:
      "استخدمه لفروع اللغة والحروف عندما تريد محتوى عربي مباشرًا دون ترجمة وسيطة.",
  },
  {
    key: "open_trivia_db",
    label: "Open Trivia DB",
    useFor: ["تاريخ", "عالم الحيوان", "تكنولوجيا"],
    strengths: [
      "يدعم amount و difficulty مباشرة",
      "مفيد للأسئلة العامة السريعة",
      "لا يحتاج API key",
    ],
    limits: [
      "المحتوى الأساسي غالبًا بالإنجليزية",
      "لا يغطي الفروع البصرية أو المتخصصة جدًا",
      "يحتاج LibreTranslate قبل إرسال أي نص للاعب",
    ],
    requiresAuth: false,
    supportsArabicDirectly: false,
    recommendedUsage:
      "استخدمه كمصدر إنجليزي لتاريخ/تقنية/حيوان، ثم مرّر السؤال والجواب عبر LibreTranslate فقط قبل reveal.",
  },
  {
    key: "rest_countries",
    label: "REST Countries",
    useFor: ["أعلام", "عواصم", "عملات", "لغات الدول", "بيانات جغرافية أساسية"],
    strengths: [
      "مصدر واضح ومنظم لبيانات الدول",
      "مناسب لتوليد أسئلة القارات والعواصم والعملات",
      "يعطي الأعلام واللغات والعملات والعاصمة",
    ],
    limits: [
      "ليس trivia API مباشرًا",
      "لا يغطي الأعلام القديمة أو النشيد الوطني أو الرؤساء",
      "يحتاج question templates في backend",
    ],
    requiresAuth: false,
    supportsArabicDirectly: false,
    recommendedUsage:
      "استعمله كمصدر بيانات خام لأسئلة الدول، ثم ولّد السؤال والإجابات في backend.",
  },
  {
    key: "islamic_quiz_api",
    label: "IslamicQuizAPI",
    useFor: ["التفسير", "العقيدة", "الحديث", "الفقه", "التاريخ", "اللغة العربية"],
    strengths: [
      "يعطي فئات وموضوعات وأسئلة عربية مباشرة",
      "يسهّل بناء أسئلة reveal دون ترجمة من الإنجليزية",
      "يمتلك بنية category/topic واضحة قابلة للتوسعة",
    ],
    limits: [
      "يعتمد على توفر الخدمة الحية بشكل كامل",
      "ليس API reveal-ready بشكل مباشر لذا يحتاج normalization في backend",
      "بعض الفروع تعتمد على كثافة المحتوى المتاح في المصدر الحي",
    ],
    requiresAuth: false,
    supportsArabicDirectly: true,
    recommendedUsage:
      "استخدمه مباشرة للفروع الإسلامية الستة، واترك backend يطبع difficulty ويتحقق من سلامة السؤال والجواب قبل الإرسال.",
  },
  {
    key: "quran_foundation",
    label: "Quran Foundation Content APIs",
    useFor: ["القرآن", "جزء عم", "جزء تبارك", "بعض معاني القرآن"],
    strengths: [
      "مصدر قوي لبيانات السور والآيات",
      "ممتاز للمحتوى القرآني المنظم",
      "مناسب لتوليد أسئلة رقم السورة وعدد الآيات والترتيب",
    ],
    limits: [
      "يتطلب auth رسميًا في docs",
      "ليس trivia API جاهزًا",
      "معاني القرآن والأسئلة التفسيرية تحتاج templates إضافية",
    ],
    requiresAuth: true,
    supportsArabicDirectly: true,
    recommendedUsage:
      "استخدمه في backend للمحتوى القرآني الرسمي، مع fallback محلي عند غياب auth أو عند الحاجة لصياغة لعبية.",
  },
  {
    key: "mumin_hadith",
    label: "Mumin Hadith API",
    useFor: ["أحاديث"],
    strengths: [
      "مخصص للحديث",
      "يقدم محتوى من مجموعات حديثية متعددة",
      "أنسب من trivia APIs العامة لفرع الحديث",
    ],
    limits: [
      "يتطلب API key",
      "ليس trivia-ready بشكل مباشر",
      "باقي الفروع الإسلامية لا يغطيها وحده",
    ],
    requiresAuth: true,
    supportsArabicDirectly: true,
    recommendedUsage:
      "استخدمه فقط لفرع الأحاديث إن توفرت مفاتيح الوصول، وإلا اعتمد fallback منظم.",
  },
  {
    key: "hybrid_general",
    label: "The Trivia API (معلومات عامة فقط)",
    useFor: ["معلومات عامة"],
    strengths: [
      "يستخدم The Trivia API v2 بالإنجليزية ثم LibreTranslate للعربية",
      "يصفّي الأسئلة الضعيفة قبل قبولها",
      "يحافظ على reveal_answer دون MCQ",
    ],
    limits: [
      "لا يُستخدم كمصدر لتاريخ/تقنية/حيوان (هذه تذهب لـ Open Trivia DB)",
      "يحتاج مفتاح The Trivia API إذا اشترطه الحساب",
      "يحتاج خادم LibreTranslate متاحًا",
    ],
    requiresAuth: false,
    supportsArabicDirectly: false,
    recommendedUsage:
      "استخدمه فقط لبطاقة معلومات عامة: اجلب نصًا إنجليزيًا من The Trivia API ثم ترجم عبر LibreTranslate قبل reveal.",
  },
  {
    key: "hybrid_countries",
    label: "Hybrid Countries Source",
    useFor: ["جغرافيا", "سياحة وسفر", "ما هي الدولة", "لغات ولهجات"],
    strengths: [
      "يجمع data APIs مع templates",
      "عملي جدًا لفروع الدول المركبة",
      "أقرب طريقة واقعية لأسئلة screenshot-style",
    ],
    limits: [
      "يحتاج منطق توليد أسئلة",
      "لا يعطي trivia جاهزة مباشرة",
      "بعض الفروع مثل الخرائط تحتاج طبقة بصرية خاصة",
    ],
    requiresAuth: false,
    supportsArabicDirectly: false,
    recommendedUsage:
      "استخدمه عندما تكون البيانات الأساسية متوفرة لكن السؤال نفسه يحتاج تركيبًا مخصصًا.",
  },
  {
    key: "internal_letters_api",
    label: "Internal Letters API",
    useFor: ["حروف", "حروف كروية", "حروف غنائي", "حروف إسلامي", "حروف أنمي", "حروف متحركة"],
    strengths: [
      "يُخرج الأسئلة بالعربية مباشرة",
      "مجهز لنمط الحرف الأول + الوصف",
      "لا يعتمد على ترجمة لحظية عند التشغيل",
    ],
    limits: [
      "مبني على بنك منظم داخل التطبيق",
      "التغطية الحالية محدودة بما هو متاح في هذا الإصدار",
      "يحتاج توسعة لاحقة إذا زادت الفروع أو القواعد",
    ],
    requiresAuth: false,
    supportsArabicDirectly: true,
    recommendedUsage:
      "استخدمه لفروع الحروف عندما تكون صيغة السؤال عربية ومحددة بالحرف الأول والوصف داخل backend.",
  },
  {
    key: "fallback_required",
    label: "مصدر مخصص",
    useFor: [
      "الفروع البصرية",
      "العطور",
      "ولاكلمة",
      "الحروف",
      "الأمثال",
      "الخرائط",
      "رؤساء الدول",
      "النشيد الوطني",
    ],
    strengths: [
      "صريح وواقعي",
      "يمنع ادعاء وجود API غير موجود",
      "مفيد للفروع المخصصة جدًا أو العربية جدًا",
    ],
    limits: [
      "ليس مصدر API فعلي",
      "يتطلب curated content أو custom source",
      "قد يحتاج وسائط أو صور أو صوت",
    ],
    requiresAuth: false,
    supportsArabicDirectly: true,
    recommendedUsage:
      "اجعل الـ backend يقرر استخدام محتوى عربي محلي منظم أو مصدر داخلي مخصص لهذا الفرع.",
  },
];
