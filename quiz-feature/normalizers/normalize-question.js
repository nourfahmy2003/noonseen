import { QUIZ_POINTS } from "../types/quiz-types.js";

export function normalizeQuestion(rawQuestion, difficulty, source) {
  const options = Array.isArray(rawQuestion.options) ? rawQuestion.options : [];
  const correctIndex = Number.isInteger(rawQuestion.correctIndex) ? rawQuestion.correctIndex : 0;

  return {
    id: rawQuestion.id ?? crypto.randomUUID(),
    text: rawQuestion.text ?? rawQuestion.question ?? rawQuestion.prompt ?? "سؤال بدون نص",
    options,
    correctIndex,
    difficulty,
    points: QUIZ_POINTS[difficulty],
    source,
    visual: rawQuestion.visual ?? null,
  };
}

export function normalizeQuestionList(rawQuestions, difficulty, source) {
  return rawQuestions.map((question) => normalizeQuestion(question, difficulty, source));
}
