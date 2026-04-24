import fs from "node:fs";
import path from "node:path";

const projectRoot = process.cwd();
const catalogPath = path.join(
  projectRoot,
  "quiz-feature/config/categoryCatalog.ts"
);
const outputDir = path.join(projectRoot, "quiz-feature/data");
const outputPath = path.join(outputDir, "fake-question-bank.json");

const catalogSource = fs.readFileSync(catalogPath, "utf8");
const lines = catalogSource.split("\n");

const sections = [];
let currentSection = null;
let currentCard = null;
let inSection = false;
let inCard = false;

for (const rawLine of lines) {
  const line = rawLine.trim();

  if (line.startsWith("createSection({")) {
    inSection = true;
    currentSection = { id: "", title: "", description: "", subcategories: [] };
    continue;
  }

  if (line.startsWith("createCard({")) {
    inCard = true;
    currentCard = { id: "", title: "", description: "" };
    continue;
  }

  if (inCard) {
    const idMatch = line.match(/^id:\s*"([^"]+)"/);
    if (idMatch) {
      currentCard.id = idMatch[1];
      continue;
    }

    const titleMatch = line.match(/^title:\s*"([^"]+)"/);
    if (titleMatch) {
      currentCard.title = titleMatch[1];
      continue;
    }

    const descriptionMatch = line.match(/^description:\s*"([^"]+)"/);
    if (descriptionMatch) {
      currentCard.description = descriptionMatch[1];
      continue;
    }

    if (line.startsWith("}),")) {
      if (currentSection && currentCard?.id) {
        currentSection.subcategories.push(currentCard);
      }
      currentCard = null;
      inCard = false;
    }

    continue;
  }

  if (inSection) {
    const idMatch = line.match(/^id:\s*"([^"]+)"/);
    if (idMatch && !currentSection.id) {
      currentSection.id = idMatch[1];
      continue;
    }

    const titleMatch = line.match(/^title:\s*"([^"]+)"/);
    if (titleMatch && !currentSection.title) {
      currentSection.title = titleMatch[1];
      continue;
    }

    const descriptionMatch = line.match(/^description:\s*"([^"]+)"/);
    if (descriptionMatch && !currentSection.description) {
      currentSection.description = descriptionMatch[1];
      continue;
    }

    if (line.startsWith("}),") && currentSection?.subcategories?.length) {
      sections.push(currentSection);
      currentSection = null;
      inSection = false;
    }
  }
}

const difficultyTemplates = [
  { key: "easy", points: 200, slot: 1, label: "سهل" },
  { key: "easy", points: 200, slot: 2, label: "سهل" },
  { key: "medium", points: 400, slot: 1, label: "متوسط" },
  { key: "medium", points: 400, slot: 2, label: "متوسط" },
  { key: "hard", points: 600, slot: 1, label: "صعب" },
  { key: "hard", points: 600, slot: 2, label: "صعب" },
];

const buildQuestion = (section, subcategory, template, index) => {
  const ordinal = index + 1;

  return {
    id: `${subcategory.id}-${template.key}-${ordinal}`,
    points: template.points,
    difficulty: template.key,
    question: `سؤال ${template.label} ${template.slot} في فرع "${subcategory.title}" ضمن قسم "${section.title}": ما الإجابة التجريبية المناسبة لهذا الفرع؟`,
    answer: `إجابة تجريبية ${ordinal} لفرع ${subcategory.title}`,
    options: [
      `إجابة تجريبية ${ordinal} لفرع ${subcategory.title}`,
      `خيار بديل ١ لفرع ${subcategory.title}`,
      `خيار بديل ٢ لفرع ${subcategory.title}`,
      `خيار بديل ٣ لفرع ${subcategory.title}`
    ],
    correctIndex: 0,
    note: subcategory.description
  };
};

const payload = {
  generatedFrom: "quiz-feature/config/categoryCatalog.ts",
  generatedAt: new Date().toISOString(),
  sections: sections.map((section) => ({
    id: section.id,
    title: section.title,
    description: section.description,
    subcategories: section.subcategories.map((subcategory) => ({
      id: subcategory.id,
      title: subcategory.title,
      description: subcategory.description,
      questions: difficultyTemplates.map((template, index) =>
        buildQuestion(section, subcategory, template, index)
      ),
    })),
  })),
};

fs.mkdirSync(outputDir, { recursive: true });
fs.writeFileSync(outputPath, JSON.stringify(payload, null, 2), "utf8");

console.log(`Generated fake question bank at ${outputPath}`);
