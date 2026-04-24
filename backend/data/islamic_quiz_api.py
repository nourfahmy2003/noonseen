"""Purpose: host the in-process IslamicQuizAPI dataset used by the SeenJeem backend."""

from copy import deepcopy

from backend.models.schemas import IslamicQuizApiCategory, IslamicQuizApiQuestionRecord, IslamicQuizApiTopic


ISLAMIC_QUIZ_CATEGORIES: list[IslamicQuizApiCategory] = [
    {"id": 1, "arabicName": "التفسير", "englishName": "Tafseer", "description": "أسئلة في تفسير الألفاظ والمعاني القرآنية."},
    {"id": 2, "arabicName": "العقيدة", "englishName": "Aqeedah", "description": "أسئلة في أصول الاعتقاد والإيمان."},
    {"id": 3, "arabicName": "الحديث", "englishName": "Hadith", "description": "أسئلة في معاني الأحاديث ورواتها ومصادرها."},
    {"id": 4, "arabicName": "الفقه", "englishName": "Fiqh", "description": "أسئلة في الأحكام والعبادات والطهارة."},
    {"id": 5, "arabicName": "التاريخ", "englishName": "Islamic History", "description": "أسئلة في السيرة والخلفاء والمعارك والدول الإسلامية."},
    {"id": 6, "arabicName": "اللغة العربية", "englishName": "Arabic Language", "description": "أسئلة في أساسيات النحو والصرف والمفردات."},
]

ISLAMIC_QUIZ_TOPICS_BY_CATEGORY_ID: dict[int, list[IslamicQuizApiTopic]] = {
    1: [
        {"slug": "tafseer-meanings", "name": "معاني الألفاظ", "description": "معاني كلمات وتراكيب قرآنية مشهورة."},
    ],
    2: [
        {"slug": "aqeedah-foundations", "name": "أصول الإيمان", "description": "أسئلة تمهيدية ومتوسطة في العقيدة الإسلامية."},
    ],
    3: [
        {"slug": "hadith-foundations", "name": "معاني الأحاديث", "description": "أسئلة في متون الأحاديث ومضامينها ورواتها."},
    ],
    4: [
        {"slug": "fiqh-foundations", "name": "فقه العبادات", "description": "أسئلة في الصلاة والطهارة والصيام والزكاة."},
    ],
    5: [
        {"slug": "islamic-history-foundations", "name": "محطات إسلامية", "description": "أسئلة في التاريخ الإسلامي المشهور."},
    ],
    6: [
        {"slug": "arabic-language-foundations", "name": "أساسيات اللغة", "description": "أسئلة لغوية عربية مباشرة وواضحة."},
    ],
}

ISLAMIC_QUIZ_QUESTIONS_BY_CATEGORY_AND_TOPIC: dict[tuple[int, str], list[IslamicQuizApiQuestionRecord]] = {
    (1, "tafseer-meanings"): [
        {"id": 101, "q": "ما المقصود بالكوثر في قوله تعالى: إنا أعطيناك الكوثر؟", "level": 1, "link": "internal://islamicquizapi/1/tafseer-meanings/101", "section": "التفسير", "answers": [{"answer": "الخير الكثير", "t": 1}]},
        {"id": 102, "q": "ما المقصود بالفلق في سورة الفلق؟", "level": 1, "link": "internal://islamicquizapi/1/tafseer-meanings/102", "section": "التفسير", "answers": [{"answer": "الصبح", "t": 1}]},
        {"id": 103, "q": "ما معنى الغاسق إذا وقب؟", "level": 2, "link": "internal://islamicquizapi/1/tafseer-meanings/103", "section": "التفسير", "answers": [{"answer": "الليل إذا أظلم", "t": 1}]},
        {"id": 104, "q": "ما المقصود بحبل الله في قوله تعالى: واعتصموا بحبل الله جميعا؟", "level": 2, "link": "internal://islamicquizapi/1/tafseer-meanings/104", "section": "التفسير", "answers": [{"answer": "القرآن", "t": 1}]},
        {"id": 105, "q": "ما المقصود بالقارعة في قوله تعالى: القارعة ما القارعة؟", "level": 3, "link": "internal://islamicquizapi/1/tafseer-meanings/105", "section": "التفسير", "answers": [{"answer": "القيامة", "t": 1}]},
        {"id": 106, "q": "ما معنى المزجاة في قوله تعالى: وجئنا ببضاعة مزجاة؟", "level": 3, "link": "internal://islamicquizapi/1/tafseer-meanings/106", "section": "التفسير", "answers": [{"answer": "القليلة الضعيفة", "t": 1}]},
    ],
    (2, "aqeedah-foundations"): [
        {"id": 201, "q": "كم عدد أركان الإيمان؟", "level": 1, "link": "internal://islamicquizapi/2/aqeedah-foundations/201", "section": "العقيدة", "answers": [{"answer": "ستة", "t": 1}]},
        {"id": 202, "q": "من هو خاتم الأنبياء والمرسلين؟", "level": 1, "link": "internal://islamicquizapi/2/aqeedah-foundations/202", "section": "العقيدة", "answers": [{"answer": "محمد صلى الله عليه وسلم", "t": 1}]},
        {"id": 203, "q": "ما الركن الذي يتضمن الإيمان بالبعث والحساب والجنة والنار؟", "level": 2, "link": "internal://islamicquizapi/2/aqeedah-foundations/203", "section": "العقيدة", "answers": [{"answer": "الإيمان باليوم الآخر", "t": 1}]},
        {"id": 204, "q": "ما التوحيد الذي يتضمن إفراد الله تعالى بالعبادة؟", "level": 2, "link": "internal://islamicquizapi/2/aqeedah-foundations/204", "section": "العقيدة", "answers": [{"answer": "توحيد الألوهية", "t": 1}]},
        {"id": 205, "q": "ما اسم الشرك الذي يعمل فيه الإنسان العمل ليراه الناس؟", "level": 3, "link": "internal://islamicquizapi/2/aqeedah-foundations/205", "section": "العقيدة", "answers": [{"answer": "الرياء", "t": 1}]},
        {"id": 206, "q": "ما نوع التوحيد المتعلق بأسماء الله وصفاته كما جاءت في النصوص؟", "level": 3, "link": "internal://islamicquizapi/2/aqeedah-foundations/206", "section": "العقيدة", "answers": [{"answer": "توحيد الأسماء والصفات", "t": 1}]},
    ],
    (3, "hadith-foundations"): [
        {"id": 301, "q": "في حديث: إنما الأعمال بالنيات، ما الذي تصحح به الأعمال؟", "level": 1, "link": "internal://islamicquizapi/3/hadith-foundations/301", "section": "الحديث", "answers": [{"answer": "النية", "t": 1}]},
        {"id": 302, "q": "في حديث: المسلم من سلم المسلمون من لسانه ويده، ما الأمران المذكوران في الحديث؟", "level": 1, "link": "internal://islamicquizapi/3/hadith-foundations/302", "section": "الحديث", "answers": [{"answer": "اللسان واليد", "t": 1}]},
        {"id": 303, "q": "من الصحابي الذي روى حديث: إنما الأعمال بالنيات؟", "level": 2, "link": "internal://islamicquizapi/3/hadith-foundations/303", "section": "الحديث", "answers": [{"answer": "عمر بن الخطاب", "t": 1}]},
        {"id": 304, "q": "ما المقصود بالإحسان في حديث جبريل؟", "level": 2, "link": "internal://islamicquizapi/3/hadith-foundations/304", "section": "الحديث", "answers": [{"answer": "أن تعبد الله كأنك تراه", "t": 1}]},
        {"id": 305, "q": "في أي كتاب اشتهر ورود حديث: من حسن إسلام المرء تركه ما لا يعنيه؟", "level": 3, "link": "internal://islamicquizapi/3/hadith-foundations/305", "section": "الحديث", "answers": [{"answer": "سنن الترمذي", "t": 1}]},
        {"id": 306, "q": "من الصحابي الذي روى حديث: لا يؤمن أحدكم حتى يحب لأخيه ما يحب لنفسه؟", "level": 3, "link": "internal://islamicquizapi/3/hadith-foundations/306", "section": "الحديث", "answers": [{"answer": "أنس بن مالك", "t": 1}]},
    ],
    (4, "fiqh-foundations"): [
        {"id": 401, "q": "كم عدد الصلوات المفروضة في اليوم والليلة؟", "level": 1, "link": "internal://islamicquizapi/4/fiqh-foundations/401", "section": "الفقه", "answers": [{"answer": "خمس", "t": 1}]},
        {"id": 402, "q": "متى يبدأ وقت صيام رمضان في كل يوم؟", "level": 1, "link": "internal://islamicquizapi/4/fiqh-foundations/402", "section": "الفقه", "answers": [{"answer": "بطلوع الفجر", "t": 1}]},
        {"id": 403, "q": "ما الركن الذي لا تصح صلاة الفريضة إلا به عند القدرة؟", "level": 2, "link": "internal://islamicquizapi/4/fiqh-foundations/403", "section": "الفقه", "answers": [{"answer": "القيام", "t": 1}]},
        {"id": 404, "q": "ما أول أركان الوضوء المذكورة في آية المائدة؟", "level": 2, "link": "internal://islamicquizapi/4/fiqh-foundations/404", "section": "الفقه", "answers": [{"answer": "غسل الوجه", "t": 1}]},
        {"id": 405, "q": "ما الحكم الفقهي لزكاة الفطر؟", "level": 3, "link": "internal://islamicquizapi/4/fiqh-foundations/405", "section": "الفقه", "answers": [{"answer": "واجبة", "t": 1}]},
        {"id": 406, "q": "ما اسم الطهارة التي تكون بالتراب عند عدم الماء أو تعذر استعماله؟", "level": 3, "link": "internal://islamicquizapi/4/fiqh-foundations/406", "section": "الفقه", "answers": [{"answer": "التيمم", "t": 1}]},
    ],
    (5, "islamic-history-foundations"): [
        {"id": 501, "q": "من أول الخلفاء الراشدين؟", "level": 1, "link": "internal://islamicquizapi/5/islamic-history-foundations/501", "section": "التاريخ", "answers": [{"answer": "أبو بكر الصديق", "t": 1}]},
        {"id": 502, "q": "إلى أي مدينة هاجر النبي صلى الله عليه وسلم؟", "level": 1, "link": "internal://islamicquizapi/5/islamic-history-foundations/502", "section": "التاريخ", "answers": [{"answer": "المدينة المنورة", "t": 1}]},
        {"id": 503, "q": "ما اسم أول معركة كبرى في الإسلام؟", "level": 2, "link": "internal://islamicquizapi/5/islamic-history-foundations/503", "section": "التاريخ", "answers": [{"answer": "بدر", "t": 1}]},
        {"id": 504, "q": "في عهد أي خليفة جُمع الناس على مصحف واحد؟", "level": 2, "link": "internal://islamicquizapi/5/islamic-history-foundations/504", "section": "التاريخ", "answers": [{"answer": "عثمان بن عفان", "t": 1}]},
        {"id": 505, "q": "من القائد المسلم الذي قاد معركة القادسية؟", "level": 3, "link": "internal://islamicquizapi/5/islamic-history-foundations/505", "section": "التاريخ", "answers": [{"answer": "سعد بن أبي وقاص", "t": 1}]},
        {"id": 506, "q": "ما الدولة الإسلامية التي اتخذت بغداد عاصمة لها؟", "level": 3, "link": "internal://islamicquizapi/5/islamic-history-foundations/506", "section": "التاريخ", "answers": [{"answer": "الدولة العباسية", "t": 1}]},
    ],
    (6, "arabic-language-foundations"): [
        {"id": 601, "q": "ما نوع الكلمة: كتاب؟", "level": 1, "link": "internal://islamicquizapi/6/arabic-language-foundations/601", "section": "اللغة العربية", "answers": [{"answer": "اسم", "t": 1}]},
        {"id": 602, "q": "ما ضد كلمة: الصدق؟", "level": 1, "link": "internal://islamicquizapi/6/arabic-language-foundations/602", "section": "اللغة العربية", "answers": [{"answer": "الكذب", "t": 1}]},
        {"id": 603, "q": "ما جمع كلمة: قلم؟", "level": 2, "link": "internal://islamicquizapi/6/arabic-language-foundations/603", "section": "اللغة العربية", "answers": [{"answer": "أقلام", "t": 1}]},
        {"id": 604, "q": "ما نوع الفعل في كلمة: كتب؟", "level": 2, "link": "internal://islamicquizapi/6/arabic-language-foundations/604", "section": "اللغة العربية", "answers": [{"answer": "فعل ماض", "t": 1}]},
        {"id": 605, "q": "ما اسم الفاعل من الفعل: كتب؟", "level": 3, "link": "internal://islamicquizapi/6/arabic-language-foundations/605", "section": "اللغة العربية", "answers": [{"answer": "كاتب", "t": 1}]},
        {"id": 606, "q": "ما المثنى من كلمة: كتاب؟", "level": 3, "link": "internal://islamicquizapi/6/arabic-language-foundations/606", "section": "اللغة العربية", "answers": [{"answer": "كتابان", "t": 1}]},
    ],
}


def fetch_islamic_quiz_categories() -> list[IslamicQuizApiCategory]:
    return deepcopy(ISLAMIC_QUIZ_CATEGORIES)


def fetch_islamic_quiz_topics(category_id: int) -> list[IslamicQuizApiTopic]:
    return deepcopy(ISLAMIC_QUIZ_TOPICS_BY_CATEGORY_ID.get(int(category_id), []))


def fetch_islamic_quiz_topic_questions(category_id: int, topic_slug: str) -> list[IslamicQuizApiQuestionRecord]:
    return deepcopy(ISLAMIC_QUIZ_QUESTIONS_BY_CATEGORY_AND_TOPIC.get((int(category_id), str(topic_slug)), []))
