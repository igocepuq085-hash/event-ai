"use client";

import { useMemo, useState } from "react";

type EventType = "wedding" | "jubilee";

type QuestionnairePayload = {
  eventType: EventType;
  clientName: string;
  phone: string;
  eventDate: string;
  city: string;
  venue: string;
  startTime: string;
  guestCount: string;
  childrenInfo: string;
  atmosphere: string;
  fears: string;
  hostWishes: string;
  references: string;
  musicLikes: string;
  musicBans: string;
  groomName?: string;
  brideName?: string;
  weddingTraditions?: string;
  groomParents?: string;
  brideParents?: string;
  grandparents?: string;
  loveStory?: string;
  coupleValues?: string;
  importantDates?: string;
  proposalStory?: string;
  nicknames?: string;
  insideJokes?: string;
  guestsList?: string;
  conflictTopics?: string;
  likedFormats?: string;
  keyMoments?: string;
  celebrantName?: string;
  celebrantAge?: string;
  familyMembers?: string;
  anniversaryAtmosphere?: string;
  biographyStory?: string;
  achievements?: string;
  lifeStages?: string;
  characterTraits?: string;
  funnyFacts?: string;
  importantGuests?: string;
  jubileeConflictTopics?: string;
  jubileeLikedFormats?: string;
  whatCannotBeDone?: string;
};

type TextFieldConfig = {
  key: keyof QuestionnairePayload;
  label: string;
  rows?: number;
};

const COMMON_FIELDS: TextFieldConfig[] = [
  { key: "atmosphere", label: "Атмосфера события" },
  { key: "fears", label: "Страхи и переживания клиента" },
  { key: "hostWishes", label: "Пожелания к ведущему" },
  { key: "references", label: "Референсы и ориентиры" },
  { key: "musicLikes", label: "Любимая музыка" },
  { key: "musicBans", label: "Стоп-лист музыки" },
];

const WEDDING_FIELDS: TextFieldConfig[] = [
  { key: "groomName", label: "Имя жениха" },
  { key: "brideName", label: "Имя невесты" },
  { key: "weddingTraditions", label: "Свадебные традиции" },
  { key: "groomParents", label: "Родители жениха" },
  { key: "brideParents", label: "Родители невесты" },
  { key: "grandparents", label: "Бабушки и дедушки" },
  { key: "loveStory", label: "История знакомства", rows: 4 },
  { key: "coupleValues", label: "Ценности пары" },
  { key: "importantDates", label: "Важные даты" },
  { key: "proposalStory", label: "История предложения" },
  { key: "nicknames", label: "Ласковые имена" },
  { key: "insideJokes", label: "Внутренние шутки" },
  { key: "guestsList", label: "Ключевые гости и особенности", rows: 4 },
  { key: "conflictTopics", label: "Чувствительные темы" },
  { key: "likedFormats", label: "Нравящиеся форматы/конкурсы" },
  { key: "keyMoments", label: "3–5 самых важных моментов вечера" },
];

const JUBILEE_FIELDS: TextFieldConfig[] = [
  { key: "celebrantName", label: "Имя юбиляра" },
  { key: "celebrantAge", label: "Возраст юбиляра" },
  { key: "familyMembers", label: "Семья юбиляра" },
  { key: "anniversaryAtmosphere", label: "Атмосфера юбилея" },
  { key: "keyMoments", label: "3–5 самых важных моментов вечера" },
  { key: "biographyStory", label: "Биография и путь" },
  { key: "achievements", label: "Достижения" },
  { key: "lifeStages", label: "Ключевые этапы жизни" },
  { key: "characterTraits", label: "Характер и особенности" },
  { key: "funnyFacts", label: "Факты и любимые фразы" },
  { key: "importantGuests", label: "Важные гости" },
  { key: "jubileeConflictTopics", label: "Чувствительные темы" },
  { key: "jubileeLikedFormats", label: "Нравящиеся форматы" },
  { key: "whatCannotBeDone", label: "Что нельзя делать" },
];

const baseInitial = {
  clientName: "",
  phone: "",
  eventDate: "",
  city: "",
  venue: "",
  startTime: "",
  guestCount: "",
  childrenInfo: "",
  atmosphere: "",
  fears: "",
  hostWishes: "",
  references: "",
  musicLikes: "",
  musicBans: "",
};

const weddingInitial = Object.fromEntries(
  WEDDING_FIELDS.map((field) => [field.key, ""]) as [keyof QuestionnairePayload, string][]
);

const jubileeInitial = Object.fromEntries(
  JUBILEE_FIELDS.map((field) => [field.key, ""]) as [keyof QuestionnairePayload, string][]
);

const emptyStateByType: Record<EventType, QuestionnairePayload> = {
  wedding: {
    eventType: "wedding",
    ...baseInitial,
    ...weddingInitial,
  },
  jubilee: {
    eventType: "jubilee",
    ...baseInitial,
    ...jubileeInitial,
  },
};

export default function QuestionnaireForm({ eventType }: { eventType: EventType }) {
  const [formData, setFormData] = useState<QuestionnairePayload>(
    emptyStateByType[eventType]
  );
  const [submitting, setSubmitting] = useState(false);

  const specificFields = useMemo(
    () => (eventType === "wedding" ? WEDDING_FIELDS : JUBILEE_FIELDS),
    [eventType]
  );

  const onChange =
    (field: keyof QuestionnairePayload) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      setFormData((prev) => ({ ...prev, [field]: e.target.value }));
    };

  const submit = async () => {
    if (!formData.clientName || !formData.phone || !formData.eventDate || !formData.city || !formData.venue) {
      alert("Заполните обязательные поля: имя, телефон, дата, город и площадка.");
      return;
    }

    try {
      setSubmitting(true);
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/questionnaire`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.detail || "Ошибка отправки анкеты");
      alert("Анкета отправлена");
      setFormData(emptyStateByType[eventType]);
    } catch (error) {
      console.error(error);
      alert("Не удалось отправить анкету");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-4">
      <section className="grid gap-3 sm:grid-cols-2">
        <Field label="Имя клиента / название заявки *">
          <input value={formData.clientName} onChange={onChange("clientName")} className={inputClass} />
        </Field>
        <Field label="Телефон *">
          <input value={formData.phone} onChange={onChange("phone")} className={inputClass} />
        </Field>
        <Field label="Дата события *">
          <input type="date" value={formData.eventDate} onChange={onChange("eventDate")} className={inputClass} />
        </Field>
        <Field label="Город *">
          <input value={formData.city} onChange={onChange("city")} className={inputClass} />
        </Field>
        <Field label="Площадка *">
          <input value={formData.venue} onChange={onChange("venue")} className={inputClass} />
        </Field>
        <Field label="Старт / сбор гостей">
          <input value={formData.startTime} onChange={onChange("startTime")} className={inputClass} />
        </Field>
        <Field label="Количество гостей">
          <input value={formData.guestCount} onChange={onChange("guestCount")} className={inputClass} />
        </Field>
        <Field label="Дети на событии">
          <input value={formData.childrenInfo} onChange={onChange("childrenInfo")} className={inputClass} />
        </Field>
      </section>

      {COMMON_FIELDS.map((field) => (
        <Field key={String(field.key)} label={field.label}>
          <Text
            value={(formData[field.key] as string) || ""}
            onChange={onChange(field.key)}
            rows={field.rows ?? 3}
          />
        </Field>
      ))}

      <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
        <div className="mb-3 text-xs uppercase tracking-[0.18em] text-white/50">
          {eventType === "wedding" ? "Блок свадьбы" : "Блок юбилея"}
        </div>

        <div className="space-y-3">
          {specificFields.map((field) => (
            <Field key={String(field.key)} label={field.label}>
              <Text
                value={(formData[field.key] as string) || ""}
                onChange={onChange(field.key)}
                rows={field.rows ?? 3}
              />
            </Field>
          ))}
        </div>
      </div>

      <button
        type="button"
        onClick={submit}
        disabled={submitting}
        className="w-full rounded-full bg-white px-6 py-3 font-medium text-black disabled:opacity-60"
      >
        {submitting ? "Отправка..." : "Отправить анкету"}
      </button>
    </div>
  );
}

const inputClass =
  "mt-1 w-full rounded-xl border border-white/15 bg-black/20 px-3 py-2 text-sm text-white outline-none";

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block text-sm text-white/85">
      {label}
      {children}
    </label>
  );
}

function Text({
  value,
  onChange,
  rows,
}: {
  value: string;
  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  rows: number;
}) {
  return (
    <textarea
      rows={rows}
      value={value}
      onChange={onChange}
      className="mt-1 w-full rounded-xl border border-white/15 bg-black/20 px-3 py-2 text-sm text-white outline-none"
    />
  );
}
