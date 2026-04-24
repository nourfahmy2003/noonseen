import { normalizeQuestionList } from "../normalizers/normalize-question.js";

const API_BASES = {
  general_api: "/api/quiz/general",
  islamic_api: "/api/quiz/islamic",
  countries_api: "/api/quiz/countries",
  wordplay_api: "/api/quiz/wordplay",
};

function buildQuery(params) {
  const query = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== "") {
      query.set(key, String(value));
    }
  });

  return query.toString();
}

export function buildQuizRequestUrl({ provider, categoryId, subcategoryId, difficulty, amount }) {
  const baseUrl = API_BASES[provider];

  if (!baseUrl) {
    throw new Error(`Unknown provider: ${provider}`);
  }

  return `${baseUrl}?${buildQuery({ categoryId, subcategoryId, difficulty, amount })}`;
}

export async function fetchQuizQuestions({ provider, categoryId, subcategoryId, difficulty, amount }) {
  const requestUrl = buildQuizRequestUrl({
    provider,
    categoryId,
    subcategoryId,
    difficulty,
    amount,
  });

  const response = await fetch(requestUrl);

  if (!response.ok) {
    throw new Error("تعذر جلب الأسئلة من المصدر المحدد.");
  }

  const payload = await response.json();
  return normalizeQuestionList(payload.questions ?? [], difficulty, payload.source ?? provider);
}

