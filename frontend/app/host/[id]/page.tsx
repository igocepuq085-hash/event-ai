"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

type Questionnaire = {
  eventType: string;
  clientName: string;
  secondName?: string;
  phone: string;
  eventDate: string;
  city: string;
  venue?: string;
  guestCount?: string;
  guestAge?: string;
  guestComposition?: string;
  eventGoal?: string;
  desiredAtmosphere?: string;
  idealImpression?: string;
  mustHaveMoments?: string;
  forbiddenTopics?: string;
  fears?: string;
  mainHeroes?: string;
  personalityTraits?: string;
  values?: string;
  importantStories?: string;
  internalJokes?: string;
  safeTopics?: string;
  tabooTopics?: string;
  hostStyle?: string;
  humorPreference?: string;
  tempoPreference?: string;
  interactionPreference?: string;
  touchingMoments?: string;
  modernVsClassic?: string;
  activeGuests?: string;
  shyGuests?: string;
  importantGuests?: string;
  conflictRisks?: string;
  childrenPresence?: string;
  whoNotToInvolve?: string;
  musicPreferences?: string;
  favoriteArtists?: string;
  bannedMusic?: string;
  danceBlockNeed?: string;
  ceremonyNeed?: string;
  surpriseNeed?: string;
  contestsNo?: string;
  sensitiveTopics?: string;
  culturalLimits?: string;
  logisticsLimits?: string;
  timingNotes?: string;
  hardNo?: string;
  finalWishes?: string;
  additionalDetails?: string;
  references?: string;
};

type SubmissionRecord = {
  id: string;
  created_at: string;
  questionnaire: Questionnaire;
};

type ApiResponse = {
  status: string;
  count: number;
  items: SubmissionRecord[];
};

type RedFlag = {
  risk: string;
  why_it_matters: string;
  how_to_handle: string;
};

type TimelineBlock = {
  block_title: string;
  block_goal: string;
  approx_duration: string;
  what_happens: string;
  host_task: string;
  transition_to_next: string;
};

type InteractiveBlock = {
  title: string;
  goal: string;
  best_moment: string;
  how_to_run: string;
  why_it_is_safe: string;
};

type HumorItem = {
  line: string;
  tone: string;
  where_to_use: string;
  safety_note: string;
};

type PlanBItem = {
  situation: string;
  response: string;
};

type ProgramData = {
  event_brief?: {
    format?: string;
    city?: string;
    venue?: string;
    date?: string;
    atmosphere?: string;
    main_goal?: string;
    key_moments?: string[];
    hard_limits?: string[];
    timing_anchor?: string;
  };
  director_concept?: {
    idea?: string;
    emotional_arc?: string;
    host_role?: string;
    main_impression_for_guests?: string;
  };
  red_flags?: RedFlag[];
  audience_map?: {
    core_audience?: string;
    active_guests?: string[];
    shy_guests?: string[];
    important_guests?: string[];
    guests_not_to_involve?: string[];
    children_notes?: string;
  };
  timeline_plan?: TimelineBlock[];
  host_lines?: {
    opening_main?: string;
    opening_short?: string;
    intro_first_dance?: string;
    intro_family_block?: string;
    intro_surprise_block?: string;
    intro_cake?: string;
    closing_lines?: string;
  };
  interactive_blocks?: InteractiveBlock[];
  humor_bank?: HumorItem[];
  plan_b?: PlanBItem[];
  final_strategy?: {
    how_to_lead_this_event?: string;
    what_to_avoid?: string;
    what_will_make_this_event_strong?: string;
  };
  print_version?: {
    title?: string;
    event_summary?: string;
    key_people?: string[];
    must_do_blocks?: string[];
    do_not_do?: string[];
    short_timeline?: string[];
    host_focus_points?: string[];
  };
};

type ProgramResponse = {
  status: string;
  submissionId: string;
  program: ProgramData;
};

function InfoCard({
  title,
  value,
}: {
  title: string;
  value?: string;
}) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
      <div className="text-xs uppercase tracking-[0.18em] text-white/40">
        {title}
      </div>
      <div className="mt-2 text-sm leading-7 text-white/80">
        {value && value.trim() ? value : "Не указано"}
      </div>
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
          `${process.env.NEXT_PUBLIC_API_URL}/api/submissions`
        );
        const data: ApiResponse = await response.json();

        if (!response.ok) {
          throw new Error("Не удалось загрузить анкету");
        }

        const foundItem = data.items.find((entry) => entry.id === resolvedParams.id);

        if (!foundItem) {
          setError("Анкета не найдена");
          return;
        }

        setItem(foundItem);
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

  return (
    <main className="min-h-screen bg-[#07070b] px-4 py-6 text-white sm:px-6 sm:py-10">
      <div className="mx-auto max-w-6xl">
        <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="inline-flex rounded-full border border-white/15 bg-white/5 px-4 py-2 text-xs uppercase tracking-[0.24em] text-white/60 backdrop-blur-md">
              карточка анкеты
            </div>

            <h1 className="mt-4 text-4xl font-semibold tracking-tight">
              Просмотр заявки
            </h1>

            <p className="mt-3 max-w-2xl text-sm leading-7 text-white/65 sm:text-base">
              Здесь отображается полная анкета клиента и рабочая программа для ведущего.
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

            {programError ? (
              <div className="rounded-[28px] border border-red-400/30 bg-red-500/10 p-6 text-red-200 backdrop-blur-xl">
                {programError}
              </div>
            ) : null}

            {program ? (
              <section className="space-y-6 rounded-[28px] border border-white/10 bg-white/5 p-6 shadow-[0_20px_60px_rgba(0,0,0,0.25)] backdrop-blur-xl">
                <div className="inline-flex rounded-full border border-white/10 bg-white/10 px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-white/55">
                  рабочая программа ведущего
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <InfoCard title="Формат" value={program.event_brief?.format} />
                  <InfoCard title="Город" value={program.event_brief?.city} />
                  <InfoCard title="Площадка" value={program.event_brief?.venue} />
                  <InfoCard title="Дата" value={program.event_brief?.date} />
                  <InfoCard title="Атмосфера" value={program.event_brief?.atmosphere} />
                  <InfoCard title="Главная цель" value={program.event_brief?.main_goal} />
                  <InfoCard title="Тайминговый якорь" value={program.event_brief?.timing_anchor} />
                </div>

                <ListBlock title="Ключевые моменты" items={program.event_brief?.key_moments} />
                <ListBlock title="Жесткие ограничения" items={program.event_brief?.hard_limits} />

                <div className="grid gap-4 md:grid-cols-2">
                  <InfoCard title="Режиссерская идея" value={program.director_concept?.idea} />
                  <InfoCard title="Эмоциональная дуга" value={program.director_concept?.emotional_arc} />
                  <InfoCard title="Роль ведущего" value={program.director_concept?.host_role} />
                  <InfoCard
                    title="Что должны унести гости"
                    value={program.director_concept?.main_impression_for_guests}
                  />
                </div>

                <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                  <div className="text-xs uppercase tracking-[0.18em] text-white/40">
                    красные флаги
                  </div>
                  <div className="mt-3 space-y-3">
                    {program.red_flags && program.red_flags.length > 0 ? (
                      program.red_flags.map((flag, index) => (
                        <div
                          key={`${flag.risk}-${index}`}
                          className="rounded-xl border border-white/10 bg-white/5 p-4"
                        >
                          <div className="text-sm font-semibold text-white">
                            {index + 1}. {flag.risk || "Риск"}
                          </div>
                          <div className="mt-2 text-sm text-white/75">
                            <span className="text-white/45">Почему важно:</span>{" "}
                            {flag.why_it_matters || "Не указано"}
                          </div>
                          <div className="mt-2 text-sm leading-7 text-white/75">
                            <span className="text-white/45">Как отработать:</span>{" "}
                            {flag.how_to_handle || "Не указано"}
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-sm text-white/60">Не сформировано</div>
                    )}
                  </div>
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <InfoCard title="Ядро аудитории" value={program.audience_map?.core_audience} />
                  <InfoCard title="Дети" value={program.audience_map?.children_notes} />
                </div>

                <div className="grid gap-4 lg:grid-cols-2">
                  <ListBlock title="Активные гости" items={program.audience_map?.active_guests} />
                  <ListBlock title="Скромные гости" items={program.audience_map?.shy_guests} />
                  <ListBlock title="Важные гости" items={program.audience_map?.important_guests} />
                  <ListBlock
                    title="Кого не вовлекать"
                    items={program.audience_map?.guests_not_to_involve}
                  />
                </div>

                <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                  <div className="text-xs uppercase tracking-[0.18em] text-white/40">
                    план вечера по блокам
                  </div>
                  <div className="mt-3 space-y-3">
                    {program.timeline_plan && program.timeline_plan.length > 0 ? (
                      program.timeline_plan.map((block, index) => (
                        <div
                          key={`${block.block_title}-${index}`}
                          className="rounded-xl border border-white/10 bg-white/5 p-4"
                        >
                          <div className="text-sm font-semibold text-white">
                            {index + 1}. {block.block_title || "Блок"}
                          </div>
                          <div className="mt-2 text-sm text-white/75">
                            <span className="text-white/45">Цель:</span>{" "}
                            {block.block_goal || "Не указана"}
                          </div>
                          <div className="mt-2 text-sm text-white/75">
                            <span className="text-white/45">Примерная длительность:</span>{" "}
                            {block.approx_duration || "Не указана"}
                          </div>
                          <div className="mt-2 text-sm text-white/75">
                            <span className="text-white/45">Что происходит:</span>{" "}
                            {block.what_happens || "Не указано"}
                          </div>
                          <div className="mt-2 text-sm text-white/75">
                            <span className="text-white/45">Задача ведущего:</span>{" "}
                            {block.host_task || "Не указано"}
                          </div>
                          <div className="mt-2 text-sm leading-7 text-white/75">
                            <span className="text-white/45">Переход дальше:</span>{" "}
                            {block.transition_to_next || "Не указан"}
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-sm text-white/60">Не сформировано</div>
                    )}
                  </div>
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <InfoCard title="Основное открытие" value={program.host_lines?.opening_main} />
                  <InfoCard title="Короткое открытие" value={program.host_lines?.opening_short} />
                  <InfoCard
                    title="Подводка к первому танцу"
                    value={program.host_lines?.intro_first_dance}
                  />
                  <InfoCard
                    title="Подводка к семейному блоку"
                    value={program.host_lines?.intro_family_block}
                  />
                  <InfoCard
                    title="Подводка к сюрпризу"
                    value={program.host_lines?.intro_surprise_block}
                  />
                  <InfoCard title="Подводка к торту" value={program.host_lines?.intro_cake} />
                  <InfoCard title="Финальные слова" value={program.host_lines?.closing_lines} />
                </div>

                <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                  <div className="text-xs uppercase tracking-[0.18em] text-white/40">
                    интерактивы
                  </div>
                  <div className="mt-3 space-y-3">
                    {program.interactive_blocks && program.interactive_blocks.length > 0 ? (
                      program.interactive_blocks.map((block, index) => (
                        <div
                          key={`${block.title}-${index}`}
                          className="rounded-xl border border-white/10 bg-white/5 p-4"
                        >
                          <div className="text-sm font-semibold text-white">
                            {index + 1}. {block.title || "Интерактив"}
                          </div>
                          <div className="mt-2 text-sm text-white/75">
                            <span className="text-white/45">Цель:</span> {block.goal || "Не указана"}
                          </div>
                          <div className="mt-2 text-sm text-white/75">
                            <span className="text-white/45">Когда лучше:</span>{" "}
                            {block.best_moment || "Не указано"}
                          </div>
                          <div className="mt-2 text-sm text-white/75">
                            <span className="text-white/45">Как провести:</span>{" "}
                            {block.how_to_run || "Не указано"}
                          </div>
                          <div className="mt-2 text-sm leading-7 text-white/75">
                            <span className="text-white/45">Почему безопасно:</span>{" "}
                            {block.why_it_is_safe || "Не указано"}
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
                    банк мягкого юмора
                  </div>
                  <div className="mt-3 space-y-3">
                    {program.humor_bank && program.humor_bank.length > 0 ? (
                      program.humor_bank.map((item, index) => (
                        <div
                          key={`${item.line}-${index}`}
                          className="rounded-xl border border-white/10 bg-white/5 p-4"
                        >
                          <div className="text-sm text-white/85">{item.line || "Не указано"}</div>
                          <div className="mt-2 text-sm text-white/75">
                            <span className="text-white/45">Тон:</span> {item.tone || "Не указан"}
                          </div>
                          <div className="mt-2 text-sm text-white/75">
                            <span className="text-white/45">Где использовать:</span>{" "}
                            {item.where_to_use || "Не указано"}
                          </div>
                          <div className="mt-2 text-sm leading-7 text-white/75">
                            <span className="text-white/45">Примечание по безопасности:</span>{" "}
                            {item.safety_note || "Не указано"}
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
                    план Б
                  </div>
                  <div className="mt-3 space-y-3">
                    {program.plan_b && program.plan_b.length > 0 ? (
                      program.plan_b.map((item, index) => (
                        <div
                          key={`${item.situation}-${index}`}
                          className="rounded-xl border border-white/10 bg-white/5 p-4"
                        >
                          <div className="text-sm font-semibold text-white">
                            {index + 1}. {item.situation || "Ситуация"}
                          </div>
                          <div className="mt-2 text-sm leading-7 text-white/75">
                            <span className="text-white/45">Что делать:</span>{" "}
                            {item.response || "Не указано"}
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-sm text-white/60">Не сформировано</div>
                    )}
                  </div>
                </div>

                <div className="grid gap-4 md:grid-cols-3">
                  <InfoCard
                    title="Как вести этот вечер"
                    value={program.final_strategy?.how_to_lead_this_event}
                  />
                  <InfoCard
                    title="Чего избегать"
                    value={program.final_strategy?.what_to_avoid}
                  />
                  <InfoCard
                    title="Что сделает вечер сильным"
                    value={program.final_strategy?.what_will_make_this_event_strong}
                  />
                </div>

                <div className="space-y-4 rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                  <div className="text-xs uppercase tracking-[0.18em] text-white/40">
                    печатная версия
                  </div>

                  <InfoCard title="Название" value={program.print_version?.title} />
                  <InfoCard
                    title="Краткое резюме для печати"
                    value={program.print_version?.event_summary}
                  />

                  <div className="grid gap-4 lg:grid-cols-2">
                    <ListBlock title="Ключевые люди" items={program.print_version?.key_people} />
                    <ListBlock
                      title="Обязательные блоки"
                      items={program.print_version?.must_do_blocks}
                    />
                    <ListBlock title="Нельзя делать" items={program.print_version?.do_not_do} />
                    <ListBlock
                      title="Короткий таймлайн"
                      items={program.print_version?.short_timeline}
                    />
                  </div>

                  <ListBlock
                    title="Фокус ведущего"
                    items={program.print_version?.host_focus_points}
                  />
                </div>
              </section>
            ) : null}

            <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              <InfoCard title="Имя клиента" value={item.questionnaire.clientName} />
              <InfoCard title="Второй герой" value={item.questionnaire.secondName} />
              <InfoCard title="Телефон" value={item.questionnaire.phone} />
              <InfoCard title="Дата события" value={item.questionnaire.eventDate} />
              <InfoCard title="Город" value={item.questionnaire.city} />
              <InfoCard title="Площадка" value={item.questionnaire.venue} />
              <InfoCard title="Количество гостей" value={item.questionnaire.guestCount} />
              <InfoCard title="Возраст гостей" value={item.questionnaire.guestAge} />
              <InfoCard title="Состав гостей" value={item.questionnaire.guestComposition} />
            </section>
          </div>
        ) : null}
      </div>
    </main>
  );
}