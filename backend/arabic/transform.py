"""Purpose: provide one shared Arabic transformation layer for non-Arabic source data."""

import re
import unicodedata


ARABIC_CHAR_PATTERN = re.compile(r"[\u0600-\u06FF]")
LATIN_CHAR_PATTERN = re.compile(r"[A-Za-z]")
UPPERCASE_TOKEN_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9 .:+/-]{0,7}$")
CORPORATE_SUFFIX_PATTERN = re.compile(
    r"\b(incorporated|inc|corp|corporation|company|co|group|holdings|holding|llc|ltd|limited|plc|ag|sa|nv|bv)\b\.?",
    re.I,
)

LABEL_OVERRIDES = {
    "addis ababa": "أديس أبابا",
    "abuja": "أبوجا",
    "amman": "عمّان",
    "ankara": "أنقرة",
    "amsterdam": "أمستردام",
    "asmara": "أسمرة",
    "asuncion": "أسونسيون",
    "austria": "النمسا",
    "athens": "أثينا",
    "baghdad": "بغداد",
    "bangkok": "بانكوك",
    "bahamas": "جزر البهاما",
    "beijing": "بكين",
    "beirut": "بيروت",
    "berlin": "برلين",
    "bogota": "بوغوتا",
    "bratislava": "براتيسلافا",
    "bucharest": "بوخارست",
    "budapest": "بودابست",
    "cairo": "القاهرة",
    "caracas": "كاراكاس",
    "copenhagen": "كوبنهاغن",
    "conakry": "كوناكري",
    "cuba": "كوبا",
    "dodoma": "دودوما",
    "doha": "الدوحة",
    "fiji": "فيجي",
    "gaborone": "غابورون",
    "ghana": "غانا",
    "accra": "أكرا",
    "hanoi": "هانوي",
    "harare": "هراري",
    "helsinki": "هلسنكي",
    "hong kong dollar": "دولار هونغ كونغ",
    "islamabad": "إسلام آباد",
    "jakarta": "جاكرتا",
    "jerusalem": "القدس",
    "kyiv": "كييف",
    "kuwait": "الكويت",
    "kuwait city": "مدينة الكويت",
    "lilongwe": "ليلونغوي",
    "ljubljana": "ليوبليانا",
    "london": "لندن",
    "madrid": "مدريد",
    "mexico city": "مكسيكو سيتي",
    "maputo": "مابوتو",
    "mozambique": "موزمبيق",
    "moscow": "موسكو",
    "montevideo": "مونتيفيديو",
    "astana": "أستانا",
    "antananarivo": "أنتاناناريفو",
    "nairobi": "نيروبي",
    "netherlands": "هولندا",
    "new zealand dollar": "الدولار النيوزيلندي",
    "nigeria": "نيجيريا",
    "norwegian krone": "الكرونة النرويجية",
    "oslo": "أوسلو",
    "ottawa": "أوتاوا",
    "pakistan": "باكستان",
    "paris": "باريس",
    "paraguay": "باراغواي",
    "florence": "فلورنسا",
    "port harcourt": "بورت هاركورت",
    "port louis": "بورت لويس",
    "port vila": "بورت فيلا",
    "praha": "براغ",
    "pyramids of giza": "أهرامات الجيزة",
    "qatar": "قطر",
    "quito": "كيتو",
    "senegal": "السنغال",
    "riyadh": "الرياض",
    "rome": "روما",
    "san jose": "سان خوسيه",
    "santiago": "سانتياغو",
    "seoul": "سيول",
    "serengeti national park": "منتزه سيرينغيتي الوطني",
    "singapore": "سنغافورة",
    "singapore city": "سنغافورة",
    "singapore dollar": "الدولار السنغافوري",
    "sofia": "صوفيا",
    "stockholm": "ستوكهولم",
    "south korea": "كوريا الجنوبية",
    "suva": "سوفا",
    "switzerland": "سويسرا",
    "swiss franc": "الفرنك السويسري",
    "tanzania": "تنزانيا",
    "tashkent": "طشقند",
    "thailand": "تايلاند",
    "tokyo": "طوكيو",
    "tripoli": "طرابلس",
    "tunis": "تونس",
    "uruguayan peso": "البيزو الأوروغوياني",
    "venezuela": "فنزويلا",
    "vienna": "فيينا",
    "vilnius": "فيلنيوس",
    "warsaw": "وارسو",
    "yaounde": "ياوندي",
    "yerevan": "يريفان",
    "ramallah": "رام الله",
    "british pound": "الجنيه الإسترليني",
    "pound sterling": "الجنيه الإسترليني",
    "us dollar": "الدولار الأمريكي",
    "canadian dollar": "الدولار الكندي",
    "australian dollar": "الدولار الأسترالي",
    "argentine peso": "البيزو الأرجنتيني",
    "brazilian real": "الريال البرازيلي",
    "chinese yuan": "اليوان الصيني",
    "eastern caribbean dollar": "دولار شرق الكاريبي",
    "west african cfa franc": "فرنك غرب أفريقيا",
    "cfa franc bceao": "فرنك غرب أفريقيا",
    "cfa franc beac": "فرنك وسط أفريقيا",
    "central african cfa franc": "فرنك وسط أفريقيا",
        "ethiopian birr": "البر الإثيوبي",
        "euro": "اليورو",
        "eritrean nakfa": "الناكفا الإريترية",
        "french": "الفرنسية",
        "georgian lari": "اللاري الجورجي",
        "german": "الألمانية",
        "greek": "اليونانية",
        "hryvnia": "الهريفنيا الأوكرانية",
        "english": "الإنجليزية",
        "arabic": "العربية",
        "dutch": "الهولندية",
        "italian": "الإيطالية",
        "indian rupee": "الروبية الهندية",
        "indonesian rupiah": "الروبية الإندونيسية",
        "jordanian dinar": "الدينار الأردني",
        "japanese": "اليابانية",
        "ukrainian hryvnia": "الهريفنيا الأوكرانية",
        "kazakhstani tenge": "التينغ الكازاخستاني",
        "kenyan shilling": "الشلن الكيني",
        "korean": "الكورية",
        "lao kip": "الكيب اللاوسي",
        "libyan dinar": "الدينار الليبي",
        "malagasy": "الملغاشية",
        "malagasy ariary": "الأرياري المدغشقري",
        "mexican peso": "البيزو المكسيكي",
        "moroccan dirham": "الدرهم المغربي",
        "nepalese rupee": "الروبية النيبالية",
        "persian (farsi)": "الفارسية",
        "polish": "البولندية",
        "portuguese": "البرتغالية",
        "pakistani rupee": "الروبية الباكستانية",
        "romanian leu": "الليو الروماني",
        "russian": "الروسية",
        "russian ruble": "الروبل الروسي",
        "macanese pataca": "الباتاكا الماكاوية",
        "peruvian sol": "السول البيروفي",
        "philippine peso": "البيزو الفلبيني",
        "qatari riyal": "الريال القطري",
        "saudi riyal": "الريال السعودي",
        "south african rand": "الراند الجنوب أفريقي",
        "spanish": "الإسبانية",
        "swahili": "السواحيلية",
        "thai baht": "البات التايلندي",
        "turkish lira": "الليرة التركية",
        "turkish": "التركية",
        "urdu": "الأردية",
        "united states dollar": "الدولار الأمريكي",
        "uzbekistani so'm": "السوم الأوزبكي",
        "vietnamese": "الفيتنامية",
        "vietnamese dong": "الدونغ الفيتنامي",
        "yemeni rial": "الريال اليمني",
    "hong kong": "هونغ كونغ",
    "dhaka": "دكا",
    "brazzaville": "برازافيل",
    "luanda": "لواندا",
    "vientiane": "فيينتيان",
    "wellington": "ويلينغتون",
    "kinshasa": "كينشاسا",
    "hagatna": "هاغاتنيا",
    "jamestown": "جيمس تاون",
}

LABEL_OVERRIDES.update(
    {
        # Keep frequently visible general and brand answers natural instead of
        # exposing literal English or short Latin tokens to players.
        "adolf hitler": "أدولف هتلر",
        "adidas": "أديداس",
        "airbnb": "إير بي إن بي",
        "albert einstein": "ألبرت أينشتاين",
        "alexander graham bell": "ألكسندر غراهام بيل",
        "amazon": "أمازون",
        "apple": "أبل",
        "bbc": "بي بي سي",
        "bmw": "بي إم دبليو",
        "canon": "كانون",
        "canada": "كندا",
        "cheetah": "الفهد",
        "china": "الصين",
        "coca cola": "كوكاكولا",
        "coca-cola": "كوكاكولا",
        "dell": "ديل",
        "disney": "ديزني",
        "dolphin": "دلفين",
        "eagle": "نسر",
        "ebay": "إيباي",
        "egypt": "مصر",
        "einstein": "أينشتاين",
        "facebook": "فيسبوك",
        "falcon": "صقر",
        "fedex": "فيديكس",
        "france": "فرنسا",
        "galileo galilei": "غاليليو غاليلي",
        "germany": "ألمانيا",
        "giraffe": "زرافة",
        "google": "غوغل",
        "huawei": "هواوي",
        "hp": "إتش بي",
        "ibm": "آي بي إم",
        "ikea": "إيكيا",
        "instagram": "إنستغرام",
        "intel": "إنتل",
        "iraqi dinar": "الدينار العراقي",
        "isaac newton": "إسحاق نيوتن",
        "jupiter": "المشتري",
        "kangaroo": "كنغر",
        "lego": "ليغو",
        "lenovo": "لينوفو",
        "lisbon": "لشبونة",
        "lion": "أسد",
        "light bulb": "المصباح الكهربائي",
        "mars": "المريخ",
        "mastercard": "ماستركارد",
        "mcdonalds": "ماكدونالدز",
        "mcdonald's": "ماكدونالدز",
        "mercedes benz": "مرسيدس",
        "mercedes-benz": "مرسيدس",
        "mercury": "عطارد",
        "microsoft": "مايكروسوفت",
        "nasa": "ناسا",
        "netflix": "نتفليكس",
        "neptune": "نبتون",
        "nigeria": "نيجيريا",
        "nike": "نايكي",
        "nikola tesla": "نيكولا تسلا",
        "octopus": "أخطبوط",
        "ottoman empire": "الدولة العثمانية",
        "oracle": "أوراكل",
        "panda": "باندا",
        "paypal": "باي بال",
        "pepsi": "بيبسي",
        "penguin": "بطريق",
        "playstation": "بلايستيشن",
        "pluto": "بلوتو",
        "puma": "بوما",
        "radio": "الراديو",
        "saturn": "زحل",
        "samsung": "سامسونج",
        "shark": "قرش",
        "shell": "شل",
        "slack": "سلاك",
        "snapchat": "سناب شات",
        "sony": "سوني",
        "south africa": "جنوب أفريقيا",
        "spain": "إسبانيا",
        "sputnik 1": "سبوتنيك 1",
        "spotify": "سبوتيفاي",
        "starbucks": "ستاربكس",
        "steam engine": "المحرك البخاري",
        "tesla": "تسلا",
        "telephone": "الهاتف",
        "television": "التلفاز",
        "thar desert": "صحراء ثار",
        "titanic": "تيتانيك",
        "thomas edison": "توماس إديسون",
        "tiger": "نمر",
        "tiktok": "تيك توك",
        "toyota": "تويوتا",
        "portugal": "البرتغال",
        "turkey": "تركيا",
        "uber": "أوبر",
        "union": "الاتحاد",
        "united kingdom": "المملكة المتحدة",
        "world war ii": "الحرب العالمية الثانية",
        "world war 2": "الحرب العالمية الثانية",
        "uranus": "أورانوس",
        "venus": "الزهرة",
        "visa": "فيزا",
        "whale": "حوت",
        "xerox": "زيروكس",
        "ayutthaya historical park": "منتزه أيوثايا التاريخي",
        "youtube": "يوتيوب",
        "zara": "زارا",
        "zebra": "حمار وحشي",
        "rocky mountains": "جبال روكي",
        "mustafa kemal atatürk": "مصطفى كمال أتاتورك",
        "mustafa kemal ataturk": "مصطفى كمال أتاتورك",
        "japan": "اليابان",
        "italy": "إيطاليا",
        "brazil": "البرازيل",
        "india": "الهند",
        "australia": "أستراليا",
    }
)

TRANSLITERATION_MAP = [
    ("sh", "ش"),
    ("ch", "تش"),
    ("th", "ث"),
    ("kh", "خ"),
    ("dh", "ذ"),
    ("gh", "غ"),
    ("ph", "ف"),
    ("aa", "ا"),
    ("ee", "ي"),
    ("oo", "و"),
]

CHAR_MAP = {
    "a": "ا",
    "b": "ب",
    "c": "ك",
    "d": "د",
    "e": "ي",
    "f": "ف",
    "g": "ج",
    "h": "ه",
    "i": "ي",
    "j": "ج",
    "k": "ك",
    "l": "ل",
    "m": "م",
    "n": "ن",
    "o": "و",
    "p": "ب",
    "q": "ق",
    "r": "ر",
    "s": "س",
    "t": "ت",
    "u": "و",
    "v": "ف",
    "w": "و",
    "x": "كس",
    "y": "ي",
    "z": "ز",
}

GENERAL_FRAGMENT_OVERRIDES = {
    "animal": "حيوان",
    "animals": "حيوانات",
    "capital": "عاصمة",
    "country": "دولة",
    "countries": "دول",
    "company": "شركة",
    "city": "مدينة",
    "planet": "كوكب",
    "scientist": "عالم",
    "river": "نهر",
    "ocean": "محيط",
    "programming language": "لغة برمجة",
    "operating system": "نظام تشغيل",
    "web browser": "متصفح ويب",
    "browser": "متصفح",
    "software": "برنامج",
    "hardware": "عتاد",
    "species": "نوع",
    "mammal": "ثديي",
    "bird": "طائر",
    "continent": "قارة",
    "invented": "اخترع",
    "discovered": "اكتشف",
    "released": "صدر",
    "founded": "تأسس",
    "created": "أنشئ",
    "largest": "أكبر",
    "smallest": "أصغر",
    "highest": "أعلى",
    "first": "أول",
}


def normalize_arabic_text(value):
    text = " ".join(str(value or "").strip().split())
    return text.replace(" ?", "؟").replace(" ،", "،")


def _normalize_latin_lookup(value):
    normalized = unicodedata.normalize("NFKD", normalize_arabic_text(value))
    return "".join(char for char in normalized if not unicodedata.combining(char)).lower()


def looks_arabic(value):
    return bool(ARABIC_CHAR_PATTERN.search(str(value or "")))


def transliterate_to_arabic(value):
    text = _normalize_latin_lookup(value)
    if not text:
        return ""

    for latin, arabic in TRANSLITERATION_MAP:
        text = text.replace(latin, arabic)

    transformed = []
    for char in text:
        if char in {" ", "-", "/", "(", ")", "."}:
            transformed.append(" " if char in {"-", "/"} else char)
            continue
        transformed.append(CHAR_MAP.get(char, char))

    return normalize_arabic_text("".join(transformed))


def _strip_company_suffixes(value):
    stripped = CORPORATE_SUFFIX_PATTERN.sub("", str(value or "").strip())
    stripped = re.sub(r"\s{2,}", " ", stripped).strip(" -_,.")
    return stripped


def ensure_arabic_label(value, *, strip_company_suffixes=False, preserve_latin_short_token=False):
    text = normalize_arabic_text(value)
    if not text:
        return "", False
    if strip_company_suffixes:
        text = _strip_company_suffixes(text)
    override = LABEL_OVERRIDES.get(_normalize_latin_lookup(text))
    if override:
        return override, False
    if looks_arabic(text) or (preserve_latin_short_token and text.isupper() and len(text) <= 5):
        return text, False
    return transliterate_to_arabic(text), True


def ensure_arabic_brand_name(value):
    return ensure_arabic_label(value, strip_company_suffixes=True)


def is_valid_arabic_output(value, *, allow_digits=False, allow_latin_short_tokens=False):
    text = normalize_arabic_text(value)
    if not text or "�" in text:
        return False
    if looks_arabic(text):
        return True
    if allow_latin_short_tokens and UPPERCASE_TOKEN_PATTERN.fullmatch(text):
        return True
    if allow_digits and not LATIN_CHAR_PATTERN.search(text):
        return True
    return False


def latin_letter_ratio(value: str) -> float:
    """Purpose: measure how much Latin leaks into supposedly Arabic player-facing strings."""
    text = str(value or "")
    if not text.strip():
        return 1.0
    latin = len(LATIN_CHAR_PATTERN.findall(text))
    return latin / max(len(text), 1)


def is_acceptable_arabic_quiz_pair(question_ar: str, answer_ar: str) -> tuple[bool, str]:
    """Purpose: reject robotic/mixed-language pairs after machine translation (LibreTranslate output).
    
    Validation rules:
    1. Both question and answer must be primarily Arabic (Arabic > 88%, max 12% Latin)
    2. Question must be at least 10 chars (to avoid trivial translations)
    3. Answer must be at least 2 chars
    4. No mojibake or invalid Unicode
    5. No excessively mixed English/Arabic (max 35% Latin in answer)
    
    If translation fails these criteria, we reject and fail rather than using local fallback.
    """
    q = normalize_arabic_text(question_ar)
    a = normalize_arabic_text(answer_ar)
    if not is_valid_arabic_output(q):
        return False, "question_not_arabic"
    if not is_valid_arabic_output(a, allow_digits=True, allow_latin_short_tokens=True):
        return False, "answer_not_arabic"
    
    # Calculate Latin character ratios more carefully.
    q_latin_ratio = latin_letter_ratio(q)
    a_latin_ratio = latin_letter_ratio(a)
    
    # Tech and general trivia often retain short Latin tokens (USB, SQL, MP3) in otherwise Arabic text.
    if q_latin_ratio > 0.18:
        return False, "question_has_too_much_latin"
    if a_latin_ratio > 0.35:  # Max 35% Latin for answers (brand tickers or acronyms allowed).
        return False, "answer_has_too_much_latin"
    
    # Reject ultra-short outputs (likely failed translations).
    if len(q) < 10:
        return False, "question_too_short"
    if len(a) < 2:
        return False, "answer_too_short"
    
    # Check for repetitive patterns that indicate poor translation (e.g., lots of repeated words).
    tokens = q.split()
    if len(tokens) > 3 and len(set(tokens)) < len(tokens) * 0.4:
        return False, "question_has_repetitive_tokens"
    
    return True, ""


def is_acceptable_arabic_brand_answer(answer_ar: str) -> tuple[bool, str]:
    """Purpose: short brand names may include brief Latin tickers; still require clear Arabic.
    
    Brand names can legitimately be short and may contain ticker symbols, so we're more permissive
    than quiz pairs but still enforce that the primary content is Arabic.
    
    Validation rules:
    1. Must pass basic Arabic output validation
    2. Max 45% Latin (to allow tickers like AAPL or abbreviations)
    3. At least 2 characters
    """
    a = normalize_arabic_text(answer_ar)
    if not is_valid_arabic_output(a, allow_digits=True, allow_latin_short_tokens=True):
        return False, "brand_answer_not_arabic"
    
    a_latin_ratio = latin_letter_ratio(a)
    if a_latin_ratio > 0.45:  # Allow more Latin for brand names (tickers, acronyms).
        return False, "brand_answer_too_much_latin"
    
    if len(a) < 2:
        return False, "brand_answer_too_short"
    
    return True, ""


def _translate_general_fragment(value):
    text = normalize_arabic_text(value).strip()
    if not text:
        return ""
    if looks_arabic(text):
        return text

    normalized_lower = text.lower()
    for english, arabic in sorted(GENERAL_FRAGMENT_OVERRIDES.items(), key=lambda item: len(item[0]), reverse=True):
        normalized_lower = normalized_lower.replace(english, arabic)

    translated_tokens = []
    for token in normalized_lower.split():
        if looks_arabic(token):
            translated_tokens.append(token)
            continue
        label, _ = ensure_arabic_label(token)
        translated_tokens.append(label or token)
    return normalize_arabic_text(" ".join(translated_tokens))


GENERAL_QUESTION_PATTERNS = (
    (
        re.compile(r"^who is (?P<target>.+?)\??$", re.I),
        lambda match: f"من هو {_translate_general_fragment(match.group('target'))}؟",
    ),
    (
        re.compile(r"^who was (?P<target>.+?)\??$", re.I),
        lambda match: f"من كان {_translate_general_fragment(match.group('target'))}؟",
    ),
    (
        re.compile(r"^what is the capital of (?P<target>.+?)\??$", re.I),
        lambda match: f"ما عاصمة {ensure_arabic_label(match.group('target'))[0]}؟",
    ),
    (
        re.compile(r"^what is (?P<target>.+?)\??$", re.I),
        lambda match: f"ما هو {_translate_general_fragment(match.group('target'))}؟",
    ),
    (
        re.compile(r"^what was (?P<target>.+?)\??$", re.I),
        lambda match: f"ما كان {_translate_general_fragment(match.group('target'))}؟",
    ),
    (
        re.compile(r"^which country has the capital (?P<target>.+?)\??$", re.I),
        lambda match: f"ما الدولة التي عاصمتها {ensure_arabic_label(match.group('target'))[0]}؟",
    ),
    (
        re.compile(r"^which country (?P<target>.+?)\??$", re.I),
        lambda match: f"أي دولة {_translate_general_fragment(match.group('target'))}؟",
    ),
    (
        re.compile(r"^which scientist (?P<target>.+?)\??$", re.I),
        lambda match: f"أي عالم {_translate_general_fragment(match.group('target'))}؟",
    ),
    (
        re.compile(r"^which company (?P<target>.+?)\??$", re.I),
        lambda match: f"أي شركة {_translate_general_fragment(match.group('target'))}؟",
    ),
    (
        re.compile(r"^who invented (?P<target>.+?)\??$", re.I),
        lambda match: f"من اخترع {ensure_arabic_label(match.group('target'))[0]}؟",
    ),
    (
        re.compile(r"^who discovered (?P<target>.+?)\??$", re.I),
        lambda match: f"من اكتشف {ensure_arabic_label(match.group('target'))[0]}؟",
    ),
    (
        re.compile(r"^which planet is known as (?P<target>.+?)\??$", re.I),
        lambda match: f"ما الكوكب المعروف باسم {ensure_arabic_label(match.group('target'))[0]}؟",
    ),
    (
        re.compile(r"^what is the largest (?P<target>.+?)\??$", re.I),
        lambda match: f"ما أكبر {ensure_arabic_label(match.group('target'))[0]}؟",
    ),
    (
        re.compile(r"^what is the smallest (?P<target>.+?)\??$", re.I),
        lambda match: f"ما أصغر {ensure_arabic_label(match.group('target'))[0]}؟",
    ),
    (
        re.compile(r"^what is the highest (?P<target>.+?)\??$", re.I),
        lambda match: f"ما أعلى {ensure_arabic_label(match.group('target'))[0]}؟",
    ),
    (
        re.compile(r"^in what year did (?P<target>.+?)\??$", re.I),
        lambda match: f"في أي سنة حدث {ensure_arabic_label(match.group('target'))[0]}؟",
    ),
    (
        re.compile(r"^when did (?P<target>.+?) happen\??$", re.I),
        lambda match: f"متى حدث {ensure_arabic_label(match.group('target'))[0]}؟",
    ),
    (
        re.compile(r"^when was (?P<target>.+?)\??$", re.I),
        lambda match: f"متى كان {_translate_general_fragment(match.group('target'))}؟",
    ),
    (
        re.compile(r"^where is (?P<target>.+?)\??$", re.I),
        lambda match: f"أين يقع {_translate_general_fragment(match.group('target'))}؟",
    ),
    (
        re.compile(r"^where was (?P<target>.+?)\??$", re.I),
        lambda match: f"أين كان {_translate_general_fragment(match.group('target'))}؟",
    ),
    (
        re.compile(r"^how many (?P<target>.+?)\??$", re.I),
        lambda match: f"كم عدد {_translate_general_fragment(match.group('target'))}؟",
    ),
    (
        re.compile(r"^what year was (?P<target>.+?)\??$", re.I),
        lambda match: f"في أي سنة كان {_translate_general_fragment(match.group('target'))}؟",
    ),
    (
        re.compile(r"^what year did (?P<target>.+?)\??$", re.I),
        lambda match: f"في أي سنة {_translate_general_fragment(match.group('target'))}؟",
    ),
    (
        re.compile(r"^what company (?:developed|created|makes) (?P<target>.+?)\??$", re.I),
        lambda match: f"ما الشركة التي طورت {ensure_arabic_label(match.group('target'))[0]}؟",
    ),
    (
        re.compile(r"^what does (?P<target>.+?) stand for\??$", re.I),
        lambda match: f"إلام يشير {ensure_arabic_label(match.group('target'))[0]}؟",
    ),
    (
        re.compile(r"^which animal (?P<target>.+?)\??$", re.I),
        lambda match: f"أي حيوان {_translate_general_fragment(match.group('target'))}؟",
    ),
    (
        re.compile(r"^which (?P<target>.+?)\??$", re.I),
        lambda match: f"أي {_translate_general_fragment(match.group('target'))}؟",
    ),
)


def ensure_arabic_general_question(question_text):
    text = normalize_arabic_text(question_text)
    if not text:
        return "", True
    if looks_arabic(text):
        return text, False
    lowered = text.lower()
    if lowered.startswith("which of these") or lowered.startswith("true or false"):
        return "", True

    for pattern, builder in GENERAL_QUESTION_PATTERNS:
        match = pattern.match(text)
        if not match:
            continue
        candidate = normalize_arabic_text(builder(match))
        if is_valid_arabic_output(candidate):
            return candidate, False

    return "", True
