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

type ProgramBlock = {
  title: string;
  goal: string;
  host_action: string;
  notes: string;
};

type ProgramData = {
  summary?: string;
  audience?: string;
  risks?: string[];
  opening?: string;
  program_blocks?: ProgramBlock[];
  jokes?: string[];
  interactives?: string[];
  recommendations?: string[];
  final_strategy?: string;
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

        const response = await fetch("http://127.0.0.1:8000/api/submissions");
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
        `http://127.0.0.1:8000/api/submissions/${submissionId}/generate-program`,
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
              Здесь отображается полная анкета клиента и внутренняя программа для ведущего.
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
                  программа для ведущего
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <InfoCard title="Краткое резюме" value={program.summary} />
                  <InfoCard title="Разбор аудитории" value={program.audience} />
                </div>

                <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                  <div className="text-xs uppercase tracking-[0.18em] text-white/40">
                    открытие вечера
                  </div>
                  <div className="mt-2 text-sm leading-7 text-white/80">
                    {program.opening?.trim() ? program.opening : "Не сформировано"}
                  </div>
                </div>

                <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                  <div className="text-xs uppercase tracking-[0.18em] text-white/40">
                    риски
                  </div>
                  <div className="mt-3 space-y-2">
                    {program.risks && program.risks.length > 0 ? (
                      program.risks.map((risk, index) => (
                        <div
                          key={`${risk}-${index}`}
                          className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white/80"
                        >
                          {index + 1}. {risk}
                        </div>
                      ))
                    ) : (
                      <div className="text-sm text-white/60">Не сформировано</div>
                    )}
                  </div>
                </div>

                <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                  <div className="text-xs uppercase tracking-[0.18em] text-white/40">
                    блоки программы
                  </div>
                  <div className="mt-3 space-y-3">
                    {program.program_blocks && program.program_blocks.length > 0 ? (
                      program.program_blocks.map((block, index) => (
                        <div
                          key={`${block.title}-${index}`}
                          className="rounded-xl border border-white/10 bg-white/5 p-4"
                        >
                          <div className="text-sm font-semibold text-white">
                            {index + 1}. {block.title || "Без названия"}
                          </div>
                          <div className="mt-2 text-sm text-white/75">
                            <span className="text-white/45">Цель:</span>{" "}
                            {block.goal || "Не указана"}
                          </div>
                          <div className="mt-2 text-sm text-white/75">
                            <span className="text-white/45">Действие ведущего:</span>{" "}
                            {block.host_action || "Не указано"}
                          </div>
                          <div className="mt-2 text-sm leading-7 text-white/75">
                            <span className="text-white/45">Нюансы:</span>{" "}
                            {block.notes || "Не указаны"}
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-sm text-white/60">Не сформировано</div>
                    )}
                  </div>
                </div>

                <div className="grid gap-4 lg:grid-cols-2">
                  <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                    <div className="text-xs uppercase tracking-[0.18em] text-white/40">
                      шутки и подводки
                    </div>
                    <div className="mt-3 space-y-2">
                      {program.jokes && program.jokes.length > 0 ? (
                        program.jokes.map((joke, index) => (
                          <div
                            key={`${joke}-${index}`}
                            className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white/80"
                          >
                            {index + 1}. {joke}
                          </div>
                        ))
                      ) : (
                        <div className="text-sm text-white/60">Не сформировано</div>
                      )}
                    </div>
                  </div>

                  <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                    <div className="text-xs uppercase tracking-[0.18em] text-white/40">
                      интерактивы
                    </div>
                    <div className="mt-3 space-y-2">
                      {program.interactives && program.interactives.length > 0 ? (
                        program.interactives.map((interactive, index) => (
                          <div
                            key={`${interactive}-${index}`}
                            className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white/80"
                          >
                            {index + 1}. {interactive}
                          </div>
                        ))
                      ) : (
                        <div className="text-sm text-white/60">Не сформировано</div>
                      )}
                    </div>
                  </div>
                </div>

                <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                  <div className="text-xs uppercase tracking-[0.18em] text-white/40">
                    рекомендации ведущему
                  </div>
                  <div className="mt-3 space-y-2">
                    {program.recommendations && program.recommendations.length > 0 ? (
                      program.recommendations.map((line, index) => (
                        <div
                          key={`${line}-${index}`}
                          className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white/80"
                        >
                          {index + 1}. {line}
                        </div>
                      ))
                    ) : (
                      <div className="text-sm text-white/60">Не сформировано</div>
                    )}
                  </div>
                </div>

                <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                  <div className="text-xs uppercase tracking-[0.18em] text-white/40">
                    финальная стратегия
                  </div>
                  <div className="mt-2 text-sm leading-7 text-white/80">
                    {program.final_strategy?.trim()
                      ? program.final_strategy
                      : "Не сформировано"}
                  </div>
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

            <section className="grid gap-4 md:grid-cols-2">
              <InfoCard title="Цель мероприятия" value={item.questionnaire.eventGoal} />
              <InfoCard title="Желаемая атмосфера" value={item.questionnaire.desiredAtmosphere} />
              <InfoCard title="Какое впечатление должно остаться" value={item.questionnaire.idealImpression} />
              <InfoCard title="Обязательные моменты" value={item.questionnaire.mustHaveMoments} />
              <InfoCard title="Чего не должно быть" value={item.questionnaire.forbiddenTopics} />
              <InfoCard title="Страхи и переживания" value={item.questionnaire.fears} />
            </section>

            <section className="grid gap-4 md:grid-cols-2">
              <InfoCard title="Главные герои" value={item.questionnaire.mainHeroes} />
              <InfoCard title="Черты характера" value={item.questionnaire.personalityTraits} />
              <InfoCard title="Ценности" value={item.questionnaire.values} />
              <InfoCard title="Важные истории" value={item.questionnaire.importantStories} />
              <InfoCard title="Внутренние шутки" value={item.questionnaire.internalJokes} />
              <InfoCard title="Безопасные темы" value={item.questionnaire.safeTopics} />
              <InfoCard title="Табу-темы" value={item.questionnaire.tabooTopics} />
            </section>

            <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              <InfoCard title="Стиль ведущего" value={item.questionnaire.hostStyle} />
              <InfoCard title="Юмор" value={item.questionnaire.humorPreference} />
              <InfoCard title="Темп" value={item.questionnaire.tempoPreference} />
              <InfoCard title="Интерактивы" value={item.questionnaire.interactionPreference} />
              <InfoCard title="Трогательные моменты" value={item.questionnaire.touchingMoments} />
              <InfoCard title="Современность / классика" value={item.questionnaire.modernVsClassic} />
            </section>

            <section className="grid gap-4 md:grid-cols-2">
              <InfoCard title="Активные гости" value={item.questionnaire.activeGuests} />
              <InfoCard title="Скромные гости" value={item.questionnaire.shyGuests} />
              <InfoCard title="Важные гости" value={item.questionnaire.importantGuests} />
              <InfoCard title="Конфликтные риски" value={item.questionnaire.conflictRisks} />
              <InfoCard title="Дети" value={item.questionnaire.childrenPresence} />
              <InfoCard title="Кого не вовлекать" value={item.questionnaire.whoNotToInvolve} />
            </section>

            <section className="grid gap-4 md:grid-cols-2">
              <InfoCard title="Музыкальные предпочтения" value={item.questionnaire.musicPreferences} />
              <InfoCard title="Любимые артисты" value={item.questionnaire.favoriteArtists} />
              <InfoCard title="Запрещенная музыка" value={item.questionnaire.bannedMusic} />
              <InfoCard title="Танцевальный блок" value={item.questionnaire.danceBlockNeed} />
              <InfoCard title="Церемонии и официальные блоки" value={item.questionnaire.ceremonyNeed} />
              <InfoCard title="Сюрпризы" value={item.questionnaire.surpriseNeed} />
            </section>

            <section className="grid gap-4 md:grid-cols-2">
              <InfoCard title="Нежелательные конкурсы" value={item.questionnaire.contestsNo} />
              <InfoCard title="Чувствительные темы" value={item.questionnaire.sensitiveTopics} />
              <InfoCard title="Культурные ограничения" value={item.questionnaire.culturalLimits} />
              <InfoCard title="Логистические ограничения" value={item.questionnaire.logisticsLimits} />
              <InfoCard title="Замечания по таймингу" value={item.questionnaire.timingNotes} />
              <InfoCard title="Жесткое нет" value={item.questionnaire.hardNo} />
            </section>

            <section className="grid gap-4 md:grid-cols-2">
              <InfoCard title="Финальные пожелания" value={item.questionnaire.finalWishes} />
              <InfoCard title="Дополнительные детали" value={item.questionnaire.additionalDetails} />
              <InfoCard title="Референсы и ориентиры" value={item.questionnaire.references} />
            </section>
          </div>
        ) : null}
      </div>
    </main>
  );
}