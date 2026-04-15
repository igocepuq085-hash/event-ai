export type EventType = "wedding" | "jubilee";

export type FormField = {
  name: string;
  label: string;
  required?: boolean;
  placeholder?: string;
  textarea?: boolean;
};

export const commonFields: FormField[] = [
  { name: "clientName", label: "Название заявки", required: true, placeholder: "Например: Свадьба Анны и Ивана" },
  { name: "phone", label: "Телефон", placeholder: "+7 ..." },
  { name: "eventDate", label: "Дата события", required: true, placeholder: "2026-06-01" },
  { name: "city", label: "Город", required: true, placeholder: "Сургут" },
  { name: "venue", label: "Площадка / ресторан", required: true, placeholder: "White Hall" },
  { name: "startTime", label: "Время начала / сбор гостей", required: true, placeholder: "18:00" },
  { name: "guestCount", label: "Количество гостей", placeholder: "45" },
  { name: "childrenInfo", label: "Будут ли дети", placeholder: "2 ребенка, 6 и 9 лет" },
  { name: "atmosphere", label: "Атмосфера", textarea: true, placeholder: "Легкая, стильная, с юмором" },
  { name: "fears", label: "Страхи или переживания", textarea: true, placeholder: "Боимся затянутых поздравлений" },
  { name: "hostWishes", label: "Пожелания к ведущему", textarea: true, placeholder: "Легко, интеллигентно, без давления" },
  { name: "references", label: "Референсы по стилю вечера", textarea: true, placeholder: "Современный европейский стиль" },
  { name: "musicLikes", label: "Какая музыка нравится", textarea: true, placeholder: "Поп, инди, хиты 2000-х" },
  { name: "musicBans", label: "Что из музыки нельзя включать", textarea: true, placeholder: "Шансон, жесткий клуб" },
];

export const weddingFields: FormField[] = [
  { name: "groomName", label: "Имя жениха", required: true },
  { name: "brideName", label: "Имя невесты", required: true },
  { name: "weddingTraditions", label: "Какие свадебные традиции нужны", textarea: true },
  { name: "groomParents", label: "Как зовут родителей жениха" },
  { name: "brideParents", label: "Как зовут родителей невесты" },
  { name: "grandparents", label: "Бабушки и дедушки", textarea: true },
  { name: "loveStory", label: "История знакомства", textarea: true },
  { name: "coupleValues", label: "Главные ценности пары", textarea: true },
  { name: "importantDates", label: "Важные даты и события пары", textarea: true },
  { name: "proposalStory", label: "История предложения", textarea: true },
  { name: "nicknames", label: "Как ласково называют друг друга" },
  { name: "insideJokes", label: "Внутренние шутки / фразы / мемы", textarea: true },
  { name: "guestsList", label: "Имена гостей и краткие характеристики", textarea: true },
  { name: "conflictTopics", label: "Конфликтные темы / чувствительные фигуры", textarea: true },
  { name: "likedFormats", label: "Какие форматы / приемы нравятся", textarea: true },
  { name: "keyMoments", label: "Какие 3-5 моментов вечера самые важные", textarea: true },
];

export const jubileeFields: FormField[] = [
  { name: "celebrantName", label: "Имя юбиляра", required: true },
  { name: "celebrantAge", label: "Возраст юбиляра" },
  { name: "anniversaryAtmosphere", label: "Какая атмосфера нужна", textarea: true },
  { name: "familyMembers", label: "Семья юбиляра", textarea: true },
  { name: "biographyStory", label: "Истории, которые можно использовать", textarea: true },
  { name: "achievements", label: "Важные достижения", textarea: true },
  { name: "lifeStages", label: "Важные этапы жизни", textarea: true },
  { name: "characterTraits", label: "Главные качества юбиляра", textarea: true },
  { name: "funnyFacts", label: "Внутренние шутки / любимые фразы / мемы", textarea: true },
  { name: "importantGuests", label: "Важные гости", textarea: true },
  { name: "jubileeConflictTopics", label: "Конфликтные темы / чувствительные фигуры", textarea: true },
  { name: "jubileeLikedFormats", label: "Какие форматы нравятся", textarea: true },
  { name: "whatCannotBeDone", label: "Что нельзя делать на юбилее", textarea: true },
  { name: "keyMoments", label: "Какие 3-5 моментов вечера самые важные", textarea: true },
];

export const initialValues: Record<string, string> = [
  ...commonFields,
  ...weddingFields,
  ...jubileeFields,
].reduce<Record<string, string>>((acc, field) => {
  acc[field.name] = "";
  return acc;
}, {});
