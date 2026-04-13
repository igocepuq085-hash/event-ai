"use client";

import { ChangeEvent, useEffect, useMemo, useState } from "react";

const STORAGE_KEY = "event-questionnaire-full-v3";
const TOTAL_STEPS = 8;

const eventTypes = [
  {
    id: "wedding",
    title: "Свадьба",
    description: "Романтика, история пары, атмосфера и эмоции вечера.",
    accent: "from-amber-200/30 via-white/10 to-transparent",
    badge: "романтика и эстетика",
    background:
      "bg-[radial-gradient(circle_at_top,rgba(255,220,180,0.22),transparent_28%),radial-gradient(circle_at_bottom,rgba(255,255,255,0.10),transparent_22%),linear-gradient(180deg,#120f12_0%,#07070b_100%)]",
    heroTitle: "Создадим красивую и тонко настроенную свадебную анкету",
    heroSubtitle:
      "Соберем атмосферу, важные смыслы, историю пары и деликатные детали, чтобы праздник получился живым, стильным и очень личным.",
    heroPoints: [
      "история пары и ключевые смыслы",
      "тональность, эстетика и эмоции",
      "бережная работа с гостями",
    ],
  },
  {
    id: "birthday",
    title: "День рождения",
    description: "Личный праздник с акцентом на характер, стиль и настроение.",
    accent: "from-fuchsia-300/30 via-white/10 to-transparent",
    badge: "личный и яркий формат",
    background:
      "bg-[radial-gradient(circle_at_top,rgba(255,120,220,0.20),transparent_28%),radial-gradient(circle_at_bottom,rgba(120,220,255,0.12),transparent_24%),linear-gradient(180deg,#100712_0%,#07070b_100%)]",
    heroTitle: "Соберем настроение яркого личного праздника",
    heroSubtitle:
      "Поможем заранее уловить характер именинника, стиль гостей, уместный юмор и тот вайб, который должен остаться после вечера.",
    heroPoints: [
      "характер главного героя вечера",
      "юмор, сюрпризы и личные акценты",
      "динамика и впечатление гостей",
    ],
  },
  {
    id: "anniversary",
    title: "Юбилей",
    description: "Торжественный формат с уважением к истории и значимости события.",
    accent: "from-emerald-300/25 via-white/10 to-transparent",
    badge: "торжественно и статусно",
    background:
      "bg-[radial-gradient(circle_at_top,rgba(120,255,190,0.18),transparent_28%),radial-gradient(circle_at_bottom,rgba(255,255,255,0.08),transparent_24%),linear-gradient(180deg,#08110d_0%,#07070b_100%)]",
    heroTitle: "Настроим торжественный вечер с уважением к истории человека",
    heroSubtitle:
      "Здесь важно соединить тепло, статус, память о пути и правильную эмоциональную интонацию без перегруза и банальности.",
    heroPoints: [
      "уважение к пути и достижениям",
      "статусная, но теплая подача",
      "бережный темп и правильные акценты",
    ],
  },
  {
    id: "corporate",
    title: "Корпоратив",
    description: "Современная подача с учетом состава гостей и динамики вечера.",
    accent: "from-cyan-300/25 via-white/10 to-transparent",
    badge: "современно и собранно",
    background:
      "bg-[radial-gradient(circle_at_top,rgba(120,220,255,0.18),transparent_28%),radial-gradient(circle_at_bottom,rgba(255,255,255,0.08),transparent_24%),linear-gradient(180deg,#071018_0%,#07070b_100%)]",
    heroTitle: "Соберем современный корпоративный сценарий без кринжа",
    heroSubtitle:
      "Продумываем баланс между статусом, драйвом, вовлечением команды и корректной подачей для разной аудитории внутри компании.",
    heroPoints: [
      "баланс формальности и легкости",
      "адекватный юмор для команды и руководства",
      "динамика без устаревших форматов",
    ],
  },
  {
    id: "private",
    title: "Частное событие",
    description: "Индивидуальный формат с акцентом на ваши личные пожелания.",
    accent: "from-violet-300/25 via-white/10 to-transparent",
    badge: "индивидуальный формат",
    background:
      "bg-[radial-gradient(circle_at_top,rgba(180,140,255,0.18),transparent_28%),radial-gradient(circle_at_bottom,rgba(255,255,255,0.08),transparent_24%),linear-gradient(180deg,#0d0916_0%,#07070b_100%)]",
    heroTitle: "Сформируем анкету под ваш уникальный формат события",
    heroSubtitle:
      "Если у вас нестандартное мероприятие, анкета поможет собрать все нюансы, ограничения, пожелания и ощущения, на которых будет строиться вечер.",
    heroPoints: [
      "индивидуальный стиль события",
      "гибкая логика под ваш формат",
      "акцент на деталях и атмосфере",
    ],
  },
];

const hostStyles = [
  "Легкий и современный",
  "Интеллигентный и сдержанный",
  "Яркий и энергичный",
  "Теплый и душевный",
  "Статусный и элегантный",
];

const humorOptions = [
  "Легкий и уместный",
  "Умеренный, без перегибов",
  "Минимально",
  "Вообще не нужен",
];

const tempoOptions = [
  "Спокойный и камерный",
  "Средний и сбалансированный",
  "Динамичный и насыщенный",
  "Шоу-формат с активной подачей",
];

const interactionOptions = [
  "Нужны активные интерактивы",
  "Лучше мягкое вовлечение",
  "Минимум интерактива",
  "Вообще без интерактивов",
];

type FormState = {
  eventType: string;
  clientName: string;
  secondName: string;
  phone: string;
  eventDate: string;
  city: string;
  venue: string;
  guestCount: string;
  guestAge: string;
  guestComposition: string;

  eventGoal: string;
  desiredAtmosphere: string;
  idealImpression: string;
  mustHaveMoments: string;
  forbiddenTopics: string;
  fears: string;

  mainHeroes: string;
  personalityTraits: string;
  values: string;
  importantStories: string;
  internalJokes: string;
  safeTopics: string;
  tabooTopics: string;

  hostStyle: string;
  humorPreference: string;
  tempoPreference: string;
  interactionPreference: string;
  touchingMoments: string;
  modernVsClassic: string;

  activeGuests: string;
  shyGuests: string;
  importantGuests: string;
  conflictRisks: string;
  childrenPresence: string;
  whoNotToInvolve: string;

  musicPreferences: string;
  favoriteArtists: string;
  bannedMusic: string;
  danceBlockNeed: string;
  ceremonyNeed: string;
  surpriseNeed: string;

  contestsNo: string;
  sensitiveTopics: string;
  culturalLimits: string;
  logisticsLimits: string;
  timingNotes: string;
  hardNo: string;

  finalWishes: string;
  additionalDetails: string;
  references: string;
};

type FormErrors = {
  clientName?: string;
  phone?: string;
  eventDate?: string;
  city?: string;
  desiredAtmosphere?: string;
  mainHeroes?: string;
};

const initialFormState: FormState = {
  eventType: "wedding",
  clientName: "",
  secondName: "",
  phone: "",
  eventDate: "",
  city: "",
  venue: "",
  guestCount: "",
  guestAge: "",
  guestComposition: "",

  eventGoal: "",
  desiredAtmosphere: "",
  idealImpression: "",
  mustHaveMoments: "",
  forbiddenTopics: "",
  fears: "",

  mainHeroes: "",
  personalityTraits: "",
  values: "",
  importantStories: "",
  internalJokes: "",
  safeTopics: "",
  tabooTopics: "",

  hostStyle: "",
  humorPreference: "",
  tempoPreference: "",
  interactionPreference: "",
  touchingMoments: "",
  modernVsClassic: "",

  activeGuests: "",
  shyGuests: "",
  importantGuests: "",
  conflictRisks: "",
  childrenPresence: "",
  whoNotToInvolve: "",

  musicPreferences: "",
  favoriteArtists: "",
  bannedMusic: "",
  danceBlockNeed: "",
  ceremonyNeed: "",
  surpriseNeed: "",

  contestsNo: "",
  sensitiveTopics: "",
  culturalLimits: "",
  logisticsLimits: "",
  timingNotes: "",
  hardNo: "",

  finalWishes: "",
  additionalDetails: "",
  references: "",
};

function InputField({
  label,
  name,
  value,
  onChange,
  placeholder,
  type = "text",
  error,
}: {
  label: string;
  name: keyof FormState;
  value: string;
  onChange: (event: ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
  type?: string;
  error?: string;
}) {
  return (
    <div>
      <label className="mb-2 block text-sm text-white/75">{label}</label>
      <input
        name={name}
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className={`w-full rounded-2xl border px-4 py-4 text-white placeholder:text-white/30 outline-none backdrop-blur-md transition ${
          error
            ? "border-red-400/60 bg-red-500/10"
            : "border-white/10 bg-white/5 focus:border-white/25 focus:bg-white/8"
        }`}
      />
      {error ? <p className="mt-2 text-sm text-red-300">{error}</p> : null}
    </div>
  );
}

function TextareaField({
  label,
  name,
  value,
  onChange,
  placeholder,
  rows = 4,
  error,
}: {
  label: string;
  name: keyof FormState;
  value: string;
  onChange: (event: ChangeEvent<HTMLTextAreaElement>) => void;
  placeholder?: string;
  rows?: number;
  error?: string;
}) {
  return (
    <div>
      <label className="mb-2 block text-sm text-white/75">{label}</label>
      <textarea
        name={name}
        value={value}
        onChange={onChange}
        rows={rows}
        placeholder={placeholder}
        className={`w-full rounded-2xl border px-4 py-4 text-white placeholder:text-white/30 outline-none backdrop-blur-md transition ${
          error
            ? "border-red-400/60 bg-red-500/10"
            : "border-white/10 bg-white/5 focus:border-white/25 focus:bg-white/8"
        }`}
      />
      {error ? <p className="mt-2 text-sm text-red-300">{error}</p> : null}
    </div>
  );
}

function ChoiceGrid({
  label,
  options,
  value,
  onSelect,
  columns = "sm:grid-cols-2",
}: {
  label: string;
  options: string[];
  value: string;
  onSelect: (value: string) => void;
  columns?: string;
}) {
  return (
    <div>
      <label className="mb-3 block text-sm text-white/75">{label}</label>
      <div className={`grid gap-3 ${columns}`}>
        {options.map((option) => {
          const isActive = value === option;
          return (
            <button
              key={option}
              type="button"
              onClick={() => onSelect(option)}
              className={`rounded-[22px] border px-4 py-4 text-left transition ${
                isActive
                  ? "border-white/30 bg-white/12"
                  : "border-white/10 bg-white/5 hover:border-white/20 hover:bg-white/10"
              }`}
            >
              {option}
            </button>
          );
        })}
      </div>
    </div>
  );
}

export default function QuestionnairePage() {
  const [step, setStep] = useState(1);
  const [isLoaded, setIsLoaded] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState<FormState>(initialFormState);
  const [errors, setErrors] = useState<FormErrors>({});

  useEffect(() => {
    const savedData = localStorage.getItem(STORAGE_KEY);

    if (savedData) {
      try {
        const parsed = JSON.parse(savedData) as {
          step?: number;
          formData?: FormState;
        };

        if (parsed.formData) setFormData(parsed.formData);
        if (parsed.step && parsed.step >= 1 && parsed.step <= TOTAL_STEPS) {
          setStep(parsed.step);
        }
      } catch (error) {
        console.error("Ошибка чтения сохраненной анкеты:", error);
      }
    }

    setIsLoaded(true);
  }, []);

  useEffect(() => {
    if (!isLoaded) return;

    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        step,
        formData,
      })
    );
  }, [formData, step, isLoaded]);

  const activeType = useMemo(
    () => eventTypes.find((item) => item.id === formData.eventType) ?? eventTypes[0],
    [formData.eventType]
  );

  const handleInputChange = (
    event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = event.target;

    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));

    setErrors((prev) => ({
      ...prev,
      [name]: undefined,
    }));
  };

  const handleTypeSelect = (eventType: string) => {
    setFormData((prev) => ({
      ...prev,
      eventType,
    }));
  };

  const selectSingleValue = (field: keyof FormState, value: string) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const validateCurrentStep = () => {
    const newErrors: FormErrors = {};

    if (step === 1) {
      if (!formData.clientName.trim()) newErrors.clientName = "Укажите имя";
      if (!formData.phone.trim()) newErrors.phone = "Укажите телефон";
      if (!formData.eventDate.trim()) newErrors.eventDate = "Укажите дату мероприятия";
      if (!formData.city.trim()) newErrors.city = "Укажите город";
    }

    if (step === 2 && !formData.desiredAtmosphere.trim()) {
      newErrors.desiredAtmosphere = "Опишите желаемую атмосферу";
    }

    if (step === 3 && !formData.mainHeroes.trim()) {
      newErrors.mainHeroes = "Опишите главных героев мероприятия";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNextStep = async () => {
    const isValid = validateCurrentStep();

    if (!isValid) {
      if (step === 1) {
        alert("Заполните имя, телефон, дату и город.");
      } else if (step === 2) {
        alert("Опишите желаемую атмосферу вечера.");
      } else if (step === 3) {
        alert("Опишите главных героев мероприятия.");
      }
      return;
    }

    if (step < TOTAL_STEPS) {
      setStep((prev) => prev + 1);
      window.scrollTo({ top: 0, behavior: "smooth" });
      return;
    }

    try {
      setIsSubmitting(true);

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/questionnaire`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(formData),
        }
      );

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || "Ошибка отправки анкеты");
      }

      alert("Анкета успешно отправлена");
      localStorage.removeItem(STORAGE_KEY);
      setFormData(initialFormState);
      setErrors({});
      setStep(1);
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (error) {
      console.error("Ошибка отправки анкеты:", error);
      alert("Не удалось отправить анкету");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handlePrevStep = () => {
    if (step > 1 && !isSubmitting) {
      setStep((prev) => prev - 1);
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  const handleResetDraft = () => {
    if (isSubmitting) return;
    localStorage.removeItem(STORAGE_KEY);
    setFormData(initialFormState);
    setErrors({});
    setStep(1);
  };

  const progressWidth = `${(step / TOTAL_STEPS) * 100}%`;

  if (!isLoaded) {
    return (
      <main className="min-h-screen bg-[#07070b] px-4 py-6 text-white sm:px-6 sm:py-10">
        <div className="mx-auto max-w-4xl">
          <div className="rounded-[36px] border border-white/10 bg-white/5 p-8 text-white/70 backdrop-blur-xl">
            Загрузка анкеты...
          </div>
        </div>
      </main>
    );
  }

  return (
    <main
      className={`min-h-screen overflow-hidden px-4 py-6 text-white sm:px-6 sm:py-10 ${activeType.background}`}
    >
      <div className="mx-auto max-w-5xl">
        <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
          <div className="inline-flex items-center rounded-full border border-white/15 bg-white/5 px-4 py-2 text-xs uppercase tracking-[0.24em] text-white/60 backdrop-blur-md">
            анкета мероприятия
          </div>

          <button
            type="button"
            onClick={handleResetDraft}
            className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs uppercase tracking-[0.18em] text-white/55 transition hover:bg-white/10 disabled:opacity-50"
            disabled={isSubmitting}
          >
            очистить черновик
          </button>
        </div>

        {step === 1 ? (
          <>
            <div className="grid gap-6 lg:grid-cols-[1.2fr_0.9fr]">
              <div className="relative overflow-hidden rounded-[36px] border border-white/10 bg-white/5 p-6 shadow-[0_20px_80px_rgba(0,0,0,0.45)] backdrop-blur-xl sm:p-8">
                <div className="absolute inset-0">
                  <div className="absolute left-1/2 top-0 h-56 w-56 -translate-x-1/2 rounded-full bg-white/10 blur-3xl" />
                  <div className="absolute right-0 top-1/4 h-40 w-40 rounded-full bg-white/10 blur-3xl" />
                  <div className="absolute bottom-0 left-0 h-40 w-40 rounded-full bg-white/10 blur-3xl" />
                </div>

                <div className="relative z-10">
                  <div className="mb-6">
                    <div className="mb-3 h-2 w-full overflow-hidden rounded-full bg-white/10">
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-white to-white/70 transition-all duration-300"
                        style={{ width: progressWidth }}
                      />
                    </div>
                    <p className="text-sm text-white/45">
                      Шаг {step} из {TOTAL_STEPS}
                    </p>
                  </div>

                  <div className="rounded-[30px] border border-white/10 bg-white/[0.04] p-5 backdrop-blur-md sm:p-6">
                    <p className="inline-flex rounded-full border border-white/10 bg-white/10 px-3 py-1 text-[11px] uppercase tracking-[0.22em] text-white/55">
                      {activeType.badge}
                    </p>

                    <h1 className="mt-4 max-w-3xl text-3xl font-semibold leading-tight sm:text-5xl">
                      {activeType.heroTitle}
                    </h1>

                    <p className="mt-5 max-w-2xl text-sm leading-7 text-white/68 sm:text-base">
                      {activeType.heroSubtitle}
                    </p>

                    <div className="mt-8 grid gap-3 sm:grid-cols-3">
                      {activeType.heroPoints.map((point) => (
                        <div
                          key={point}
                          className="rounded-2xl border border-white/10 bg-white/[0.05] p-4 text-sm leading-6 text-white/75"
                        >
                          {point}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              <div className="relative overflow-hidden rounded-[36px] border border-white/10 bg-white/5 p-6 shadow-[0_20px_80px_rgba(0,0,0,0.45)] backdrop-blur-xl sm:p-8">
                <div className="relative z-10 space-y-6">
                  <div>
                    <label className="mb-3 block text-sm text-white/75">
                      1. Какой формат мероприятия вы планируете?
                    </label>

                    <div className="grid gap-3">
                      {eventTypes.map((eventType) => {
                        const isActive = formData.eventType === eventType.id;

                        return (
                          <button
                            key={eventType.id}
                            type="button"
                            onClick={() => handleTypeSelect(eventType.id)}
                            className={`rounded-[24px] border p-4 text-left transition duration-200 ${
                              isActive
                                ? "border-white/30 bg-white/12 shadow-[0_0_0_1px_rgba(255,255,255,0.08)]"
                                : "border-white/10 bg-white/5 hover:border-white/20 hover:bg-white/10"
                            }`}
                          >
                            <div className="flex items-start justify-between gap-4">
                              <div>
                                <div className="text-base font-medium">{eventType.title}</div>
                                <div className="mt-2 text-sm leading-6 text-white/58">
                                  {eventType.description}
                                </div>
                              </div>

                              <div
                                className={`mt-1 h-5 w-5 rounded-full border ${
                                  isActive ? "border-white bg-white" : "border-white/25 bg-transparent"
                                }`}
                              />
                            </div>
                          </button>
                        );
                      })}
                    </div>
                  </div>

                  <InputField
                    label="2. Как вас зовут?"
                    name="clientName"
                    value={formData.clientName}
                    onChange={handleInputChange}
                    placeholder="Введите имя"
                    error={errors.clientName}
                  />

                  <InputField
                    label="3. Контактный телефон"
                    name="phone"
                    value={formData.phone}
                    onChange={handleInputChange}
                    placeholder="+7..."
                    error={errors.phone}
                  />

                  <div className="grid gap-4 sm:grid-cols-2">
                    <InputField
                      label="4. Дата"
                      name="eventDate"
                      type="date"
                      value={formData.eventDate}
                      onChange={handleInputChange}
                      error={errors.eventDate}
                    />
                    <InputField
                      label="5. Город"
                      name="city"
                      value={formData.city}
                      onChange={handleInputChange}
                      placeholder="Например, Москва"
                      error={errors.city}
                    />
                  </div>

                  <InputField
                    label="6. Площадка"
                    name="venue"
                    value={formData.venue}
                    onChange={handleInputChange}
                    placeholder="Название площадки"
                  />
                </div>
              </div>
            </div>

            <div className="mt-8 flex justify-end">
              <button
                type="button"
                onClick={handleNextStep}
                className="rounded-full bg-white px-7 py-3 text-sm font-medium text-neutral-950 transition duration-200 hover:scale-[1.02] disabled:opacity-50"
                disabled={isSubmitting}
              >
                Далее
              </button>
            </div>
          </>
        ) : (
          <div className="relative overflow-hidden rounded-[36px] border border-white/10 bg-white/5 p-6 shadow-[0_20px_80px_rgba(0,0,0,0.45)] backdrop-blur-xl sm:p-8">
            <div className="absolute inset-0">
              <div className="absolute left-1/2 top-0 h-56 w-56 -translate-x-1/2 rounded-full bg-white/10 blur-3xl" />
              <div className="absolute right-0 top-1/4 h-40 w-40 rounded-full bg-white/10 blur-3xl" />
              <div className="absolute bottom-0 left-0 h-40 w-40 rounded-full bg-white/10 blur-3xl" />
            </div>

            <div className="relative z-10">
              <div className="mb-6">
                <div className="mb-3 h-2 w-full overflow-hidden rounded-full bg-white/10">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-white to-white/70 transition-all duration-300"
                    style={{ width: progressWidth }}
                  />
                </div>
                <p className="text-sm text-white/45">
                  Шаг {step} из {TOTAL_STEPS}
                </p>
              </div>

              <div className="relative mb-8 overflow-hidden rounded-[30px] border border-white/10 bg-white/[0.04] p-5 backdrop-blur-md sm:p-6">
                <div className={`absolute inset-0 bg-gradient-to-br ${activeType.accent}`} />
                <div className="relative z-10">
                  <p className="inline-flex rounded-full border border-white/10 bg-white/10 px-3 py-1 text-[11px] uppercase tracking-[0.22em] text-white/55">
                    {activeType.badge}
                  </p>

                  <h1 className="mt-4 text-3xl font-semibold leading-tight sm:text-4xl">
                    {step === 2 && <>Атмосфера и ожидания от вечера</>}
                    {step === 3 && <>Главные герои и важные смыслы</>}
                    {step === 4 && <>Стиль ведения и подача вечера</>}
                    {step === 5 && <>Гости и особенности аудитории</>}
                    {step === 6 && <>Музыка и блоки программы</>}
                    {step === 7 && <>Ограничения и стоп-темы</>}
                    {step === 8 && <>Финальные детали и пожелания</>}
                  </h1>

                  <p className="mt-4 max-w-2xl text-sm leading-7 text-white/68 sm:text-base">
                    Заполните анкету максимально подробно. Чем глубже детали, тем точнее можно подготовить действительно сильный и запоминающийся праздник.
                  </p>
                </div>
              </div>

              {step === 2 && (
                <div className="space-y-6">
                  <TextareaField label="11. Какая главная цель этого мероприятия?" name="eventGoal" value={formData.eventGoal} onChange={handleInputChange} placeholder="Что для вас самое важное в этом вечере?" />
                  <TextareaField label="12. Какой атмосферы вы хотите от вечера?" name="desiredAtmosphere" value={formData.desiredAtmosphere} onChange={handleInputChange} placeholder="Например: тепло, красиво, современно, без перегруза" error={errors.desiredAtmosphere} />
                  <TextareaField label="13. Какое впечатление гости должны унести с собой?" name="idealImpression" value={formData.idealImpression} onChange={handleInputChange} placeholder="Что они должны почувствовать после мероприятия?" />
                  <TextareaField label="14. Какие моменты обязательно должны быть в программе?" name="mustHaveMoments" value={formData.mustHaveMoments} onChange={handleInputChange} placeholder="Например: первый танец, благодарность родителям, трогательный блок" />
                  <TextareaField label="15. Что точно не должно появиться в программе?" name="forbiddenTopics" value={formData.forbiddenTopics} onChange={handleInputChange} placeholder="Что вам категорически не близко?" />
                  <TextareaField label="16. Есть ли у вас страхи или переживания по поводу вечера?" name="fears" value={formData.fears} onChange={handleInputChange} placeholder="Что для вас может испортить праздник?" />
                </div>
              )}

              {step === 3 && (
                <div className="space-y-6">
                  <TextareaField label="17. Расскажите о главных героях мероприятия" name="mainHeroes" value={formData.mainHeroes} onChange={handleInputChange} placeholder="Кто вы, какие вы, что о вас важно знать?" error={errors.mainHeroes} />
                  <TextareaField label="18. Какие черты характера важно учесть?" name="personalityTraits" value={formData.personalityTraits} onChange={handleInputChange} placeholder="Например: легкие, интеллигентные, скромные, энергичные" />
                  <TextareaField label="19. Какие ценности и смыслы вам близки?" name="values" value={formData.values} onChange={handleInputChange} placeholder="Что для вас действительно важно в жизни и в этом событии?" />
                  <TextareaField label="20. Какие истории или факты обязательно нужно учесть?" name="importantStories" value={formData.importantStories} onChange={handleInputChange} placeholder="История знакомства, путь, достижения, семейные детали" />
                  <TextareaField label="21. Есть ли внутренние шутки, мемы, фирменные фразы?" name="internalJokes" value={formData.internalJokes} onChange={handleInputChange} placeholder="То, что поймут свои и что можно красиво использовать" />
                  <TextareaField label="22. О чем можно шутить или говорить легко?" name="safeTopics" value={formData.safeTopics} onChange={handleInputChange} placeholder="Безопасные темы для легких подводок и юмора" />
                  <TextareaField label="23. О чем шутить или говорить нельзя?" name="tabooTopics" value={formData.tabooTopics} onChange={handleInputChange} placeholder="Запретные темы" />
                </div>
              )}

              {step === 4 && (
                <div className="space-y-6">
                  <ChoiceGrid label="24. Какой стиль ведения вам ближе?" options={hostStyles} value={formData.hostStyle} onSelect={(value) => selectSingleValue("hostStyle", value)} columns="grid-cols-1" />
                  <ChoiceGrid label="25. Как вы относитесь к юмору в программе?" options={humorOptions} value={formData.humorPreference} onSelect={(value) => selectSingleValue("humorPreference", value)} />
                  <ChoiceGrid label="26. Какой темп вечера вам ближе?" options={tempoOptions} value={formData.tempoPreference} onSelect={(value) => selectSingleValue("tempoPreference", value)} columns="grid-cols-1" />
                  <ChoiceGrid label="27. Нужны ли интерактивы и вовлечение гостей?" options={interactionOptions} value={formData.interactionPreference} onSelect={(value) => selectSingleValue("interactionPreference", value)} columns="grid-cols-1" />
                  <TextareaField label="28. Нужны ли трогательные моменты?" name="touchingMoments" value={formData.touchingMoments} onChange={handleInputChange} placeholder="Какие именно эмоциональные моменты вы хотите?" />
                  <TextareaField label="29. Вам ближе современный формат или классика?" name="modernVsClassic" value={formData.modernVsClassic} onChange={handleInputChange} placeholder="Какой баланс нужен между классикой и современностью?" />
                </div>
              )}

              {step === 5 && (
                <div className="space-y-6">
                  <TextareaField label="30. Кто из гостей будет самым активным?" name="activeGuests" value={formData.activeGuests} onChange={handleInputChange} placeholder="Кого можно смело вовлекать?" />
                  <TextareaField label="31. Кто из гостей более скромный или закрытый?" name="shyGuests" value={formData.shyGuests} onChange={handleInputChange} placeholder="К кому нужен более деликатный подход?" />
                  <TextareaField label="32. Есть ли важные или статусные гости?" name="importantGuests" value={formData.importantGuests} onChange={handleInputChange} placeholder="Кого важно представить или учитывать отдельно?" />
                  <TextareaField label="33. Есть ли рискованные отношения или конфликтные темы между гостями?" name="conflictRisks" value={formData.conflictRisks} onChange={handleInputChange} placeholder="Например: бывшие, напряженные родственники, рабочие конфликты" />
                  <TextareaField label="34. Будут ли дети на мероприятии?" name="childrenPresence" value={formData.childrenPresence} onChange={handleInputChange} placeholder="Возраст детей, нужно ли их отдельно учитывать" />
                  <TextareaField label="35. Кого точно нельзя вовлекать в активные блоки?" name="whoNotToInvolve" value={formData.whoNotToInvolve} onChange={handleInputChange} placeholder="Кого лучше не вызывать, не шутить и не ставить в центр внимания" />
                </div>
              )}

              {step === 6 && (
                <div className="space-y-6">
                  <TextareaField label="36. Какие музыкальные стили вам нравятся?" name="musicPreferences" value={formData.musicPreferences} onChange={handleInputChange} placeholder="Какая музыка подходит настроению вечера?" />
                  <TextareaField label="37. Любимые артисты, треки или музыкальные ориентиры" name="favoriteArtists" value={formData.favoriteArtists} onChange={handleInputChange} placeholder="Что точно создает нужную атмосферу?" />
                  <TextareaField label="38. Что из музыки точно не включать?" name="bannedMusic" value={formData.bannedMusic} onChange={handleInputChange} placeholder="Жанры, треки, артисты под запретом" />
                  <TextareaField label="39. Нужен ли танцевальный блок?" name="danceBlockNeed" value={formData.danceBlockNeed} onChange={handleInputChange} placeholder="Насколько важна танцевальная часть?" />
                  <TextareaField label="40. Нужны ли церемонии, тосты, награждения, официальные блоки?" name="ceremonyNeed" value={formData.ceremonyNeed} onChange={handleInputChange} placeholder="Какие обязательные официальные или символические части нужны?" />
                  <TextareaField label="41. Планируются ли сюрпризы, подарки, неожиданные выступления?" name="surpriseNeed" value={formData.surpriseNeed} onChange={handleInputChange} placeholder="Что важно заранее предусмотреть?" />
                </div>
              )}

              {step === 7 && (
                <div className="space-y-6">
                  <TextareaField label="42. Какие конкурсы, форматы или приемы вам не нравятся?" name="contestsNo" value={formData.contestsNo} onChange={handleInputChange} placeholder="Что выглядит для вас неуместно или устаревше?" />
                  <TextareaField label="43. Какие темы особенно чувствительны?" name="sensitiveTopics" value={formData.sensitiveTopics} onChange={handleInputChange} placeholder="Темы, которые могут задеть вас или гостей" />
                  <TextareaField label="44. Есть ли культурные, семейные или личные ограничения?" name="culturalLimits" value={formData.culturalLimits} onChange={handleInputChange} placeholder="То, что обязательно нужно уважать и учитывать" />
                  <TextareaField label="45. Есть ли ограничения площадки или логистики?" name="logisticsLimits" value={formData.logisticsLimits} onChange={handleInputChange} placeholder="Шум, время, пространство, техника, запреты площадки" />
                  <TextareaField label="46. Есть ли важные замечания по таймингу?" name="timingNotes" value={formData.timingNotes} onChange={handleInputChange} placeholder="Например: до 21:00 нужен мягкий формат, потом динамика" />
                  <TextareaField label="47. Что категорически нельзя использовать ни при каких обстоятельствах?" name="hardNo" value={formData.hardNo} onChange={handleInputChange} placeholder="Ваше жесткое нет" />
                </div>
              )}

              {step === 8 && (
                <div className="space-y-6">
                  <TextareaField label="48. Какие у вас финальные пожелания к ведущему?" name="finalWishes" value={formData.finalWishes} onChange={handleInputChange} placeholder="Что особенно важно по вашему ощущению?" />
                  <TextareaField label="49. Какие детали мы еще не спросили, но их важно знать?" name="additionalDetails" value={formData.additionalDetails} onChange={handleInputChange} placeholder="Любые дополнительные смыслы, нюансы, контекст" />
                  <TextareaField label="50. Есть ли референсы, примеры, ссылки, идеи, на которые можно ориентироваться?" name="references" value={formData.references} onChange={handleInputChange} placeholder="Можно перечислить ссылки, примеры формата, образы, настроение" />
                </div>
              )}

              <div className="mt-8 flex items-center justify-between gap-4">
                <button
                  type="button"
                  onClick={handlePrevStep}
                  className="rounded-full border border-white/10 bg-white/5 px-6 py-3 text-sm text-white/70 backdrop-blur-md disabled:opacity-50"
                  disabled={step === 1 || isSubmitting}
                >
                  Назад
                </button>

                <button
                  type="button"
                  onClick={handleNextStep}
                  className="rounded-full bg-white px-7 py-3 text-sm font-medium text-neutral-950 transition duration-200 hover:scale-[1.02] disabled:opacity-50"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? "Отправка..." : step < TOTAL_STEPS ? "Далее" : "Завершить анкету"}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}