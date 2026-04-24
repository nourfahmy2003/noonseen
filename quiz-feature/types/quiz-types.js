/**
 * @typedef {Object} QuizCategory
 * @property {string} id
 * @property {string} name
 * @property {string} description
 * @property {string} icon
 */

/**
 * @typedef {Object} QuizSubcategory
 * @property {string} id
 * @property {string} categoryId
 * @property {string} name
 * @property {string} description
 * @property {string} icon
 * @property {string|null} flag
 * @property {string} provider
 * @property {string} info
 */

/**
 * @typedef {"easy" | "medium" | "hard"} QuizDifficulty
 */

/**
 * @typedef {Object} QuizOptions
 * @property {QuizDifficulty} difficulty
 * @property {number} amount
 */

/**
 * @typedef {Object} NormalizedQuestion
 * @property {string} id
 * @property {string} text
 * @property {string[]} options
 * @property {number} correctIndex
 * @property {"easy" | "medium" | "hard"} difficulty
 * @property {number} points
 * @property {string} source
 */

/**
 * @typedef {Object} QuizSessionState
 * @property {string|null} categoryId
 * @property {string|null} subcategoryId
 * @property {QuizDifficulty|null} difficulty
 * @property {number|null} amount
 * @property {NormalizedQuestion[]} questions
 */

export const QUIZ_POINTS = {
  easy: 200,
  medium: 400,
  hard: 600,
};

