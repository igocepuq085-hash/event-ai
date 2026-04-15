"use client";

import { useEffect, useState, useTransition } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { fetchApi, type Submission } from "@/lib/api";
import { AppShell } from "@/components/shell";

type GenerationState = {
  status: string;
  stage?: string;
  percent?: number;
  message?: string;
  error?: string;
  job_id?: string;
  updated_at?: string;
};

type GenerationResponse = {
  generation: GenerationState;
  hasProgram?: boolean;
  program?: Record<string, unknown>;
};

function getStageLabel(stage?: string) {
  switch (stage) {
    case "dossier":
      return "Creative dossier";
    case "writer":
      return "Main writer";
    case "polish":
      return "Polish";
    case "final_assembly":
      return "Финальная сборка";
    case "queued":
      return "Очередь";
    case "failed":
      return "Ошибка";
    default:
      return "Ожидание";
  }
}

export default function HostDetailPage() {
  const params = useParams<{ id: string }>();
  const [submission, setSubmission] = useState<Submission | null>(null);
  const [program, setProgram] = useState<Record<string, unknown> | null>(null);
  const [hasProgram, setHasProgram] = useState(false);
  const [generation, setGeneration] = useState<GenerationState>({ status: "idle" });
  const [error, setError] = useState("");
  const [isDownloading, setIsDownloading] = useState(false);
  const [isPending, startTransition] = useTransition();
  const id = params.id;

  useEffect(() => {
    if (!id) return;
    Promise.all([
      fetchApi<{ item: Submission }>(`/api/submissions/${id}`),
      fetchApi<GenerationResponse>(`/api/submissions/${id}/generation-status`),
    ])
      .then(([data, statusData]) => {
        setSubmission(data.item);
        setGeneration(statusData.generation || data.item.generation || { status: "idle" });
        setHasProgram(Boolean(statusData.hasProgram || data.item.program));
        if (data.item.program) {
          setProgram(data.item.program);
        }
      })
      .catch((loadError) => {
        setError(loadError instanceof Error ? loadError.message : "Не удалось загрузить заявку");
      });
  }, [id]);

  useEffect(() => {
    if (!id) return;
    if (!["queued", "running"].includes(generation.status)) return;

    const intervalId = window.setInterval(async () => {
      try {
        const statusData = await fetchApi<GenerationResponse>(`/api/submissions/${id}/generation-status`);
        setGeneration(statusData.generation);
        setHasProgram(Boolean(statusData.hasProgram));
        if (statusData.hasProgram || statusData.generation.status === "ready") {
          const data = await fetchApi<{ item: Submission }>(`/api/submissions/${id}`);
          setSubmission(data.item);
          setGeneration(data.item.generation || { status: "ready" });
          setHasProgram(Boolean(statusData.hasProgram || data.item.program));
          if (data.item.program) {
            setProgram(data.item.program);
          }
          window.clearInterval(intervalId);
        }
      } catch (pollError) {
        setError(pollError instanceof Error ? pollError.message : "Не удалось обновить статус генерации");
        window.clearInterval(intervalId);
      }
    }, 2500);

    return () => window.clearInterval(intervalId);
  }, [generation.status, id]);

  useEffect(() => {
    if (!id) return;
    if (generation.status !== "ready" || hasProgram) return;

    fetchApi<{ item: Submission }>(`/api/submissions/${id}`)
      .then((data) => {
        setSubmission(data.item);
        setHasProgram(Boolean(data.item.program));
        if (data.item.program) {
          setProgram(data.item.program);
        }
      })
      .catch(() => {});
  }, [generation.status, hasProgram, id]);

  const handleGenerate = () => {
    if (!id) return;
    setError("");
    startTransition(async () => {
      try {
        const data = await fetchApi<GenerationResponse>(`/api/submissions/${id}/generate-program/start`, { method: "POST" });
        setGeneration(data.generation);
        setHasProgram(Boolean(data.hasProgram));
        if (data.program) {
          setProgram(data.program);
        }
      } catch (generateError) {
        setError(generateError instanceof Error ? generateError.message : "Ошибка генерации");
      }
    });
  };

  const handleDownload = async () => {
    if (!id || !hasProgram || isDownloading) return;
    setError("");
    setIsDownloading(true);

    try {
      const response = await fetch(`/api/backend/api/submissions/${id}/export-docx`, {
        method: "GET",
        cache: "no-store",
      });

      if (!response.ok) {
        const contentType = response.headers.get("content-type") || "";
        let message = `Ошибка скачивания: ${response.status}`;

        if (contentType.includes("application/json")) {
          const data = (await response.json()) as { detail?: string };
          message = data.detail || message;
        } else {
          const text = await response.text();
          if (text) {
            message = text;
          }
        }

        throw new Error(message);
      }

      const blob = await response.blob();
      const contentDisposition = response.headers.get("content-disposition") || "";
      const filenameMatch = contentDisposition.match(/filename=\"([^\"]+)\"/i);
      const filename = filenameMatch?.[1] || `event_ai_${id}.docx`;
      const objectUrl = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = objectUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(objectUrl);
    } catch (downloadError) {
      setError(downloadError instanceof Error ? downloadError.message : "Не удалось скачать .docx");
    } finally {
      setIsDownloading(false);
    }
  };

  const isGenerating = isPending || ["queued", "running"].includes(generation.status);
  const canDownload = generation.status === "ready" && hasProgram && Boolean(program);
  const passport = (program?.event_passport as Record<string, unknown> | undefined) || null;
  const timeline = (program?.scenario_timeline as Record<string, unknown>[] | undefined) || [];
  const hostCommands = (program?.key_host_commands as string[] | undefined) || [];
  const questionnaire = submission?.questionnaire || {};

  return (
    <AppShell>
      <main className="mx-auto flex w-full max-w-7xl flex-col gap-8 px-6 pb-16 pt-8">
        <div className="flex items-center justify-between gap-4">
          <Link href="/host" className="text-sm font-medium text-stone-700">
            ← Назад к списку
          </Link>
          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              onClick={handleGenerate}
              disabled={isGenerating || !id}
              className="rounded-full bg-[var(--accent)] px-5 py-3 text-sm font-semibold text-white disabled:opacity-70"
            >
              {isGenerating ? "Генерация в работе..." : "Сформировать программу"}
            </button>
            <button
              type="button"
              onClick={handleDownload}
              disabled={!canDownload || isDownloading}
              className={`rounded-full border border-[var(--border)] bg-white/70 px-5 py-3 text-sm font-semibold text-stone-800 ${canDownload ? "" : "pointer-events-none opacity-50"}`}
            >
              Скачать .docx
            </button>
          </div>
        </div>

        {error ? <div className="rounded-[24px] border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">{error}</div> : null}
        {generation.status === "ready" && !hasProgram ? (
          <div className="rounded-[24px] border border-amber-200 bg-amber-50 px-5 py-4 text-sm text-amber-800">
            Генерация дошла до финала, но итоговая программа не прошла проверку. Нажмите `Сформировать программу` еще раз.
          </div>
        ) : null}
        {generation.status !== "idle" ? (
          <div className="rounded-[24px] border border-[var(--border)] bg-white/80 px-5 py-4 text-sm text-stone-700">
            <div className="flex items-center justify-between gap-4 font-medium text-stone-900">
              <span>Статус генерации: {getStageLabel(generation.stage || generation.status)}</span>
              <span>{generation.percent ?? 0}%</span>
            </div>
            <div className="mt-3 h-2 overflow-hidden rounded-full bg-stone-200">
              <div
                className="h-full rounded-full bg-[var(--accent)] transition-all duration-500"
                style={{ width: `${generation.percent ?? 0}%` }}
              />
            </div>
            <div className="mt-1">{generation.error || generation.message || "Генерация запущена."}</div>
          </div>
        ) : null}

        <section className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
          <div className="rounded-[32px] border border-[var(--border)] bg-white/75 p-6">
            <div className="text-xs uppercase tracking-[0.28em] text-stone-500">Заявка</div>
            <h1 className="mt-3 text-3xl font-semibold text-stone-900">{questionnaire.clientName || "Загрузка..."}</h1>
            <div className="mt-6 grid gap-3 text-sm text-stone-600">
              {Object.entries(questionnaire).map(([key, value]) => {
                if (!value) return null;
                return (
                  <div key={key} className="rounded-[20px] border border-[var(--border)] bg-[var(--surface)] px-4 py-3">
                    <div className="text-xs uppercase tracking-[0.18em] text-stone-500">{key}</div>
                    <div className="mt-1 whitespace-pre-wrap text-sm text-stone-800">{String(value)}</div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="flex flex-col gap-6">
            <div className="rounded-[32px] border border-[var(--border)] bg-white/75 p-6">
              <div className="text-xs uppercase tracking-[0.28em] text-stone-500">Паспорт события</div>
              {passport ? (
                <div className="mt-4 grid gap-3 text-sm text-stone-700 md:grid-cols-2">
                  {Object.entries(passport).map(([key, value]) => (
                    <div key={key} className="rounded-[20px] border border-[var(--border)] bg-[var(--surface)] px-4 py-3">
                      <div className="text-xs uppercase tracking-[0.18em] text-stone-500">{key}</div>
                      <div className="mt-1 whitespace-pre-wrap">{Array.isArray(value) ? value.join(", ") : String(value)}</div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="mt-4 text-sm text-stone-600">Программа еще не сформирована.</p>
              )}
            </div>

            <div className="rounded-[32px] border border-[var(--border)] bg-white/75 p-6">
              <div className="text-xs uppercase tracking-[0.28em] text-stone-500">Команды ведущему</div>
              <div className="mt-4 grid gap-3">
                {hostCommands.length ? (
                  hostCommands.map((item) => (
                    <div key={item} className="rounded-[18px] border border-[var(--border)] bg-[var(--surface)] px-4 py-3 text-sm text-stone-700">
                      {item}
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-stone-600">После генерации здесь появятся ключевые команды ведущему.</p>
                )}
              </div>
            </div>

            <div className="rounded-[32px] border border-[var(--border)] bg-white/75 p-6">
              <div className="text-xs uppercase tracking-[0.28em] text-stone-500">Тайминг</div>
              <div className="mt-4 grid gap-3">
                {timeline.length ? (
                  timeline.map((block, index) => (
                    <div key={`${String(block.block_title)}-${index}`} className="rounded-[20px] border border-[var(--border)] bg-[var(--surface)] p-4">
                      <div className="text-xs uppercase tracking-[0.18em] text-stone-500">
                        {String(block.time_from || "")} - {String(block.time_to || "")}
                      </div>
                      <div className="mt-2 text-lg font-semibold text-stone-900">{String(block.block_title || "")}</div>
                      <p className="mt-2 text-sm leading-7 text-stone-700">{String(block.what_happens || "")}</p>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-stone-600">После генерации здесь появится пошаговый тайминг.</p>
                )}
              </div>
            </div>
          </div>
        </section>
      </main>
    </AppShell>
  );
}
