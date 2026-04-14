"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

type Questionnaire = Record<string, string>;

type SubmissionRecord = {
  id: string;
  created_at: string;
  questionnaire: Questionnaire;
  program?: ProgramData;
};

type SubmissionResponse = {
  status: string;
  item: SubmissionRecord;
};

type ScenarioTimelineBlock = {
  time_from: string;
  time_to: string;
  block_title: string;
  block_purpose: string;
  what_happens: string;
  host_action: string;
  host_text: string;
  dj_task: string;
  director_move: string;
  risk_control: string;
  transition: string;
};

type RiskItem = {
  risk: string;
  why_it_matters: string;
  how_to_prevent: string;
  what_to_do_if_triggered: string;
};

type PlanBItem = {
  situation: string;
  solution: string;
};

type ProgramData = {
  event_passport?: {
    event_type?: string;
    format_name?: string;
    city?: string;
    venue?: string;
    event_date?: string;
    working_timeline_note?: string;
    main_goal?: string;
    atmosphere?: string;
    style?: string;
    mandatory_points?: string[];
    hard_bans?: string[];
    timing_anchor?: string;
  };
  quality_panel?: {
    scenario_verdict?: string;
    director_verdict?: string;
    critic_verdict?: string;
    final_ready?: boolean;
    fixed_issues?: string[];
  };
  concept?: {
    big_idea?: string;
    main_director_thesis?: string;
    main_emotional_result?: string;
    why_this_event_will_be_remembered?: string;
  };
  trend_layer?: {
    trend_summary?: string;
    applied_trends?: string[];
    rejected_outdated_patterns?: string[];
  };
  key_host_commands?: string[];
  questions_to_clarify_before_event?: string[];
  director_logic?: {
    opening_logic?: string;
    development_logic?: string;
    family_or_core_emotional_logic?: string;
    final_logic?: string;
  };
  scenario_timeline?: ScenarioTimelineBlock[];
  host_script?: {
    opening_main?: string;
    opening_short?: string;
    welcome_line?: string;
    first_core_intro?: string;
    family_block_intro?: string;
    surprise_intro?: string;
    dance_block_intro?: string;
    final_block_intro?: string;
    closing_words?: string;
  };
  dj_guidance?: {
    overall_music_policy?: string;
    welcome_music?: string;
    opening_music?: string;
    table_background?: string;
    emotional_blocks_music?: string;
    dance_block_1?: string;
    dance_block_2?: string;
    dance_block_3?: string;
    final_block_music?: string;
    final_music?: string;
    stop_list?: string[];
    technical_notes?: string[];
  };
  guest_management?: {
    active_people?: string[];
    shy_people?: string[];
    important_people?: string[];
    do_not_involve?: string[];
    sensitive_people_or_topics?: string[];
    management_notes?: string[];
  };
  risk_map?: RiskItem[];
  plan_b?: PlanBItem[];
  final_print_version?: {
    title?: string;
    summary?: string;
    timeline_short?: string[];
    must_do?: string[];
    must_not_do?: string[];
    host_focus?: string[];
    dj_focus?: string[];
  };
};

type ProgramResponse = {
  status: string;
  submissionId: string;
  program: ProgramData;
  cached?: boolean;
};

const QUESTIONNAIRE_LABELS: Record<string, string> = {
  eventType: "Тип мероприятия",
  clientName: "Название заявки",
  phone: "Телефон",
  eventDate: "Дата события",
  city: "Город",
  venue: "Площадка",
  startTime: "Время начала",
  guestCount: "Количество гостей",
  childrenInfo: "Дети",
  atmosphere: "Атмосфера",
  fears: "Страхи и переживания",
  hostWishes: "Пожелания к ведущему",
  references: "Референсы",
  musicLikes: "Любимая музыка",
  musicBans: "Стоп-лист музыки",
  groomName: "Имя жениха",
  brideName: "Имя невесты",
  weddingTraditions: "Свадебные традиции",
  groomParents: "Родители жениха",
  brideParents: "Родители невесты",
  grandparents: "Бабушки и дедушки",
  loveStory: "История знакомства",
  coupleValues: "Ценности пары",
  importantDates: "Важные даты",
  proposalStory: "История предложения",
  nicknames: "Ласковые имена",
  insideJokes: "Внутренние шутки",
  guestsList: "Ключевые гости",
  conflictTopics: "Чувствительные темы",
  likedFormats: "Нравящиеся форматы",
  celebrantName: "Имя юбиляра",
  celebrantAge: "Возраст юбиляра",
  familyMembers: "Семья юбиляра",
  anniversaryAtmosphere: "Атмосфера юбилея",
  keyMoments: "Ключевые моменты",
  biographyStory: "Биография",
  achievements: "Достижения",
  lifeStages: "Этапы жизни",
  characterTraits: "Черты характера",
  funnyFacts: "Факты и фразы",
  importantGuests: "Важные гости",
  jubileeConflictTopics: "Чувствительные темы",
  jubileeLikedFormats: "Нравящиеся форматы",
  whatCannotBeDone: "Что нельзя делать",
};

function InfoCard({
  title,
  value,
}: {
  title: string;
  value?: string | boolean;
}) {
  let displayValue = "Не указано";

  if (typeof value === "boolean") {
    displayValue = value ? "Да" : "Нет";
  } else if (typeof value === "string" && value.trim()) {
    displayValue = value;
  }

  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
      <div className="text-xs uppercase tracking-[0.18em] text-white/40">
        {title}
      </div>
      <div className="mt-2 text-sm leading-7 text-white/80">{displayValue}</div>
    </div>
  );
}

function ListBlock({
  title,
  items,
}: {
  title: string;
  items?: string[];
}) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
      <div className="text-xs uppercase tracking-[0.18em] text-white/40">
        {title}
      </div>
      <div className="mt-3 space-y-2">
        {items && items.length > 0 ? (
          items.map((item, index) => (
            <div
              key={`${item}-${index}`}
              className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white/80"
            >
              {index + 1}. {item}
            </div>
          ))
        ) : (
          <div className="text-sm text-white/60">Не сформировано</div>
        )}
      </div>
    </div>
  );
}

export default function HostSubmissionPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const [item, setItem] = useState<SubmissionRecord | null>(null);
  const [submissionId, setSubmissionId] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [programLoading, setProgramLoading] = useState(false);
  const [programError, setProgramError] = useState("");
  const [program, setProgram] = useState<ProgramData | null>(null);

  useEffect(() => {
    const loadSubmission = async () => {
      try {
        const resolvedParams = await params;
        setSubmissionId(resolvedParams.id);

        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/submissions/${resolvedParams.id}`
        );
        const data: SubmissionResponse = await response.json();

        if (!response.ok) {
          throw new Error("Не удалось загрузить анкету");
        }

        setItem(data.item);
        if (data.item.program) {
          setProgram(data.item.program);
        }
      } catch (err) {
        console.error(err);
        setError("Не удалось загрузить анкету");
      } finally {
        setLoading(false);
      }
    };

    loadSubmission();
  }, [params]);

  const handleGenerateProgram = async () => {
    if (!submissionId) return;

    try {
      setProgramLoading(true);
      setProgramError("");

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/submissions/${submissionId}/generate-program`,
        {
          method: "POST",
        }
      );

      const data: ProgramResponse | { detail?: string } = await response.json();

      if (!response.ok || !("program" in data)) {
        throw new Error(
          "detail" in data && data.detail
            ? data.detail
            : "Не удалось сформировать программу"
        );
      }

      setProgram(data.program);
    } catch (err) {
      console.error(err);
      setProgramError("Не удалось сформировать программу");
    } finally {
      setProgramLoading(false);
    }
  };

  const handleDownloadDocx = () => {
    if (!submissionId) return;

    window.open(
      `${process.env.NEXT_PUBLIC_API_URL}/api/submissions/${submissionId}/export-docx`,
      "_blank"
    );
  };

  const handleLogout = async () => {
    await fetch("/api/host-logout", { method: "POST" });
    window.location.href = "/login";
  };

  return (
    <main className="min-h-screen bg-[#07070b] px-4 py-6 text-white sm:px-6 sm:py-10">
      <div className="mx-auto max-w-7xl">
        <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="inline-flex rounded-full border border-white/15 bg-white/5 px-4 py-2 text-xs uppercase tracking-[0.24em] text-white/60 backdrop-blur-md">
              карточка анкеты
            </div>

            <h1 className="mt-4 text-4xl font-semibold tracking-tight">
              Просмотр заявки
            </h1>

            <p className="mt-3 max-w-3xl text-sm leading-7 text-white/65 sm:text-base">
              Здесь отображается анкета клиента и финальный сценарный документ,
              который агент собирает как аналитик, тренд-аналитик, сценарист,
              режиссер и критик.
            </p>
          </div>

          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              onClick={handleGenerateProgram}
              disabled={programLoading || loading || !!error}
              className="rounded-full bg-white px-5 py-3 text-sm font-medium text-neutral-950 transition hover:scale-[1.02] disabled:opacity-50"
            >
              {programLoading ? "Формирование..." : "Сформировать программу"}
            </button>

            <button
              type="button"
              onClick={handleDownloadDocx}
              disabled={loading || !!error}
              className="rounded-full border border-white/10 bg-white/5 px-5 py-3 text-sm text-white/75 transition hover:bg-white/10 disabled:opacity-50"
            >
              Скачать Word
            </button>

            <button
              type="button"
              onClick={handleLogout}
              className="rounded-full border border-white/10 bg-white/5 px-5 py-3 text-sm text-white/75 transition hover:bg-white/10"
            >
              Выйти
            </button>

            <Link
              href="/host"
              className="rounded-full border border-white/10 bg-white/5 px-5 py-3 text-sm text-white/75 transition hover:bg-white/10"
            >
              Назад к списку
            </Link>
          </div>
        </div>

        {loading ? (
          <div className="rounded-[28px] border border-white/10 bg-white/5 p-6 text-white/70 backdrop-blur-xl">
            Загрузка анкеты...
          </div>
        ) : error ? (
          <div className="rounded-[28px] border border-red-400/30 bg-red-500/10 p-6 text-red-200 backdrop-blur-xl">
            {error}
          </div>
        ) : item ? (
          <div className="space-y-6">
            <section className="rounded-[28px] border border-white/10 bg-white/5 p-6 shadow-[0_20px_60px_rgba(0,0,0,0.25)] backdrop-blur-xl">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                <div>
                  <div className="inline-flex rounded-full border border-white/10 bg-white/10 px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-white/55">
                    {item.questionnaire.eventType}
                  </div>

                  <h2 className="mt-4 text-3xl font-semibold">
                    {item.questionnaire.clientName}
                  </h2>

                  <p className="mt-2 text-sm text-white/55">
                    Создано: {new Date(item.created_at).toLocaleString("ru-RU")}
                  </p>
                </div>

                <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white/65">
                  ID: {submissionId}
                </div>
              </div>
            </section>

            <section className="rounded-[28px] border border-white/10 bg-white/5 p-6 shadow-[0_20px_60px_rgba(0,0,0,0.25)] backdrop-blur-xl">
              <div className="mb-4 inline-flex rounded-full border border-white/10 bg-white/10 px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-white/55">
                анкета клиента
              </div>
              <div className="grid gap-3 md:grid-cols-2">
                {Object.entries(item.questionnaire).map(([key, value]) => (
                  <InfoCard
                    key={key}
                    title={QUESTIONNAIRE_LABELS[key] ?? key}
                    value={typeof value === "string" ? value : String(value)}
                  />
                ))}
              </div>
            </section>

            {programError ? (
              <div className="rounded-[28px] border border-red-400/30 bg-red-500/10 p-6 text-red-200 backdrop-blur-xl">
                {programError}
              </div>
            ) : null}

            {program ? (
              <section className="space-y-6 rounded-[28px] border border-white/10 bg-white/5 p-6 shadow-[0_20px_60px_rgba(0,0,0,0.25)] backdrop-blur-xl">
                <div className="inline-flex rounded-full border border-white/10 bg-white/10 px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-white/55">
                  готовая программа ведущего
                </div>

                <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                  <InfoCard title="Тип события" value={program.event_passport?.event_type} />
                  <InfoCard title="Формат" value={program.event_passport?.format_name} />
                  <InfoCard title="Город" value={program.event_passport?.city} />
                  <InfoCard title="Площадка" value={program.event_passport?.venue} />
                  <InfoCard title="Дата" value={program.event_passport?.event_date} />
                  <InfoCard title="Главная цель" value={program.event_passport?.main_goal} />
                  <InfoCard title="Атмосфера" value={program.event_passport?.atmosphere} />
                  <InfoCard title="Тайминговый якорь" value={program.event_passport?.timing_anchor} />
                </div>

                <InfoCard
                  title="Рабочая пометка по таймингу"
                  value={program.event_passport?.working_timeline_note}
                />

                <ListBlock title="Обязательные точки" items={program.event_passport?.mandatory_points} />
                <ListBlock title="Жесткие запреты" items={program.event_passport?.hard_bans} />

                <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                  <InfoCard title="Вердикт сценариста" value={program.quality_panel?.scenario_verdict} />
                  <InfoCard title="Вердикт режиссера" value={program.quality_panel?.director_verdict} />
                  <InfoCard title="Вердикт критика" value={program.quality_panel?.critic_verdict} />
                  <InfoCard title="Готово к работе" value={program.quality_panel?.final_ready} />
                </div>

                <ListBlock
                  title="Что было исправлено перед финальной сборкой"
                  items={program.quality_panel?.fixed_issues}
                />

                <div className="grid gap-4 md:grid-cols-2">
                  <InfoCard title="Большая идея вечера" value={program.concept?.big_idea} />
                  <InfoCard title="Главный режиссерский тезис" value={program.concept?.main_director_thesis} />
                  <InfoCard title="Главный эмоциональный результат" value={program.concept?.main_emotional_result} />
                  <InfoCard title="Почему вечер запомнится" value={program.concept?.why_this_event_will_be_remembered} />
                </div>

                <InfoCard title="Краткое резюме трендов" value={program.trend_layer?.trend_summary} />
                <div className="grid gap-4 lg:grid-cols-2">
                  <ListBlock title="Какие тренды применены" items={program.trend_layer?.applied_trends} />
                  <ListBlock title="Что отброшено как устаревшее" items={program.trend_layer?.rejected_outdated_patterns} />
                </div>

                <ListBlock title="Ключевые команды ведущему" items={program.key_host_commands} />
                <ListBlock title="Что уточнить до мероприятия" items={program.questions_to_clarify_before_event} />

                <div className="grid gap-4 md:grid-cols-2">
                  <InfoCard title="Логика открытия" value={program.director_logic?.opening_logic} />
                  <InfoCard title="Логика развития" value={program.director_logic?.development_logic} />
                  <InfoCard
                    title="Логика эмоционального ядра"
                    value={program.director_logic?.family_or_core_emotional_logic}
                  />
                  <InfoCard title="Логика финала" value={program.director_logic?.final_logic} />
                </div>

                <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                  <div className="text-xs uppercase tracking-[0.18em] text-white/40">
                    Пошаговый тайминг и действия ведущего
                  </div>

                  <div className="mt-4 space-y-4">
                    {program.scenario_timeline && program.scenario_timeline.length > 0 ? (
                      program.scenario_timeline.map((block, index) => (
                        <div
                          key={`${block.time_from}-${block.block_title}-${index}`}
                          className="rounded-2xl border border-white/10 bg-white/5 p-5"
                        >
                          <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
                            <div className="text-lg font-semibold text-white">
                              {index + 1}. {block.block_title || "Блок"}
                            </div>
                            <div className="rounded-full border border-white/10 bg-white/10 px-4 py-2 text-sm text-white/75">
                              {block.time_from || "--:--"} — {block.time_to || "--:--"}
                            </div>
                          </div>

                          <div className="mt-4 grid gap-4 md:grid-cols-2">
                            <InfoCard title="Цель блока" value={block.block_purpose} />
                            <InfoCard title="Что происходит" value={block.what_happens} />
                            <InfoCard title="Действие ведущего" value={block.host_action} />
                            <InfoCard title="Задача диджея" value={block.dj_task} />
                            <InfoCard title="Режиссерский ход" value={block.director_move} />
                            <InfoCard title="Контроль риска" value={block.risk_control} />
                          </div>

                          <div className="mt-4 rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                            <div className="text-xs uppercase tracking-[0.18em] text-white/40">
                              Текст ведущего
                            </div>
                            <div className="mt-2 whitespace-pre-wrap text-sm leading-7 text-white/80">
                              {block.host_text?.trim() ? block.host_text : "Не сформировано"}
                            </div>
                          </div>

                          <div className="mt-4 rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                            <div className="text-xs uppercase tracking-[0.18em] text-white/40">
                              Переход к следующему блоку
                            </div>
                            <div className="mt-2 text-sm leading-7 text-white/80">
                              {block.transition?.trim() ? block.transition : "Не сформировано"}
                            </div>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-sm text-white/60">Не сформировано</div>
                    )}
                  </div>
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <InfoCard title="Основное открытие" value={program.host_script?.opening_main} />
                  <InfoCard title="Короткое открытие" value={program.host_script?.opening_short} />
                  <InfoCard title="Welcome-фраза" value={program.host_script?.welcome_line} />
                  <InfoCard title="Подводка к первому ключевому блоку" value={program.host_script?.first_core_intro} />
                  <InfoCard title="Подводка к семейному блоку" value={program.host_script?.family_block_intro} />
                  <InfoCard title="Подводка к сюрпризу" value={program.host_script?.surprise_intro} />
                  <InfoCard title="Подводка к танцевальному блоку" value={program.host_script?.dance_block_intro} />
                  <InfoCard title="Подводка к финальному блоку" value={program.host_script?.final_block_intro} />
                  <InfoCard title="Финальные слова" value={program.host_script?.closing_words} />
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <InfoCard title="Музыкальная политика" value={program.dj_guidance?.overall_music_policy} />
                  <InfoCard title="Музыка на welcome" value={program.dj_guidance?.welcome_music} />
                  <InfoCard title="Музыка на открытие" value={program.dj_guidance?.opening_music} />
                  <InfoCard title="Фон под застолье" value={program.dj_guidance?.table_background} />
                  <InfoCard title="Музыка на эмоциональные блоки" value={program.dj_guidance?.emotional_blocks_music} />
                  <InfoCard title="Танцпол 1" value={program.dj_guidance?.dance_block_1} />
                  <InfoCard title="Танцпол 2" value={program.dj_guidance?.dance_block_2} />
                  <InfoCard title="Танцпол 3" value={program.dj_guidance?.dance_block_3} />
                  <InfoCard title="Музыка на финальный блок" value={program.dj_guidance?.final_block_music} />
                  <InfoCard title="Финальная музыка" value={program.dj_guidance?.final_music} />
                </div>

                <ListBlock title="Стоп-лист для диджея" items={program.dj_guidance?.stop_list} />
                <ListBlock title="Технические заметки для диджея" items={program.dj_guidance?.technical_notes} />

                <div className="grid gap-4 lg:grid-cols-2">
                  <ListBlock title="Активные люди" items={program.guest_management?.active_people} />
                  <ListBlock title="Скромные люди" items={program.guest_management?.shy_people} />
                  <ListBlock title="Важные люди" items={program.guest_management?.important_people} />
                  <ListBlock title="Кого не вовлекать" items={program.guest_management?.do_not_involve} />
                  <ListBlock title="Чувствительные люди и темы" items={program.guest_management?.sensitive_people_or_topics} />
                  <ListBlock title="Управленческие заметки" items={program.guest_management?.management_notes} />
                </div>

                <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                  <div className="text-xs uppercase tracking-[0.18em] text-white/40">
                    Риски и способы отработки
                  </div>
                  <div className="mt-4 space-y-4">
                    {program.risk_map && program.risk_map.length > 0 ? (
                      program.risk_map.map((risk, index) => (
                        <div
                          key={`${risk.risk}-${index}`}
                          className="rounded-2xl border border-white/10 bg-white/5 p-4"
                        >
                          <div className="text-sm font-semibold text-white">
                            {index + 1}. {risk.risk || "Риск"}
                          </div>
                          <div className="mt-2 text-sm text-white/75">
                            <span className="text-white/45">Почему важно:</span>{" "}
                            {risk.why_it_matters || "Не указано"}
                          </div>
                          <div className="mt-2 text-sm text-white/75">
                            <span className="text-white/45">Как предотвратить:</span>{" "}
                            {risk.how_to_prevent || "Не указано"}
                          </div>
                          <div className="mt-2 text-sm leading-7 text-white/75">
                            <span className="text-white/45">Что делать, если случилось:</span>{" "}
                            {risk.what_to_do_if_triggered || "Не указано"}
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-sm text-white/60">Не сформировано</div>
                    )}
                  </div>
                </div>

                <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                  <div className="text-xs uppercase tracking-[0.18em] text-white/40">
                    План Б
                  </div>
                  <div className="mt-4 space-y-4">
                    {program.plan_b && program.plan_b.length > 0 ? (
                      program.plan_b.map((item, index) => (
                        <div
                          key={`${item.situation}-${index}`}
                          className="rounded-2xl border border-white/10 bg-white/5 p-4"
                        >
                          <div className="text-sm font-semibold text-white">
                            {index + 1}. {item.situation || "Ситуация"}
                          </div>
                          <div className="mt-2 text-sm leading-7 text-white/80">
                            {item.solution || "Не указано"}
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-sm text-white/60">Не сформировано</div>
                    )}
                  </div>
                </div>

                <div className="space-y-4 rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                  <div className="text-xs uppercase tracking-[0.18em] text-white/40">
                    Краткая версия для печати
                  </div>

                  <InfoCard title="Название" value={program.final_print_version?.title} />
                  <InfoCard title="Краткое резюме" value={program.final_print_version?.summary} />

                  <div className="grid gap-4 lg:grid-cols-2">
                    <ListBlock title="Короткий таймлайн" items={program.final_print_version?.timeline_short} />
                    <ListBlock title="Обязательно сделать" items={program.final_print_version?.must_do} />
                    <ListBlock title="Нельзя делать" items={program.final_print_version?.must_not_do} />
                    <ListBlock title="Фокус ведущего" items={program.final_print_version?.host_focus} />
                  </div>

                  <ListBlock title="Фокус диджея" items={program.final_print_version?.dj_focus} />
                </div>
              </section>
            ) : null}
          </div>
        ) : null}
      </div>
    </main>
  );
}
