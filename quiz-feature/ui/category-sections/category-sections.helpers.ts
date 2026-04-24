import { apiSourceMap } from "../../config/sourceMap";

const iconMap: Record<string, string> = {
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
};

export const apiSourceLookup = new Map(
  apiSourceMap.map((source) => [source.key, source])
);

export const getPlaceholderIcon = (
  imageKey?: string,
  iconKey?: string
): string => {
  if (iconKey && iconMap[iconKey]) {
    return iconMap[iconKey];
  }

  if (imageKey) {
    const normalized = imageKey.toLowerCase();
    if (normalized.includes("quran")) return "📖";
    if (normalized.includes("football")) return "⚽";
    if (normalized.includes("country")) return "🌍";
    if (normalized.includes("anime")) return "🌀";
    if (normalized.includes("history")) return "🏛️";
    if (normalized.includes("animal")) return "🦁";
  }

  return "✨";
};

export const getVisualAccent = (seed = ""): string => {
  const palette = [
    "#7FB7FF",
    "#8FD0F6",
    "#A6C7FF",
    "#9ED7D3",
    "#A6D0F5",
    "#B3C2FF",
  ];

  let hash = 0;
  for (let index = 0; index < seed.length; index += 1) {
    hash = (hash + seed.charCodeAt(index) * (index + 1)) % palette.length;
  }

  return palette[hash];
};

export const flagCodeToEmoji = (flagCode: string): string => {
  const normalized = flagCode.trim().toUpperCase();

  if (!/^[A-Z]{2}$/.test(normalized)) {
    return "🏳️";
  }

  return String.fromCodePoint(
    ...normalized.split("").map((char) => 127397 + char.charCodeAt(0))
  );
};
