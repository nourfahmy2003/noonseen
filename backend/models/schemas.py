"""Purpose: define the live-only typed schemas used by quiz preparation and the board."""

from typing import Any, NotRequired, TypedDict


class SelectedSubcategory(TypedDict, total=False):
    category: str
    categoryId: str
    categoryTitle: str
    subcategoryId: str
    subcategoryTitle: str
    imageKey: str
    iconKey: str
    flagCode: str


class FlatCategorySelection(TypedDict, total=False):
    ui_subcategory_id: str
    ui_title_ar: str
    backend_category: str
    imageKey: str
    iconKey: str
    flagCode: str


class InternalQuestion(TypedDict, total=False):
    id: str
    category: str
    difficulty: str
    points: int
    question_ar: str
    answer_ar: str
    source: str
    source_type: str
    metadata: dict[str, Any]
    needs_review: bool


class QuizQuestion(TypedDict, total=False):
    id: str
    points: int
    difficulty: str
    question: str
    answer: str
    displayMode: str
    questionType: NotRequired[str]
    visual: NotRequired[dict[str, Any]]
    source: NotRequired[str]
    sourceType: NotRequired[str]
    metadata: NotRequired[dict[str, Any]]


class QuizCategory(TypedDict, total=False):
    id: str
    name: str
    backendCategory: str
    icon: str
    imageKey: str
    iconKey: str
    flagCode: str
    description: str
    questions: list[QuizQuestion]
    sourceMode: str
    resolvedSource: str
    sourceType: str


class QuizDiagnostic(TypedDict, total=False):
    id: str
    name: str
    backendCategory: str
    sourceMode: str
    questionCount: int
    source: str
    sourceType: str
    reason: str


class SourceDefinition(TypedDict, total=False):
    backend_category: str
    client_key: str
    source: str
    source_type: str
    requires_auth: bool
    mode: str
    pool: str


class IslamicQuizApiTopic(TypedDict, total=False):
    slug: str
    name: str
    description: str


class IslamicQuizApiCategory(TypedDict, total=False):
    id: int
    arabicName: str
    englishName: str
    description: str
    topics: list[IslamicQuizApiTopic]


class IslamicQuizApiAnswer(TypedDict, total=False):
    answer: str
    t: int


class IslamicQuizApiQuestionRecord(TypedDict, total=False):
    id: int
    q: str
    level: int
    link: str
    section: str
    answers: list[IslamicQuizApiAnswer]


class NormalizedCountry(TypedDict):
    name: str
    common_name: str
    capital: str | None
    currency_codes: list[str]
    currency_names: list[str]
    languages: list[str]
    flag: str
    flag_svg: str
    cca2: str
    cca3: str
    region: str
    subregion: str
    population: int
    continents: list[str]
    borders: list[str]
    timezones: list[str]
    maps: dict[str, Any]
    start_of_week: str
    car_side: str
    landlocked: bool
    area: float | int
    independent: bool | None
    un_member: bool | None


class WallaKelmaPrompt(TypedDict, total=False):
    id: str
    mode: str
    category: str
    difficulty: str
    secret_value: str
    secret_value_ar: str
    display_hint_ar: str
    source: str
    source_type: str
    metadata: dict[str, Any]
    is_private: bool


class WallaKelmaPublicPayload(TypedDict, total=False):
    token: str
    category: str
    difficulty: str
    status: str
    api_base_url: str
    qr_path: str
    qr_url: str
    expires_at: int


class WallaKelmaPrivatePayload(TypedDict, total=False):
    token: str
    category: str
    difficulty: str
    secret_value: str
    secret_value_ar: str
    display_hint_ar: str
    source: str
    source_type: str
    metadata: dict[str, Any]
    expires_at: int
