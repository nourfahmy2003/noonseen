import { readStorage, removeStorage, writeStorage } from "../utils/storage.js";

const QUIZ_SESSION_KEY = "quiz-feature-session";

const initialState = {
  categoryId: null,
  subcategoryId: null,
  difficulty: null,
  amount: null,
  questions: [],
};

export function getQuizSession() {
  return readStorage(QUIZ_SESSION_KEY, initialState);
}

export function saveQuizSession(partialState) {
  const nextState = {
    ...getQuizSession(),
    ...partialState,
  };

  writeStorage(QUIZ_SESSION_KEY, nextState);
  return nextState;
}

export function clearQuizSession() {
  removeStorage(QUIZ_SESSION_KEY);
}

export function clearQuizQuestions() {
  return saveQuizSession({ questions: [] });
}

